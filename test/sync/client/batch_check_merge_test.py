import json

from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase
from unittest.mock import patch

from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.models.batch_check_request import ClientBatchCheckRequest
from openfga_sdk.exceptions import (
    AuthenticationError,
    FgaValidationException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from openfga_sdk.sync import rest
from openfga_sdk.sync.client.client import OpenFgaClient
from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.metrics import TelemetryMetrics
from test.client.batch_check_merge_test import (
    API_URL,
    BATCH_CHECK_URL,
    MODEL,
    MODEL_ID,
    MODELS_URL,
    NO_RETRY,
    OTHER_MODEL_ID,
    STORE_ID,
    UNMERGED,
    checks,
    forbidden,
    http_mock_response,
    model_not_found,
    rate_limited,
    sent_checks,
    server_error,
    store_not_found,
    timed_out,
    token_request_failed,
    unauthorized,
)


def mock_response(body, status=200):
    obj = http_mock_response(body, status)
    return rest.RESTResponse(obj, obj.data)


class FakeServer:
    """
    Answers model reads and BatchCheck requests, and records what was sent.
    """

    def __init__(self, model_error=None, answer=None, model_body=None):
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


class TestSyncBatchCheckMergeEquivalentChecks(TestCase):
    def setUp(self):
        self.configuration = ClientConfiguration(
            api_url=API_URL,
            store_id=STORE_ID,
            authorization_model_id=MODEL_ID,
        )

    def batch_check(self, client, items, options=None):
        return client.batch_check(
            ClientBatchCheckRequest(checks=items),
            options={"merge_equivalent_checks": True, **(options or {})},
        )

    @patch.object(rest.RESTClientObject, "request")
    def test_merges_aliases_and_copies_the_answer_back(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server
        items = checks()

        with OpenFgaClient(self.configuration) as client:
            response = self.batch_check(client, items)

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
    def test_merges_checks_that_would_land_in_different_batches(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            response = self.batch_check(
                client, checks()[:3], options={"max_batch_size": 1}
            )

        self.assertEqual(sent_checks(server), [("merged-1", "viewer")])
        self.assertEqual(response.checks_sent, 1)
        self.assertEqual(len(response.result), 3)

    @patch.object(rest.RESTClientObject, "request")
    def test_reads_the_model_once_across_threads_and_later_calls(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            with ThreadPoolExecutor(max_workers=5) as executor:
                list(
                    executor.map(lambda _: self.batch_check(client, checks()), range(5))
                )
            self.batch_check(client, checks())

        self.assertEqual(server.model_reads, 1)
        self.assertEqual(len(server.sent), 6)

    @patch.object(rest.RESTClientObject, "request")
    def test_requires_a_model_id(self, mock_request):
        self.configuration.authorization_model_id = None

        with OpenFgaClient(self.configuration) as client:
            with self.assertRaisesRegex(
                FgaValidationException, "authorization_model_id"
            ):
                self.batch_check(client, checks())

        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    def test_requires_a_store_id(self, mock_request):
        self.configuration.store_id = None

        with OpenFgaClient(self.configuration) as client:
            with self.assertRaisesRegex(FgaValidationException, "store_id"):
                self.batch_check(client, checks())

        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    def test_the_model_id_in_the_options_wins(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            self.batch_check(
                client, checks(), {"authorization_model_id": OTHER_MODEL_ID}
            )
            self.batch_check(client, checks())

        self.assertEqual(server.model_ids_read, [OTHER_MODEL_ID, MODEL_ID])
        self.assertEqual(
            [body["authorization_model_id"] for body in server.sent],
            [OTHER_MODEL_ID, MODEL_ID],
        )

    @patch.object(rest.RESTClientObject, "request")
    def test_uses_the_model_id_in_the_options_when_none_is_configured(
        self, mock_request
    ):
        self.configuration.authorization_model_id = None
        server = FakeServer()
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            response = self.batch_check(
                client, checks(), {"authorization_model_id": OTHER_MODEL_ID}
            )

        self.assertEqual(server.model_ids_read, [OTHER_MODEL_ID])
        self.assertEqual(server.sent[0]["authorization_model_id"], OTHER_MODEL_ID)
        self.assertEqual(response.checks_sent, 2)

    @patch.object(rest.RESTClientObject, "request")
    def test_rejects_an_option_value_that_is_not_a_bool(self, mock_request):
        with OpenFgaClient(self.configuration) as client:
            with self.assertRaisesRegex(
                FgaValidationException, "merge_equivalent_checks must be a bool"
            ):
                self.batch_check(
                    client, checks(), options={"merge_equivalent_checks": 1}
                )

        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    def test_reads_the_model_with_the_callers_headers(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            self.batch_check(client, checks(), options={"headers": {"X-Custom": "1"}})

        self.assertEqual(server.model_read_headers[0].get("X-Custom"), "1")

    @patch.object(rest.RESTClientObject, "request")
    def test_rejects_invalid_and_duplicate_correlation_ids(self, mock_request):
        invalid = checks()
        invalid[0].correlation_id = "a\n"
        duplicate = checks()
        duplicate[1].correlation_id = "a"

        with OpenFgaClient(self.configuration) as client:
            with self.assertRaises(FgaValidationException):
                self.batch_check(client, invalid)
            with self.assertRaisesRegex(
                FgaValidationException, r"Duplicate correlation_id \(a\) provided"
            ):
                self.batch_check(client, duplicate)

        mock_request.assert_not_called()

    @patch.object(rest.RESTClientObject, "request")
    def test_generates_missing_correlation_ids(self, mock_request):
        mock_request.side_effect = FakeServer()
        items = checks()
        items[3].correlation_id = None

        with OpenFgaClient(self.configuration) as client:
            response = self.batch_check(client, items)

        self.assertIsNotNone(items[3].correlation_id)
        self.assertEqual(response.result[3].correlation_id, items[3].correlation_id)

    @patch.object(rest.RESTClientObject, "request")
    def test_no_checks_sends_nothing(self, mock_request):
        with OpenFgaClient(self.configuration) as client:
            response = self.batch_check(client, [])

        self.assertEqual(response.result, [])
        self.assertEqual(response.checks_sent, 0)
        mock_request.assert_not_called()

    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch.object(rest.RESTClientObject, "request")
    def test_sends_unmerged_when_the_model_cannot_be_read(
        self, mock_request, mock_fallback
    ):
        server = FakeServer(model_error=rate_limited)
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            with self.assertLogs(
                "openfga_sdk.client._batch_check_merge", "WARNING"
            ) as logs:
                response = self.batch_check(client, checks(), NO_RETRY)
            self.batch_check(client, checks(), NO_RETRY)

        self.assertEqual(len(logs.records), 1)
        self.assertIn("429", logs.output[0])
        self.assertEqual(server.model_reads, 1)
        self.assertEqual(sent_checks(server), UNMERGED * 2)
        self.assertEqual(response.checks_sent, 4)
        self.assertEqual(mock_fallback.call_count, 2)
        self.assertEqual(
            mock_fallback.call_args.kwargs["attributes"][
                TelemetryAttributes.http_response_status_code
            ],
            429,
        )

    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch.object(rest.RESTClientObject, "request")
    def test_sends_unmerged_when_the_server_fails_or_times_out(
        self, mock_request, mock_fallback
    ):
        for model_error, status in [(server_error, 500), (timed_out, None)]:
            with self.subTest(error=model_error.__name__):
                server = FakeServer(model_error=model_error)
                mock_request.side_effect = server

                with OpenFgaClient(self.configuration) as client:
                    with self.assertLogs(
                        "openfga_sdk.client._batch_check_merge", "WARNING"
                    ):
                        response = self.batch_check(client, checks(), NO_RETRY)
                        self.batch_check(client, checks(), NO_RETRY)

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

    @patch.object(TelemetryMetrics, "batchCheckMergeFallback")
    @patch(
        "openfga_sdk.client._batch_check_merge.resolve",
        side_effect=RuntimeError("boom"),
    )
    @patch.object(rest.RESTClientObject, "request")
    def test_sends_unmerged_when_grouping_fails(
        self, mock_request, _resolve, mock_fallback
    ):
        server = FakeServer()
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            with self.assertLogs(
                "openfga_sdk.client._batch_check_merge", "WARNING"
            ) as logs:
                response = self.batch_check(client, checks())

        self.assertIn("couldn't group the checks", logs.output[0])
        self.assertEqual(sent_checks(server), UNMERGED)
        self.assertEqual(response.checks_sent, 4)
        self.assertIsNone(
            mock_fallback.call_args.kwargs["attributes"][
                TelemetryAttributes.http_response_status_code
            ]
        )

    @patch.object(rest.RESTClientObject, "request")
    def test_fails_before_sending_when_the_store_does_not_exist_or_no_token(
        self, mock_request
    ):
        for model_error, error_type in [
            (store_not_found, NotFoundException),
            (token_request_failed, AuthenticationError),
        ]:
            with self.subTest(error=model_error.__name__):
                server = FakeServer(model_error=model_error)
                mock_request.side_effect = server

                with OpenFgaClient(self.configuration) as client:
                    with self.assertNoLogs(
                        "openfga_sdk.client._batch_check_merge", "WARNING"
                    ):
                        with self.assertRaises(error_type):
                            self.batch_check(client, checks())

                self.assertEqual(server.sent, [])

    @patch.object(rest.RESTClientObject, "request")
    def test_fails_before_sending_when_the_model_does_not_exist(self, mock_request):
        server = FakeServer(model_error=model_not_found)
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            with self.assertRaises(ValidationException) as raised:
                self.batch_check(client, checks())

        self.assertEqual(raised.exception.code, "authorization_model_not_found")
        self.assertEqual(server.sent, [])

    @patch.object(rest.RESTClientObject, "request")
    def test_fails_before_sending_when_the_credentials_cannot_read_the_model(
        self, mock_request
    ):
        for model_error, error_type in [
            (unauthorized, UnauthorizedException),
            (forbidden, ForbiddenException),
        ]:
            with self.subTest(status=error_type.__name__):
                server = FakeServer(model_error=model_error)
                mock_request.side_effect = server

                with OpenFgaClient(self.configuration) as client:
                    with self.assertNoLogs(
                        "openfga_sdk.client._batch_check_merge", "WARNING"
                    ):
                        for _ in range(2):
                            with self.assertRaises(error_type):
                                self.batch_check(client, checks())

                self.assertEqual(server.sent, [])
                self.assertEqual(server.model_reads, 2)

    @patch.object(rest.RESTClientObject, "request")
    def test_sends_unmerged_when_the_model_response_is_empty(self, mock_request):
        server = FakeServer(model_body={})
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            with self.assertLogs(
                "openfga_sdk.client._batch_check_merge", "WARNING"
            ) as logs:
                response = self.batch_check(client, checks())

        self.assertEqual(len(logs.records), 1)
        self.assertEqual(sent_checks(server), UNMERGED)
        self.assertEqual(response.checks_sent, 4)

    @patch.object(rest.RESTClientObject, "request")
    def test_copies_an_error_to_every_check_in_the_group(self, mock_request):
        mock_request.side_effect = FakeServer(
            answer=lambda check: (
                {"error": {"message": "boom"}}
                if check["correlation_id"] == "merged-1"
                else {"allowed": True}
            )
        )

        with OpenFgaClient(self.configuration) as client:
            response = self.batch_check(client, checks())

        for result in response.result[:3]:
            self.assertFalse(result.allowed)
            self.assertEqual(result.error.message, "boom")
        self.assertTrue(response.result[3].allowed)

    @patch.object(rest.RESTClientObject, "request")
    def test_a_missing_answer_is_an_error_and_unknown_answers_are_ignored(
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

        with OpenFgaClient(self.configuration) as client:
            response = self.batch_check(client, checks())

        self.assertEqual(
            [r.correlation_id for r in response.result], ["a", "b", "c", "d"]
        )
        for result in response.result[:3]:
            self.assertFalse(result.allowed)
            self.assertEqual(
                result.error.message, "No result returned for correlation_id (merged-1)"
            )
        self.assertTrue(response.result[3].allowed)

    @patch.object(TelemetryMetrics, "batchCheckChecksSent")
    @patch.object(TelemetryMetrics, "batchCheckChecksRequested")
    @patch.object(rest.RESTClientObject, "request")
    def test_a_failed_request_fails_the_call_and_still_counts_checks(
        self, mock_request, mock_requested, mock_sent
    ):
        def handle(method, url, **kwargs):
            if method == "GET":
                return mock_response(json.dumps({"authorization_model": MODEL}))
            raise ValidationException(http_resp=http_mock_response("{}", 400))

        mock_request.side_effect = handle

        with OpenFgaClient(self.configuration) as client:
            with self.assertRaises(ValidationException):
                self.batch_check(client, checks())

        self.assertEqual(mock_requested.call_args.args, (4,))
        self.assertEqual(mock_sent.call_args.args, (2,))

    @patch.object(rest.RESTClientObject, "request")
    def test_option_off_is_unchanged(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            response = client.batch_check(ClientBatchCheckRequest(checks=checks()))

        self.assertEqual(server.model_reads, 0)
        self.assertEqual(sent_checks(server), UNMERGED)
        self.assertIsNone(response.checks_sent)

    @patch.object(TelemetryMetrics, "batchCheckChecksSent")
    @patch.object(TelemetryMetrics, "batchCheckChecksRequested")
    @patch.object(TelemetryMetrics, "modelCacheLookup")
    @patch.object(rest.RESTClientObject, "request")
    def test_records_telemetry(
        self, mock_request, mock_lookup, mock_requested, mock_sent
    ):
        mock_request.side_effect = FakeServer()

        with OpenFgaClient(self.configuration) as client:
            self.batch_check(client, checks())
            self.batch_check(client, checks())

        self.assertEqual(
            [
                call.kwargs["attributes"][
                    TelemetryAttributes.fga_client_model_cache_result
                ]
                for call in mock_lookup.call_args_list
            ],
            ["miss", "hit"],
        )
        self.assertEqual(mock_requested.call_args.args, (4,))
        self.assertEqual(mock_sent.call_args.args, (2,))
