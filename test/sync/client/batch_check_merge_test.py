import json

from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase
from unittest.mock import patch

from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.models.batch_check_request import ClientBatchCheckRequest
from openfga_sdk.exceptions import FgaValidationException, ForbiddenException
from openfga_sdk.sync import rest
from openfga_sdk.sync.client.client import OpenFgaClient
from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.metrics import TelemetryMetrics
from test.client.batch_check_merge_test import (
    API_URL,
    BATCH_CHECK_URL,
    MODEL,
    MODEL_ID,
    MODEL_URL,
    STORE_ID,
    checks,
    http_mock_response,
    sent_checks,
)


def mock_response(body, status=200):
    obj = http_mock_response(body, status)
    return rest.RESTResponse(obj, obj.data)


class FakeServer:
    """
    Answers model reads and BatchCheck requests, and records what was sent.
    """

    def __init__(self, model_error=None, answer=None):
        self.model_error = model_error
        self.answer = answer or (
            lambda check: {"allowed": check["tuple_key"]["relation"] == "viewer"}
        )
        self.model_reads = 0
        self.model_read_headers = []
        self.sent = []

    def __call__(self, method, url, **kwargs):
        if method == "GET" and url == MODEL_URL:
            self.model_reads += 1
            self.model_read_headers.append(kwargs.get("headers") or {})
            if self.model_error is not None:
                raise self.model_error
            return mock_response(json.dumps({"authorization_model": MODEL}))

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


def forbidden():
    return ForbiddenException(http_resp=http_mock_response("{}", 403))


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
            with self.assertRaises(FgaValidationException):
                self.batch_check(client, checks())

        mock_request.assert_not_called()

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
        server = FakeServer(model_error=forbidden())
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            with self.assertLogs("openfga_sdk.sync.client.client", "WARNING") as logs:
                response = self.batch_check(client, checks())
            self.batch_check(client, checks())

        self.assertEqual(len(logs.records), 1)
        self.assertIn("403", logs.output[0])
        self.assertEqual(server.model_reads, 1)
        unmerged = [
            ("a", "viewer"),
            ("b", "can_view"),
            ("c", "can_share"),
            ("d", "editor"),
        ]
        self.assertEqual(sent_checks(server), unmerged * 2)
        self.assertEqual(response.checks_sent, 4)
        self.assertEqual(mock_fallback.call_count, 2)
        self.assertEqual(
            mock_fallback.call_args.kwargs["attributes"][
                TelemetryAttributes.http_response_status_code
            ],
            403,
        )

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

    @patch.object(rest.RESTClientObject, "request")
    def test_option_off_is_unchanged(self, mock_request):
        server = FakeServer()
        mock_request.side_effect = server

        with OpenFgaClient(self.configuration) as client:
            response = client.batch_check(ClientBatchCheckRequest(checks=checks()))

        self.assertEqual(server.model_reads, 0)
        self.assertEqual(
            sent_checks(server),
            [("a", "viewer"), ("b", "can_view"), ("c", "can_share"), ("d", "editor")],
        )
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
