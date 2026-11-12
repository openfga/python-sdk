import json


_SENSITIVE_RESPONSE_FIELDS = ("access_token", "refresh_token", "id_token")


def redact_response_body(data):
    """
    Decode a response body for logging. If it is a JSON object containing
    token fields, such as an OAuth2 token response, their values are replaced
    with "[REDACTED]".
    """
    text = data.decode("utf-8")
    try:
        parsed = json.loads(text)
    except ValueError:
        return text
    if not isinstance(parsed, dict):
        return text

    sensitive_fields = [f for f in _SENSITIVE_RESPONSE_FIELDS if f in parsed]
    if not sensitive_fields:
        return text
    for field in sensitive_fields:
        parsed[field] = "[REDACTED]"
    return json.dumps(parsed)
