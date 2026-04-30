from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from curl import DEFAULT_CURL_INPUT


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

PLACEHOLDER_PATTERN = re.compile(
    r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}|"
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|"
    r"<([A-Za-z_][A-Za-z0-9_]*)>"
)


class ConvertPayload(BaseModel):
    curl_text: str = Field(default="", description="One or more curl commands")


def build_default_raw_text() -> str:
    return "\n\n".join(entry["curl"].strip() for entry in DEFAULT_CURL_INPUT)


def normalize_block(block: str) -> str:
    lines = [line.rstrip() for line in block.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def split_curl_blocks(raw_text: str) -> list[str]:
    if not raw_text:
        return []

    stripped = raw_text.strip()
    if not stripped:
        return []

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, list):
        blocks = []
        for item in parsed:
            if isinstance(item, dict):
                curl_command = item.get("curl")
                if isinstance(curl_command, str) and curl_command.strip():
                    blocks.append(normalize_block(curl_command))
        if blocks:
            return blocks

    blocks = []
    current_lines: list[str] = []

    for raw_line in raw_text.splitlines():
        line = raw_line.rstrip()
        starts_new_command = re.match(r"^\s*(?:\$\s*)?curl\b", line) is not None

        if starts_new_command and current_lines:
            block = normalize_block("\n".join(current_lines))
            if block:
                blocks.append(block)
            current_lines = []

        if line.strip() or current_lines:
            current_lines.append(line)

    if current_lines:
        block = normalize_block("\n".join(current_lines))
        if block:
            blocks.append(block)

    return blocks


def curl_to_spec(curl_command: str) -> dict[str, Any]:
    tokens = shlex.split(curl_command)
    method = "GET"
    url = ""
    params: dict[str, str] = {}
    headers: dict[str, str] = {}
    data: str | None = None
    explicit_method = False

    index = 0
    while index < len(tokens):
        token = tokens[index]

        if token == "curl":
            index += 1
            continue

        if token in (
            "--location",
            "-L",
            "--compressed",
            "-s",
            "--silent",
            "--show-error",
            "--fail",
            "--fail-with-body",
        ):
            index += 1
            continue

        if token in ("--request", "-X") and index + 1 < len(tokens):
            method = tokens[index + 1].upper()
            explicit_method = True
            index += 2
            continue

        if token in ("--header", "-H") and index + 1 < len(tokens):
            header = tokens[index + 1]
            if ":" in header:
                key, value = header.split(":", 1)
                headers[key.strip()] = value.strip()
            index += 2
            continue

        if token in ("--cookie", "-b") and index + 1 < len(tokens):
            cookie_value = tokens[index + 1]
            if "Cookie" in headers and headers["Cookie"]:
                headers["Cookie"] += "; " + cookie_value
            else:
                headers["Cookie"] = cookie_value
            index += 2
            continue

        if token in ("--user-agent", "-A") and index + 1 < len(tokens):
            headers["User-Agent"] = tokens[index + 1]
            index += 2
            continue

        if token in (
            "--data",
            "--data-raw",
            "--data-binary",
            "--data-ascii",
            "--data-urlencode",
            "-d",
        ) and index + 1 < len(tokens):
            data = tokens[index + 1]
            if not explicit_method:
                method = "POST"
            index += 2
            continue

        if token in ("--get", "-G"):
            method = "GET"
            explicit_method = True
            index += 1
            continue

        if token.startswith("http://") or token.startswith("https://"):
            parsed_url = urlparse(token)
            url = parsed_url._replace(query="", fragment="").geturl()
            params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
            index += 1
            continue

        index += 1

    if not url:
        raise ValueError("No URL found in curl command")

    return {
        "method": method,
        "url": url,
        "params": params,
        "headers": headers,
        "data": data,
    }


def find_placeholders(text: str | None) -> list[str]:
    if not text:
        return []

    found: list[str] = []
    for match in PLACEHOLDER_PATTERN.finditer(text):
        name = next(group for group in match.groups() if group)
        if name not in found:
            found.append(name)
    return found


def render_template_expression(text: str | None) -> str:
    if text is None:
        return "None"

    if not find_placeholders(text):
        return repr(text)

    pieces: list[str] = []
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

    if len(pieces) == 1:
        return pieces[0]
    return " + ".join(pieces)


def render_value_expression(value: Any) -> str:
    if isinstance(value, str):
        return render_template_expression(value)
    return repr(value)


def parse_json_body(data: str | None) -> dict[str, Any] | None:
    if not data:
        return None

    try:
        parsed_body = json.loads(data.strip())
    except Exception:
        return None

    return parsed_body if isinstance(parsed_body, dict) else None


def determine_body_type(spec: dict[str, Any]) -> str:
    parsed_body = parse_json_body(spec.get("data"))
    if parsed_body is not None:
        return "JSON"
    if spec.get("data"):
        return "RAW"
    return "NONE"


def collect_placeholders(spec: dict[str, Any]) -> list[str]:
    names: list[str] = []
    values = [spec.get("url"), *spec.get("params", {}).values(), *spec.get("headers", {}).values(), spec.get("data")]
    for value in values:
        for name in find_placeholders(value):
            if name not in names:
                names.append(name)
    return names


def render_python_script(spec: dict[str, Any]) -> str:
    body_type = determine_body_type(spec)
    parsed_body = parse_json_body(spec.get("data"))
    placeholders = collect_placeholders(spec)

    lines: list[str] = ["import requests"]
    if body_type == "JSON":
        lines.append("import json")

    lines.append("")

    if placeholders:
        for name in placeholders:
            lines.append(f"{name} = None")
        lines.append("")

    lines.append(f"url = {render_template_expression(spec['url'])}")

    params = spec.get("params") or {}
    if params:
        lines.append("params = {")
        for key, value in params.items():
            lines.append(f"    {key!r}: {render_value_expression(value)},")
        lines.append("}")

    headers = spec.get("headers") or {}
    if headers:
        lines.append("headers = {")
        for key, value in headers.items():
            lines.append(f"    {key!r}: {render_value_expression(value)},")
        lines.append("}")

    if body_type == "JSON" and parsed_body is not None:
        lines.append("payload = json.dumps({")
        for key, value in parsed_body.items():
            lines.append(f"    {key!r}: {render_value_expression(value)},")
        lines.append("})")
    elif body_type == "RAW" and spec.get("data") is not None:
        lines.append(f"payload = {render_template_expression(spec['data'])}")

    lines.append("")

    request_kwargs = [f"method={spec['method']!r}", "url=url"]
    if params:
        request_kwargs.append("params=params")
    if headers:
        request_kwargs.append("headers=headers")
    if body_type != "NONE":
        request_kwargs.append("data=payload")

    lines.append(f"response = requests.request({', '.join(request_kwargs)})")
    lines.append("print(response.text)")
    return "\n".join(lines)


def build_request_preview(curl_command: str, index: int) -> dict[str, Any]:
    spec = curl_to_spec(curl_command)
    parsed_url = urlparse(spec["url"])
    host = parsed_url.netloc or parsed_url.path or "unknown"
    body_type = determine_body_type(spec)
    filename = f"req_{index}.py"

    return {
        "id": index,
        "title": f"Request {index}",
        "filename": filename,
        "method": spec["method"],
        "host": host,
        "bodyType": body_type,
        "summary": f"{spec['method']} | {host} | {body_type}",
        "curl": curl_command,
        "code": render_python_script(spec),
    }


def convert_raw_text(raw_text: str) -> dict[str, Any]:
    blocks = split_curl_blocks(raw_text)
    requests = []

    for index, block in enumerate(blocks, start=1):
        try:
            requests.append(build_request_preview(block, index))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Request {index}: {exc}") from exc

    return {
        "raw_text": raw_text,
        "count": len(requests),
        "requests": requests,
    }


DEFAULT_RAW_TEXT = build_default_raw_text()
DEFAULT_RESPONSE = convert_raw_text(DEFAULT_RAW_TEXT)


app = FastAPI(title="Curl Transpiller")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/default-input")
def get_default_input() -> dict[str, Any]:
    return DEFAULT_RESPONSE


@app.post("/api/convert")
def convert_curl(payload: ConvertPayload) -> dict[str, Any]:
    return convert_raw_text(payload.curl_text)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
