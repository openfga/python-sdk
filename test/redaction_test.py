import json

import pytest

from openfga_sdk.redaction import redact_response_body


def test_redact_response_body_redacts_token_fields():
    body = b'{"access_token":"a","refresh_token":"r","id_token":"i","expires_in":3600}'

    assert json.loads(redact_response_body(body)) == {
        "access_token": "[REDACTED]",
        "refresh_token": "[REDACTED]",
        "id_token": "[REDACTED]",
        "expires_in": 3600,
    }


@pytest.mark.parametrize(
    "body",
    [
        b'{"allowed":true}',
        b"[1, 2]",
        b"not json",
        b"",
    ],
)
def test_redact_response_body_leaves_other_bodies_unchanged(body):
    assert redact_response_body(body) == body.decode("utf-8")
