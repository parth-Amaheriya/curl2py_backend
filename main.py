import re
import shlex
import json
from urllib.parse import parse_qsl, urlparse
import os
from curl import DEFAULT_CURL_INPUT

# Regex for {{place}}, ${place}, <place>
PLACEHOLDER_PATTERN = re.compile(
    r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}|"
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|"
    r"<([A-Za-z_][A-Za-z0-9_]*)>"
)

def curl_to_requests(curl_command):
    tokens = shlex.split(curl_command)
    method = "GET"
    url = ""
    params = {}
    headers = {}
    data = None
    explicit_method = False

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "curl":
            i += 1
            continue

        if token in (
            "--location", "-L",
            "--compressed", "-s", "--silent",
            "--show-error", "--fail", "--fail-with-body"
        ):
            i += 1
            continue

        if token in ("--request", "-X") and i + 1 < len(tokens):
            method = tokens[i + 1].upper()
            explicit_method = True
            i += 2
            continue

        if token in ("--header", "-H") and i + 1 < len(tokens):
            header = tokens[i + 1]
            if ":" in header:
                key, value = header.split(":", 1)
                headers[key.strip()] = value.strip()
            i += 2
            continue

        if token in ("--cookie", "-b") and i + 1 < len(tokens):
            cookie_value = tokens[i + 1]
            if "Cookie" in headers and headers["Cookie"]:
                headers["Cookie"] += "; " + cookie_value
            else:
                headers["Cookie"] = cookie_value
            i += 2
            continue

        if token in ("--user-agent", "-A") and i + 1 < len(tokens):
            headers["User-Agent"] = tokens[i + 1]
            i += 2
            continue

        if token in (
            "--data", "--data-raw", "--data-binary",
            "--data-ascii", "--data-urlencode", "-d"
        ) and i + 1 < len(tokens):
            data = tokens[i + 1]
            if not explicit_method:
                method = "POST"
            i += 2
            continue

        if token in ("--get", "-G"):
            method = "GET"
            explicit_method = True
            i += 1
            continue

        if token.startswith("http://") or token.startswith("https://"):
            parsed_url = urlparse(token)
            url = parsed_url._replace(query="", fragment="").geturl()
            params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
            i += 1
            continue

        i += 1

    return {
        "method": method,
        "url": url,
        "params": params,
        "headers": headers,
        "data": data,
    }

def find_placeholders(text):
    if not text:
        return []
    found = []
    for match in PLACEHOLDER_PATTERN.finditer(text):
        name = next(group for group in match.groups() if group)
        if name not in found:
            found.append(name)
    return found

def sanitize_identifier(text):
    s = re.sub(r"[^a-zA-Z0-9_]+", "_", text.strip().lower())
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "value"
    if not re.match(r"[A-Za-z_]", s):
        s = f"param_{s}"
    return s

def render_template_expression(text):
    if text is None:
        return "None"
    pieces = []
    last = 0
    for match in PLACEHOLDER_PATTERN.finditer(text):
        literal = text[last:match.start()]
        if literal:
            pieces.append(repr(literal))
        name = next(group for group in match.groups() if group)
        pieces.append(f"(str({name}) if {name} is not None else '')")
        last = match.end()
    tail = text[last:]
    if tail:
        pieces.append(repr(tail))
    if not pieces:
        return "''"
    if len(pieces) == 1:
        return pieces[0]
    return " + ".join(pieces)

def build_request_arguments(spec):
    arguments = []
    used_names = set()
    query_entries = []
    payload_entries = []
    payload_mode = None
    payload_literal = None

    def add_optional(name, default):
        candidate = sanitize_identifier(name)
        if candidate in used_names:
            return candidate
        used_names.add(candidate)
        arguments.append({
            "name": candidate,
            "default": default,
            "required": False,
        })
        return candidate

    # Placeholders in URL
    for ph in find_placeholders(spec["url"]):
        add_optional(ph, None)

    # Placeholders in query params
    for key, value in spec["params"].items():
        phs = find_placeholders(value)
        if phs:
            for ph in phs:
                add_optional(ph, None)
            query_entries.append({
                "key": key,
                "expression": render_template_expression(value),
            })
        else:
            arg_name = add_optional(key, value)
            query_entries.append({
                "key": key,
                "expression": arg_name,
            })

    # Headers
    for val in spec["headers"].values():
        for ph in find_placeholders(val):
            add_optional(ph, None)

    # Body/payload
    if spec["data"]:
        body_text = spec["data"].strip()
        try:
            parsed_body = json.loads(body_text)
        except Exception:
            parsed_body = None

        if isinstance(parsed_body, dict):
            payload_mode = "json"
            for key, value in parsed_body.items():
                if isinstance(value, str):
                    phs = find_placeholders(value)
                    if phs:
                        for ph in phs:
                            add_optional(ph, None)
                        payload_entries.append({
                            "key": key,
                            "expression": render_template_expression(value),
                        })
                    else:
                        arg_name = add_optional(key, value)
                        payload_entries.append({
                            "key": key,
                            "expression": arg_name,
                        })
                else:
                    arg_name = add_optional(key, value)
                    payload_entries.append({
                        "key": key,
                        "expression": arg_name,
                    })
        else:
            payload_mode = "raw"
            payload_literal = render_template_expression(spec["data"])
            for ph in find_placeholders(spec["data"]):
                add_optional(ph, None)

    return arguments, query_entries, payload_entries, payload_mode, payload_literal

def render_request_function(spec):
    args = []
    for arg in spec["arguments"]:
        if arg["required"]:
            args.append(arg["name"])
        else:
            args.append(f"{arg['name']}={arg['default']!r}")
    signature = f"def {spec['name']}({', '.join(args)}):" if args else f"def {spec['name']}():"

    lines = [signature]
    lines.append(f"    url = {render_template_expression(spec['url'])}")

    # Query params
    if spec["query_entries"]:
        lines.append("    params = {")
        for e in spec["query_entries"]:
            lines.append(f"        {e['key']!r}: {e['expression']},")
        lines.append("    }")
    else:
        lines.append("    params = None")

    # Headers
    lines.append("    headers = {")
    for k, v in spec["headers"].items():
        lines.append(f"        {k!r}: {render_template_expression(v)},")
    lines.append("    }")

    # Payload
    if spec["payload_mode"] == "json":
        lines.append("    payload = {")
        for e in spec["payload_entries"]:
            lines.append(f"        {e['key']!r}: {e['expression']},")
        lines.append("    }")
    elif spec["payload_mode"] == "raw" and spec["payload_literal"] is not None:
        lines.append(f"    payload = {spec['payload_literal']}")
    else:
        lines.append(f"    payload = {render_template_expression(spec['data'])}")

    request_keyword = "json" if spec["payload_mode"] == "json" else "data"

    lines.append("")
    lines.append(f"    response = requests.request(method={spec['method']!r}, url=url, params=params, headers=headers, {request_keyword}=payload, impersonate='chrome')")
    lines.append(f"    response.raise_for_status()")
    lines.append(f"    print(response)")
    lines.append(f"    return {spec['name']}_parser(response)")
    return "\n".join(lines)

def render_main_function(request_specs):
    lines = ["def do_requests():\n"]
    for idx, spec in enumerate(request_specs):
        lines.append(f"    response_{idx+1} = {spec['name']}()")
    return "\n".join(lines)
def build_request_specs_list(raw_input_list):
    """Handles empty or duplicate names by autogenerating unique function names."""
    specs = []
    used_names = set()
    for entry in raw_input_list:
        curl_command = entry['curl']
        supplied_name = entry.get('name', '').strip()
        spec = curl_to_requests(curl_command)

        # If name is missing/empty, generate one from url path
        if supplied_name:
            sanitized_fn = sanitize_identifier(supplied_name)
        else:
            # build name from url path (e.g., get_layout_search_post)
            method = spec.get('method', 'get')
            path = urlparse(spec.get('url', '')).path.strip("/").replace("/", "_")
            sanitized_fn = sanitize_identifier(f"{method.lower()}_{path}" if path else method.lower())

        # Ensure uniqueness
        original_fn = sanitized_fn
        suffix = 2
        while sanitized_fn in used_names or not sanitized_fn:
            sanitized_fn = f"{original_fn}_{suffix}"
            suffix += 1
        used_names.add(sanitized_fn)

        spec["name"] = sanitized_fn
        args, queries, payloads, pmode, plit = build_request_arguments(spec)
        spec.update({
            "arguments": args,
            "query_entries": queries,
            "payload_entries": payloads,
            "payload_mode": pmode,
            "payload_literal": plit,
        })
        specs.append(spec)
    return specs

def build_python_script(raw_input_list):
    specs = build_request_specs_list(raw_input_list)
    code = [
        "from curl_cffi import requests",
        "from parser import *",
        ""
    ]
    for spec in specs:
        code.append(render_request_function(spec))
        code.append("")
    code.append(render_main_function(specs))
    code.append("")
    code.append("if __name__ == '__main__':")
    code.append("    do_requests()")
    code.append("")
    return "\n".join(code), [spec['name'] for spec in specs]

def build_parser_py(function_names):
    code = []
    for fn in function_names:
        code.append(f"def {fn}_parser(response):")
        code.append(f"    pass\n")
    return "\n".join(code)

def main():
    raw_input_list = DEFAULT_CURL_INPUT
    script_code, function_names = build_python_script(raw_input_list)
    parser_code = build_parser_py(function_names)
    os.makedirs("generated_code", exist_ok=True)
    with open("generated_code/request_script.py", "w", encoding="utf-8") as f:
        f.write(script_code)
    with open("generated_code/parser.py", "w", encoding="utf-8") as f:
        f.write(parser_code)

if __name__ == "__main__":
    main()