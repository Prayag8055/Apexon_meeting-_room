import json
import decimal

def json_default(obj):
    if isinstance(obj, decimal.Decimal):
        return int(obj) if obj == int(obj) else float(obj)
    return str(obj)

def response(code: int, body: dict) -> dict:
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body, default=json_default)
    }

def normalize_path(raw_path: str, event: dict) -> str:
    if not raw_path:
        return "/"
    stage = (
        event.get("requestContext", {}).get("stage")
        or event.get("requestContext", {}).get("http", {}).get("stage")
    )
    if stage and raw_path.startswith(f"/{stage}/"):
        raw_path = raw_path[len(stage) + 2:]
        if not raw_path.startswith("/"):
            raw_path = "/" + raw_path
    if stage and raw_path == f"/{stage}":
        raw_path = "/"
    if len(raw_path) > 1 and raw_path.endswith("/"):
        raw_path = raw_path[:-1]
    return raw_path

def parse_event(event: dict) -> dict:
    import base64
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "GET")
    raw_path = event.get("path") or event.get("rawPath") or "/"
    path = normalize_path(raw_path, event)
    qs = event.get("queryStringParameters") or {}
    body_raw = event.get("body")
    if event.get("isBase64Encoded"):
        try:
            body_raw = base64.b64decode(body_raw or "").decode("utf-8")
        except Exception:
            pass
    try:
        body = json.loads(body_raw) if body_raw else {}
    except json.JSONDecodeError:
        body = {}
    return {"method": method, "path": path, "qs": qs, "body": body}
