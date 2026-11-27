import asyncio
import json

from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

import aiohttp
import urllib3

from openfga_sdk import rest
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.client import OpenFgaClient
from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.client.models.batch_check_request import ClientBatchCheckRequest
from openfga_sdk.client.models.batch_check_response import ClientBatchCheckResponse
from openfga_sdk.configuration import RetryParams
from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.exceptions import (
    AuthenticationError,
    FgaValidationException,
    ForbiddenException,
    NotFoundException,
    RateLimitExceededError,
    ServiceException,
    UnauthorizedException,
    ValidationException,
)
from openfga_sdk.models.consistency_preference import ConsistencyPreference
from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.metrics import TelemetryMetrics


STORE_ID = "01YCP46JKYM8FJCQ37NMBYHE5X"
MODEL_ID = "01GXSA8YR785C4FYS3C0RTG7B1"
OTHER_MODEL_ID = "01HVMMBCMGZNT3SED4Z17ECXCA"
API_URL = "http://api.fga.example"
MODELS_URL = f"{API_URL}/stores/{STORE_ID}/authorization-models/"
BATCH_CHECK_URL = f"{API_URL}/stores/{STORE_ID}/batch-check"
TOKEN_URL = "https://issuer.fga.example/oauth/token"

# define viewer: [user], can_view: viewer, can_share: can_view, editor: [user]
MODEL = {
    "id": MODEL_ID,
    "schema_version": "1.1",
    "type_definitions": [
        {"type": "user"},
        {
            "type": "document",
            "relations": {
                "viewer": {"this": {}},
                "can_view": {"computedUserset": {"relation": "viewer"}},
                "can_share": {"computedUserset": {"relation": "can_view"}},
                "editor": {"this": {}},
            },
            "metadata": {
                "relations": {
                    "viewer": {"directly_related_user_types": [{"type": "user"}]},
                    "can_view": {"directly_related_user_types": []},
                    "can_share": {"directly_related_user_types": []},
                    "editor": {"directly_related_user_types": [{"type": "user"}]},
                }
            },
        },
    ],
}


def http_mock_response(body, status):
    headers = urllib3.response.HTTPHeaderDict({"content-type": "application/json"})
    return urllib3.HTTPResponse(
        body.encode("utf-8"), headers, status, preload_content=False
    )


def mock_response(body, status=200):
    obj = http_mock_response(body, status)
    return rest.RESTResponse(obj, obj.data)


def token_issued():
    return mock_response(json.dumps({"access_token": "token", "expires_in": 3600}))


def short_lived_token_issued():
    # Expires within the SDK's renewal buffer, so every request gets a new token
    return mock_response(json.dumps({"access_token": "token", "expires_in": 300}))


def short_lived_tokens_then_rate_limited(count):
    responses = iter([short_lived_token_issued] * count)
    return lambda: next(responses, rate_limited)()


def no_token_issued():
    return mock_response("{}")


def token_configuration():
    """
    A configuration that gets a token from TOKEN_URL, and retries a failed token
    request once.
    """
    return ClientConfiguration(
        api_url=API_URL,
        store_id=STORE_ID,
        authorization_model_id=MODEL_ID,
        credentials=Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="client-id",
                client_secret="client-secret",
                api_issuer=TOKEN_URL,
                api_audience="audience",
            ),
        ),
        retry_params=RetryParams(max_retry=1),
    )


def checks():
    return [
        ClientBatchCheckItem(
            user="user:anne", relation="viewer", object="document:1", correlation_id="a"
        ),
        ClientBatchCheckItem(
            user="user:anne",
            relation="can_view",
            object="document:1",
            correlation_id="b",
        ),
        ClientBatchCheckItem(
            user="user:anne",
            relation="can_share",
            object="document:1",
            correlation_id="c",
        ),
        ClientBatchCheckItem(
            user="user:anne", relation="editor", object="document:1", correlation_id="d"
        ),
    ]


class FakeServer:
    """
    Answers token requests, model reads and BatchCheck requests, and records what was
    sent.
    """

    def __init__(
        self, model_error=None, answer=None, model_body=None, token=token_issued
    ):
        self.token = token
        self.token_requests = 0
        self.model_error = model_error
        self.model_body = (
            {"authorization_model": MODEL} if model_body is None else model_body
        )
        self.answer = answer or (
            lambda check: {"allowed": check["tuple_key"]["relation"] == "viewer"}
        )
        self.model_reads = 0
        self.model_ids_read = []
        self.model_read_headers = []
        self.sent = []

    def __call__(self, method, url, **kwargs):
        if method == "POST" and url == TOKEN_URL:
            self.token_requests += 1
            response = self.token()
            if isinstance(response, Exception):
                raise response
            return response

        if method == "GET" and url.startswith(MODELS_URL):
            self.model_reads += 1
            self.model_ids_read.append(url.removeprefix(MODELS_URL))
            self.model_read_headers.append(kwargs.get("headers") or {})
            if self.model_error is not None:
                raise self.model_error()
            return mock_response(json.dumps(self.model_body))

        if method == "POST" and url == BATCH_CHECK_URL:
            body = kwargs["body"]
            self.sent.append(body)
            return mock_response(
                json.dumps(
                    {
                        "result": {
                            check["correlation_id"]: self.answer(check)
                            for check in body["checks"]
                        }
                    }
                )
            )

        raise AssertionError(f"Unexpected request: {method} {url}")


def sent_checks(server):
    return [
        (
            check["correlation_id"],
            check["tuple_key"]["relation"],
        )
        for body in server.sent
        for check in body["checks"]
    ]


def forbidden():
    return ForbiddenException(http_resp=http_mock_response("{}", 403))


def unauthorized():
    return UnauthorizedException(http_resp=http_mock_response("{}", 401))


def rate_limited():
    return RateLimitExceededError(http_resp=http_mock_response("{}", 429))


def server_error():
    return ServiceException(http_resp=http_mock_response("{}", 500))


def timed_out():
    return TimeoutError("timed out")


def connection_dropped():
    return aiohttp.ClientConnectionError("connection reset")


def store_not_found():
    body = {"code": "store_id_not_found", "message": f"Store '{STORE_ID}' not found"}
    return NotFoundException(http_resp=http_mock_response(json.dumps(body), 404))


def bad_request():
    return ValidationException(http_resp=http_mock_response("{}", 400))


UNMERGED = [("a", "viewer"), ("b", "can_view"), ("c", "can_share"), ("d", "editor")]


def model_not_found():
    body = {
        "code": "authorization_model_not_found",
        "message": f"Authorization Model '{MODEL_ID}' not found",
    }
    return ValidationException(http_resp=http_mock_response(json.dumps(body), 400))


class TestBatchCheckMergeEquivalentChecks(IsolatedAsyncioTestCase):
    def setUp(self):
        self.configuration = ClientConfiguration(
            api_url=API_URL,
            store_id=STORE_ID,
            authorization_model_id=MODEL_ID,
        )

    async def batch_check(self, client, items, options=None):
        return await client.batch_check(
            ClientBatchCheckRequest(checks=items),
            options={"merge_equivalent_checks": True, **(options or {})},
        )

    @patch.object(rest.RESTClientObject, "request")
    async def test_merges_aliases_and_copies_the_answer_back(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server
        items = checks()

        async with OpenFgaClient(self.configuration) as client:
            response = await self.batch_check(client, items)

        self.assertEqual(server.model_reads, 1)
        self.assertEqual(sent_checks(server), [("merged-1", "viewer"), ("d", "editor")])
        self.assertEqual(server.sent[0]["authorization_model_id"], MODEL_ID)
        self.assertEqual(response.checks_sent, 2)
        self.assertEqual(
            [(r.correlation_id, r.allowed, r.error) for r in response.result],
            [
                ("a", True, None),
                ("b", True, None),
                ("c", True, None),
                ("d", False, None),
            ],
        )
        self.assertEqual([r.request for r in response.result], items)

    @patch.object(rest.RESTClientObject, "request")
    async def test_merges_checks_that_would_land_in_different_batches(
        self, mock_request
    ):
        server = FakeServer()
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            response = await self.batch_check(
                client, checks()[:3], options={"max_batch_size": 1}
            )

        self.assertEqual(sent_checks(server), [("merged-1", "viewer")])
        self.assertEqual(response.checks_sent, 1)
        self.assertEqual(len(response.result), 3)

    @patch.object(rest.RESTClientObject, "request")
    async def test_reads_the_model_once_for_parallel_and_later_calls(
        self, mock_request
    ):
        server = FakeServer()
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            await asyncio.gather(
                *[self.batch_check(client, checks()) for _ in range(5)]
            )
            await self.batch_check(client, checks())

        self.assertEqual(server.model_reads, 1)
        self.assertEqual(len(server.sent), 6)

    @patch.object(rest.RESTClientObject, "request")
    async def test_requires_a_model_id(self, mock_request):
        self.configuration.authorization_model_id = None

        async with OpenFgaClient(self.configuration) as client:
            with self.assertRaisesRegex(
                FgaValidationException, "authorization_model_id"
            ):
                await self.batch_check(client, checks())

        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    async def test_requires_a_store_id(self, mock_request):
        self.configuration.store_id = None

        async with OpenFgaClient(self.configuration) as client:
            with self.assertRaisesRegex(FgaValidationException, "store_id"):
                await self.batch_check(client, checks())

        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    async def test_the_model_id_in_the_options_wins(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            await self.batch_check(
                client, checks(), {"authorization_model_id": OTHER_MODEL_ID}
            )
            await self.batch_check(client, checks())

        self.assertEqual(server.model_ids_read, [OTHER_MODEL_ID, MODEL_ID])
        self.assertEqual(
            [body["authorization_model_id"] for body in server.sent],
            [OTHER_MODEL_ID, MODEL_ID],
        )

    @patch.object(rest.RESTClientObject, "request")
    async def test_uses_the_model_id_in_the_options_when_none_is_configured(
        self, mock_request
    ):
        self.configuration.authorization_model_id = None
        server = FakeServer()
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            response = await self.batch_check(
                client, checks(), {"authorization_model_id": OTHER_MODEL_ID}
            )

        self.assertEqual(server.model_ids_read, [OTHER_MODEL_ID])
        self.assertEqual(server.sent[0]["authorization_model_id"], OTHER_MODEL_ID)
        self.assertEqual(response.checks_sent, 2)

    @patch.object(rest.RESTClientObject, "request")
    async def test_rejects_an_option_value_that_is_not_a_bool(self, mock_request):
        async with OpenFgaClient(self.configuration) as client:
            with self.assertRaisesRegex(
                FgaValidationException, "merge_equivalent_checks must be a bool"
            ):
                await self.batch_check(
                    client, checks(), options={"merge_equivalent_checks": "true"}
                )

        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    async def test_reads_the_model_with_the_callers_headers(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            await self.batch_check(
                client, checks(), options={"headers": {"X-Custom": "1"}}
            )

        self.assertEqual(server.model_read_headers[0].get("X-Custom"), "1")

    @patch.object(rest.RESTClientObject, "request")
    async def test_sends_the_consistency_option(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            await self.batch_check(
                client,
                checks(),
                options={"consistency": ConsistencyPreference.HIGHER_CONSISTENCY},
            )

        self.assertEqual(server.sent[0]["consistency"], "HIGHER_CONSISTENCY")

    @patch.object(rest.RESTClientObject, "request")
    async def test_rejects_invalid_correlation_ids(self, mock_request):
        for correlation_id in ["has space", "x" * 37, "é", "a\n"]:
            items = checks()
            items[0].correlation_id = correlation_id

            async with OpenFgaClient(self.configuration) as client:
                with self.assertRaises(FgaValidationException):
                    await self.batch_check(client, items)

        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    async def test_rejects_duplicate_correlation_ids(self, mock_request):
        items = checks()
        items[1].correlation_id = "a"

        async with OpenFgaClient(self.configuration) as client:
            with self.assertRaisesRegex(
                FgaValidationException, r"Duplicate correlation_id \(a\) provided"
            ):
                await self.batch_check(client, items)

        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    async def test_generates_missing_correlation_ids(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server
        items = checks()
        items[3].correlation_id = None

        async with OpenFgaClient(self.configuration) as client:
            response = await self.batch_check(client, items)

        self.assertIsNotNone(items[3].correlation_id)
        self.assertEqual(response.result[3].correlation_id, items[3].correlation_id)

    def test_checks_sent_defaults_to_none_and_can_be_set(self):
        response = ClientBatchCheckResponse([])
        self.assertIsNone(response.checks_sent)

        response.checks_sent = 3

        self.assertEqual(response.checks_sent, 3)

    @patch.object(rest.RESTClientObject, "request")
    async def test_no_checks_sends_nothing(self, mock_request):
        async with OpenFgaClient(self.configuration) as client:
            response = await self.batch_check(client, [])

        self.assertEqual(response.result, [])
        self.assertEqual(response.checks_sent, 0)
        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    async def test_sends_unmerged_when_the_model_cannot_be_read(self, mock_request):
        server = FakeServer(model_error=rate_limited)
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            with self.assertLogs(
                "openfga_sdk.client._batch_check_merge", "WARNING"
            ) as logs:
                response = await self.batch_check(client, checks())
            second = await self.batch_check(client, checks())

        self.assertEqual(len(logs.records), 1)
        self.assertIn(MODEL_ID, logs.output[0])
        self.assertIn(STORE_ID, logs.output[0])
        self.assertIn("429", logs.output[0])
        self.assertEqual(server.model_reads, 1)
        self.assertEqual(sent_checks(server), UNMERGED * 2)
        self.assertEqual(response.checks_sent, 4)
        self.assertEqual(second.checks_sent, 4)
        self.assertEqual(
            [r.allowed for r in response.result], [True, False, False, False]
        )

    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch.object(rest.RESTClientObject, "request")
    async def test_sends_unmerged_when_the_server_fails_or_times_out(
        self, mock_request, mock_fallback
    ):
        for model_error, status in [(server_error, 500), (timed_out, None)]:
            with self.subTest(error=model_error.__name__):
                server = FakeServer(model_error=model_error)
                mock_request.side_effect = server

                async with OpenFgaClient(self.configuration) as client:
                    with self.assertLogs(
                        "openfga_sdk.client._batch_check_merge", "WARNING"
                    ):
                        response = await self.batch_check(client, checks())
                        await self.batch_check(client, checks())

                self.assertEqual(sent_checks(server), UNMERGED * 2)
                self.assertEqual(response.checks_sent, 4)
                # Only a 429 is remembered, so the next call reads again.
                self.assertEqual(server.model_reads, 2)
                self.assertEqual(
                    mock_fallback.call_args.kwargs["attributes"][
                        TelemetryAttributes.http_response_status_code
                    ],
                    status,
                )

    @patch.object(rest.RESTClientObject, "request")
    async def test_does_not_retry_the_model_read(self, mock_request):
        retries = {"retry_params": RetryParams(max_retry=3, min_wait_in_ms=1)}
        for model_error in [rate_limited, server_error, connection_dropped]:
            with self.subTest(error=model_error.__name__):
                server = FakeServer(model_error=model_error)
                mock_request.side_effect = server

                async with OpenFgaClient(self.configuration) as client:
                    with self.assertLogs(
                        "openfga_sdk.client._batch_check_merge", "WARNING"
                    ):
                        await self.batch_check(client, checks(), retries)

                self.assertEqual(server.model_reads, 1)
                self.assertEqual(sent_checks(server), UNMERGED)

    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch(
        "openfga_sdk.client._batch_check_merge.resolve",
        side_effect=RuntimeError("boom"),
    )
    @patch.object(rest.RESTClientObject, "request")
    async def test_sends_unmerged_when_grouping_fails(
        self, mock_request, _resolve, mock_fallback
    ):
        server = FakeServer()
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            with self.assertLogs(
                "openfga_sdk.client._batch_check_merge", "WARNING"
            ) as logs:
                response = await self.batch_check(client, checks())

        self.assertIn("couldn't group the checks", logs.output[0])
        self.assertEqual(sent_checks(server), UNMERGED)
        self.assertEqual(response.checks_sent, 4)
        self.assertEqual(
            [r.allowed for r in response.result], [True, False, False, False]
        )
        self.assertIsNone(
            mock_fallback.call_args.kwargs["attributes"][
                TelemetryAttributes.http_response_status_code
            ]
        )

    @patch.object(rest.RESTClientObject, "request")
    async def test_fails_before_sending_when_the_store_does_not_exist(
        self, mock_request
    ):
        server = FakeServer(model_error=store_not_found)
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            with self.assertNoLogs("openfga_sdk.client._batch_check_merge", "WARNING"):
                with self.assertRaises(NotFoundException):
                    await self.batch_check(client, checks())

        self.assertEqual(server.sent, [])

    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch.object(rest.RESTClientObject, "request")
    async def test_fails_like_the_option_off_when_the_token_request_fails(
        self, mock_request, mock_fallback
    ):
        for token, error_type in [
            (unauthorized, UnauthorizedException),
            (bad_request, ValidationException),
            (rate_limited, RateLimitExceededError),
            (server_error, ServiceException),
            (connection_dropped, aiohttp.ClientConnectionError),
            (no_token_issued, AuthenticationError),
        ]:
            with self.subTest(token=token.__name__):
                token_requests = []
                for merge in [False, True]:
                    server = FakeServer(token=token)
                    mock_request.side_effect = server

                    async with OpenFgaClient(token_configuration()) as client:
                        with self.assertNoLogs(
                            "openfga_sdk.client._batch_check_merge", "WARNING"
                        ):
                            with self.assertRaises(error_type):
                                await client.batch_check(
                                    ClientBatchCheckRequest(checks=checks()),
                                    options={"merge_equivalent_checks": merge},
                                )

                    self.assertEqual(server.model_reads, 0)
                    self.assertEqual(server.sent, [])
                    token_requests.append(server.token_requests)

                self.assertEqual(token_requests[1], token_requests[0])

        mock_fallback.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    async def test_a_failed_token_request_is_not_remembered(self, mock_request):
        server = FakeServer(token=rate_limited)
        mock_request.side_effect = server

        async with OpenFgaClient(token_configuration()) as client:
            with self.assertRaises(RateLimitExceededError):
                await self.batch_check(client, checks())

            server.token = token_issued
            response = await self.batch_check(client, checks())

        self.assertEqual(server.model_reads, 1)
        self.assertEqual(sent_checks(server), [("merged-1", "viewer"), ("d", "editor")])
        self.assertEqual(response.checks_sent, 2)

    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch.object(rest.RESTClientObject, "request")
    async def test_fails_when_the_model_read_cannot_renew_the_token(
        self, mock_request, mock_fallback
    ):
        for renewals in [0, 1]:
            with self.subTest(renewals_before_failing=renewals):
                server = FakeServer(token=short_lived_token_issued)
                mock_request.side_effect = server

                async with OpenFgaClient(token_configuration()) as client:
                    await client.batch_check(ClientBatchCheckRequest(checks=checks()))
                    server.token = short_lived_tokens_then_rate_limited(renewals)

                    with self.assertNoLogs(
                        "openfga_sdk.client._batch_check_merge", "WARNING"
                    ):
                        with self.assertRaises(RateLimitExceededError):
                            await self.batch_check(client, checks())

                    server.token = short_lived_token_issued
                    response = await self.batch_check(client, checks())

                self.assertEqual(server.model_reads, 1)
                self.assertEqual(response.checks_sent, 2)

        mock_fallback.assert_not_called()

    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch.object(rest.RESTClientObject, "request")
    async def test_sends_unmerged_when_the_read_fails_after_renewing_the_token(
        self, mock_request, mock_fallback
    ):
        server = FakeServer(model_error=rate_limited, token=short_lived_token_issued)
        mock_request.side_effect = server

        async with OpenFgaClient(token_configuration()) as client:
            with self.assertLogs("openfga_sdk.client._batch_check_merge", "WARNING"):
                response = await self.batch_check(client, checks())

        self.assertEqual(server.model_reads, 1)
        self.assertEqual(sent_checks(server), UNMERGED)
        self.assertEqual(response.checks_sent, 4)
        mock_fallback.assert_called_once()

    @patch.object(rest.RESTClientObject, "request")
    async def test_fails_before_sending_when_the_model_does_not_exist(
        self, mock_request
    ):
        server = FakeServer(model_error=model_not_found)
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            with self.assertNoLogs("openfga_sdk.client._batch_check_merge", "WARNING"):
                for _ in range(2):
                    with self.assertRaises(ValidationException) as raised:
                        await self.batch_check(client, checks())
                    self.assertEqual(
                        raised.exception.code, "authorization_model_not_found"
                    )

        self.assertEqual(server.sent, [])
        self.assertEqual(server.model_reads, 2)

    @patch.object(rest.RESTClientObject, "request")
    async def test_fails_before_sending_when_the_credentials_cannot_read_the_model(
        self, mock_request
    ):
        for model_error, error_type in [
            (unauthorized, UnauthorizedException),
            (forbidden, ForbiddenException),
        ]:
            with self.subTest(status=error_type.__name__):
                server = FakeServer(model_error=model_error)
                mock_request.side_effect = server

                async with OpenFgaClient(self.configuration) as client:
                    with self.assertNoLogs(
                        "openfga_sdk.client._batch_check_merge", "WARNING"
                    ):
                        for _ in range(2):
                            with self.assertRaises(error_type):
                                await self.batch_check(client, checks())

                self.assertEqual(server.sent, [])
                self.assertEqual(server.model_reads, 2)

    @patch.object(rest.RESTClientObject, "request")
    async def test_sends_unmerged_when_the_model_response_is_empty(self, mock_request):
        server = FakeServer(model_body={})
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            with self.assertLogs(
                "openfga_sdk.client._batch_check_merge", "WARNING"
            ) as logs:
                response = await self.batch_check(client, checks())

        self.assertEqual(len(logs.records), 1)
        self.assertEqual(sent_checks(server), UNMERGED)
        self.assertEqual(response.checks_sent, 4)

    @patch.object(rest.RESTClientObject, "request")
    async def test_copies_an_error_to_every_check_in_the_group(self, mock_request):
        server = FakeServer(
            answer=lambda check: (
                {"error": {"message": "boom"}}
                if check["correlation_id"] == "merged-1"
                else {"allowed": True}
            )
        )
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            response = await self.batch_check(client, checks())

        for result in response.result[:3]:
            self.assertFalse(result.allowed)
            self.assertEqual(result.error.message, "boom")
        self.assertTrue(response.result[3].allowed)
        self.assertIsNone(response.result[3].error)

    @patch.object(rest.RESTClientObject, "request")
    async def test_a_missing_answer_is_an_error_and_unknown_answers_are_ignored(
        self, mock_request
    ):
        def handle(method, url, **kwargs):
            if method == "GET":
                return mock_response(json.dumps({"authorization_model": MODEL}))
            return mock_response(
                json.dumps(
                    {"result": {"d": {"allowed": True}, "unknown": {"allowed": True}}}
                )
            )

        mock_request.side_effect = handle

        async with OpenFgaClient(self.configuration) as client:
            response = await self.batch_check(client, checks())

        self.assertEqual(
            [r.correlation_id for r in response.result], ["a", "b", "c", "d"]
        )
        for result in response.result[:3]:
            self.assertFalse(result.allowed)
            self.assertEqual(
                result.error.message, "No result returned for correlation_id (merged-1)"
            )
        self.assertTrue(response.result[3].allowed)

    @patch.object(rest.RESTClientObject, "request")
    async def test_a_failed_request_fails_the_call(self, mock_request):
        def handle(method, url, **kwargs):
            if method == "GET":
                return mock_response(json.dumps({"authorization_model": MODEL}))
            raise ValidationException(http_resp=http_mock_response("{}", 400))

        mock_request.side_effect = handle

        async with OpenFgaClient(self.configuration) as client:
            with self.assertRaises(ValidationException):
                await self.batch_check(client, checks())

    @patch.object(TelemetryMetrics, "batchCheckChecksSent")
    @patch.object(TelemetryMetrics, "batchCheckChecksRequested")
    @patch.object(rest.RESTClientObject, "request")
    async def test_counts_checks_even_when_a_request_fails(
        self, mock_request, mock_requested, mock_sent
    ):
        def handle(method, url, **kwargs):
            if method == "GET":
                return mock_response(json.dumps({"authorization_model": MODEL}))
            raise ValidationException(http_resp=http_mock_response("{}", 400))

        mock_request.side_effect = handle

        async with OpenFgaClient(self.configuration) as client:
            with self.assertRaises(ValidationException):
                await self.batch_check(client, checks())

        self.assertEqual(mock_requested.call_args.args, (4,))
        self.assertEqual(mock_sent.call_args.args, (2,))

    @patch.object(rest.RESTClientObject, "request")
    async def test_option_off_is_unchanged(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        async with OpenFgaClient(self.configuration) as client:
            response = await client.batch_check(
                ClientBatchCheckRequest(checks=checks())
            )

        self.assertEqual(server.model_reads, 0)
        self.assertEqual(sent_checks(server), UNMERGED)
        self.assertIsNone(response.checks_sent)

    @patch.object(TelemetryMetrics, "batchCheckChecksSent")
    @patch.object(TelemetryMetrics, "batchCheckChecksRequested")
    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch.object(TelemetryMetrics, "modelCacheLookup")
    @patch.object(rest.RESTClientObject, "request")
    async def test_records_telemetry(
        self, mock_request, mock_lookup, mock_fallback, mock_requested, mock_sent
    ):
        mock_request.side_effect = FakeServer()
        attributes = {
            TelemetryAttributes.fga_client_request_store_id: STORE_ID,
            TelemetryAttributes.fga_client_request_model_id: MODEL_ID,
        }

        async with OpenFgaClient(self.configuration) as client:
            await self.batch_check(client, checks())
            await self.batch_check(client, checks())

        self.assertEqual(
            [
                call.kwargs["attributes"][
                    TelemetryAttributes.fga_client_model_cache_result
                ]
                for call in mock_lookup.call_args_list
            ],
            ["miss", "hit"],
        )
        mock_fallback.assert_not_called()
        self.assertEqual(mock_requested.call_args.args, (4,))
        self.assertEqual(mock_requested.call_args.kwargs["attributes"], attributes)
        self.assertEqual(mock_sent.call_args.args, (2,))
        self.assertEqual(mock_sent.call_args.kwargs["attributes"], attributes)

    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch.object(rest.RESTClientObject, "request")
    async def test_records_the_fallback_with_its_status_code(
        self, mock_request, mock_fallback
    ):
        mock_request.side_effect = FakeServer(model_error=rate_limited)

        async with OpenFgaClient(self.configuration) as client:
            with self.assertLogs("openfga_sdk.client._batch_check_merge", "WARNING"):
                await self.batch_check(client, checks())

        attributes = mock_fallback.call_args.kwargs["attributes"]
        self.assertEqual(attributes[TelemetryAttributes.http_response_status_code], 429)
        self.assertEqual(
            attributes[TelemetryAttributes.fga_client_request_model_id], MODEL_ID
        )
