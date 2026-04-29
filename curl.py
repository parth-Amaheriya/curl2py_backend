
DEFAULT_CURL_INPUT =[{"name":"search", "curl":"""curl 'https://blinkit.com/v1/layout/search?q=mil&search_type=type_to_search' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'access_token: null' \
  -H 'app_client: consumer_web' \
  -H 'app_version: 1010101010' \
  -H 'auth_key: c761ec3633c22afad934fb17a66385c1c06c5472b4898b866b7306186d0bb477' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b '_fbp=fb.1.1776421560488.734913384742893717; gr_1_deviceId=e0360658-a235-44dd-a8e5-bbd7ff854c6f; city=; __cf_bm=XgfCygCxmElezUAjxETjnJ5JUXzz3IvdzzNEP5gN6XQ-1777441950.130418-1.0.1.1-Gi7HSOV3Adr3msB5FMOq68AKC3p5rRHFAUMo8vW9C4BKsJk4Wg_thdrwoaZnd7BFRTergigRVbbWZBv1ksxJABLS1kR4lFOXqZVHgTUfvady9F1ZTTZR78DDrlVyaqmL; _cfuvid=ruu2UdvxetVCB1KW___RcBhLupDliWVxMC0vaA4T9yY-1777441950.130418-1.0.1.1-KaEkv2PltK94k7bde1QtVQWu9gW.jHcTICOpyuKxuTM; gr_1_lat=28.4890323; gr_1_lon=77.010109; gr_1_locality=1849; gr_1_landmark=undefined; _gid=GA1.2.687620840.1777441951; _gat_UA-85989319-1=1; _ga=GA1.2.810293142.1776421560; _gcl_au=1.2.1094485388.1776421560; _ga_DDJ0134H6Z=GS2.2.s1777441951$o5$g1$t1777441970$j41$l0$h0; _ga_JSMJG966C7=GS2.1.s1777441951$o5$g1$t1777441970$j41$l0$h0' \
  -H 'device_id: b6acf6d9a8ad0810' \
  -H 'lat: 28.4890323' \
  -H 'lon: 77.010109' \
  -H 'origin: https://blinkit.com' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://blinkit.com/s/?q=mil' \
  -H 'rn_bundle_version: 1009003012' \
  -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'session_uuid: 629c69c8-213e-49d4-8c26-68f84725374a' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  -H 'web_app_version: 1008010016' \
  --data-raw '{}'"""},
{"name":"auto_suggest", "curl":"""
curl 'https://blinkit.com/v1/actions/auto_suggest' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'access_token: null' \
  -H 'app_client: consumer_web' \
  -H 'app_version: 1010101010' \
  -H 'auth_key: c761ec3633c22afad934fb17a66385c1c06c5472b4898b866b7306186d0bb477' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b '_fbp=fb.1.1776421560488.734913384742893717; gr_1_deviceId=e0360658-a235-44dd-a8e5-bbd7ff854c6f; city=; __cf_bm=XgfCygCxmElezUAjxETjnJ5JUXzz3IvdzzNEP5gN6XQ-1777441950.130418-1.0.1.1-Gi7HSOV3Adr3msB5FMOq68AKC3p5rRHFAUMo8vW9C4BKsJk4Wg_thdrwoaZnd7BFRTergigRVbbWZBv1ksxJABLS1kR4lFOXqZVHgTUfvady9F1ZTTZR78DDrlVyaqmL; _cfuvid=ruu2UdvxetVCB1KW___RcBhLupDliWVxMC0vaA4T9yY-1777441950.130418-1.0.1.1-KaEkv2PltK94k7bde1QtVQWu9gW.jHcTICOpyuKxuTM; gr_1_lat=28.4890323; gr_1_lon=77.010109; gr_1_locality=1849; gr_1_landmark=undefined; _gid=GA1.2.687620840.1777441951; _gat_UA-85989319-1=1; _ga=GA1.2.810293142.1776421560; _gcl_au=1.2.1094485388.1776421560; _ga_DDJ0134H6Z=GS2.2.s1777441951$o5$g1$t1777441970$j41$l0$h0; _ga_JSMJG966C7=GS2.1.s1777441951$o5$g1$t1777441970$j41$l0$h0' \
  -H 'device_id: b6acf6d9a8ad0810' \
  -H 'lat: 28.4890323' \
  -H 'lon: 77.010109' \
  -H 'origin: https://blinkit.com' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://blinkit.com/s/?q=mil' \
  -H 'rn_bundle_version: 1009003012' \
  -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'session_uuid: 629c69c8-213e-49d4-8c26-68f84725374a' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  -H 'web_app_version: 1008010016' \
  --data-raw '{"q":"mil","search_type":"type_to_search"}'"""},
{"name":"search2", "curl":"""
  curl 'https://blinkit.com/v1/layout/search?offset=12&limit=12&actual_query=mil&last_snippet_type=product_card_snippet_type_2&last_widget_type=listing_container&page_index=1&q=mil&search_count=161&search_method=basic&search_type=type_to_search&total_entities_processed=1&total_pagination_items=161' \
  -X 'POST' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'access_token: null' \
  -H 'app_client: consumer_web' \
  -H 'app_version: 1010101010' \
  -H 'auth_key: c761ec3633c22afad934fb17a66385c1c06c5472b4898b866b7306186d0bb477' \
  -H 'cache-control: no-cache' \
  -H 'content-length: 0' \
  -H 'content-type: application/json' \
  -b '_fbp=fb.1.1776421560488.734913384742893717; gr_1_deviceId=e0360658-a235-44dd-a8e5-bbd7ff854c6f; city=; __cf_bm=XgfCygCxmElezUAjxETjnJ5JUXzz3IvdzzNEP5gN6XQ-1777441950.130418-1.0.1.1-Gi7HSOV3Adr3msB5FMOq68AKC3p5rRHFAUMo8vW9C4BKsJk4Wg_thdrwoaZnd7BFRTergigRVbbWZBv1ksxJABLS1kR4lFOXqZVHgTUfvady9F1ZTTZR78DDrlVyaqmL; _cfuvid=ruu2UdvxetVCB1KW___RcBhLupDliWVxMC0vaA4T9yY-1777441950.130418-1.0.1.1-KaEkv2PltK94k7bde1QtVQWu9gW.jHcTICOpyuKxuTM; gr_1_lat=28.4890323; gr_1_lon=77.010109; gr_1_locality=1849; gr_1_landmark=undefined; _gid=GA1.2.687620840.1777441951; _gat_UA-85989319-1=1; _ga=GA1.2.810293142.1776421560; _gcl_au=1.2.1094485388.1776421560; _ga_DDJ0134H6Z=GS2.2.s1777441951$o5$g1$t1777441970$j41$l0$h0; _ga_JSMJG966C7=GS2.1.s1777441951$o5$g1$t1777441970$j41$l0$h0' \
  -H 'device_id: b6acf6d9a8ad0810' \
  -H 'lat: 28.4890323' \
  -H 'lon: 77.010109' \
  -H 'origin: https://blinkit.com' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://blinkit.com/s/?q=mil' \
  -H 'rn_bundle_version: 1009003012' \
  -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'session_uuid: 629c69c8-213e-49d4-8c26-68f84725374a' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  -H 'web_app_version: 1008010016'"""
}]



