import uuid

from concurrent.futures import ThreadPoolExecutor

from openfga_sdk.client.configuration import ClientConfiguration
from openfga_sdk.client.models.assertion import ClientAssertion
from openfga_sdk.client.models.batch_check_item import (
    ClientBatchCheckItem,
    construct_batch_item,
)
from openfga_sdk.client.models.batch_check_request import ClientBatchCheckRequest
from openfga_sdk.client.models.batch_check_response import ClientBatchCheckResponse
from openfga_sdk.client.models.batch_check_single_response import (
    ClientBatchCheckSingleResponse,
)
from openfga_sdk.client.models.check_request import (
    ClientCheckRequest,
    construct_check_request,
)
from openfga_sdk.client.models.client_batch_check_response import (
    ClientBatchCheckClientResponse,
)
from openfga_sdk.client.models.expand_request import ClientExpandRequest
from openfga_sdk.client.models.list_objects_request import ClientListObjectsRequest
from openfga_sdk.client.models.list_relations_request import ClientListRelationsRequest
from openfga_sdk.client.models.list_users_request import ClientListUsersRequest
from openfga_sdk.client.models.read_changes_request import ClientReadChangesRequest
from openfga_sdk.client.models.tuple import ClientTuple, convert_tuple_keys
from openfga_sdk.client.models.write_request import ClientWriteRequest
from openfga_sdk.client.models.write_response import ClientWriteResponse
from openfga_sdk.client.models.write_single_response import (
    construct_write_single_response,
)
from openfga_sdk.client.models.write_transaction_opts import WriteTransactionOpts
from openfga_sdk.constants import (
    CLIENT_BULK_REQUEST_ID_HEADER,
    CLIENT_MAX_BATCH_SIZE,
    CLIENT_MAX_METHOD_PARALLEL_REQUESTS,
    CLIENT_METHOD_HEADER,
)
from openfga_sdk.exceptions import (
    AuthenticationError,
    FgaValidationException,
    UnauthorizedException,
)
from openfga_sdk.models.assertion import Assertion
from openfga_sdk.models.batch_check_request import BatchCheckRequest
from openfga_sdk.models.check_request import CheckRequest
from openfga_sdk.models.contextual_tuple_keys import ContextualTupleKeys
from openfga_sdk.models.create_store_request import CreateStoreRequest
from openfga_sdk.models.expand_request import ExpandRequest
from openfga_sdk.models.expand_request_tuple_key import ExpandRequestTupleKey
from openfga_sdk.models.list_objects_request import ListObjectsRequest
from openfga_sdk.models.list_users_request import ListUsersRequest
from openfga_sdk.models.read_authorization_model_response import (
    ReadAuthorizationModelResponse,
)
from openfga_sdk.models.read_request import ReadRequest
from openfga_sdk.models.read_request_tuple_key import ReadRequestTupleKey
from openfga_sdk.models.streamed_list_objects_response import (
    StreamedListObjectsResponse,
)
from openfga_sdk.models.tuple_key import TupleKey
from openfga_sdk.models.write_assertions_request import WriteAssertionsRequest
from openfga_sdk.models.write_authorization_model_request import (
    WriteAuthorizationModelRequest,
)
from openfga_sdk.models.write_request import WriteRequest
from openfga_sdk.sync.api_client import ApiClient
from openfga_sdk.sync.open_fga_api import OpenFgaApi
from openfga_sdk.validation import is_well_formed_ulid_string


def _chuck_array(array, max_size):
    """
    Helper function to chuck array into arrays of max_size
    """
    return [
        array[i * max_size : (i + 1) * max_size]
        for i in range((len(array) + max_size - 1) // max_size)
    ]


def set_heading_if_not_set(
    options: dict[str, int | str | dict[str, int | str]] | None,
    name: str,
    value: str,
) -> dict[str, int | str | dict[str, int | str]]:
    """
    Set heading to the value if it is not set
    """
    _options: dict[str, int | str | dict[str, int | str]] = (
        options if options is not None else {}
    )

    if type(_options.get("headers")) is not dict:
        _options["headers"] = {}

    if type(_options["headers"]) is dict:
        if _options["headers"].get(name) is None:
            _options["headers"][name] = value

    return _options


def options_to_kwargs(
    options: dict[str, int | str | dict[str, int | str]] | None = None,
) -> dict[str, int | str | dict[str, int | str]]:
    """
    Return kwargs with continuation_token and page_size
    """
    kwargs = {}
    if options is not None:
        if options.get("name"):
            kwargs["name"] = options["name"]
        if options.get("page_size"):
            kwargs["page_size"] = options["page_size"]
        if options.get("continuation_token"):
            kwargs["continuation_token"] = options["continuation_token"]
        if options.get("headers"):
            kwargs["_headers"] = options["headers"]
        if options.get("retry_params"):
            kwargs["_retry_params"] = options["retry_params"]
    return kwargs


def options_to_transaction_info(
    options: dict[str, int | str | dict[str, int | str]] | None = None,
):
    """
    Return the transaction info
    """
    if options is not None and options.get("transaction"):
        return options["transaction"]
    return WriteTransactionOpts()


def options_to_conflict_info(
    options: dict[str, int | str | dict[str, int | str]] | None = None,
):
    """
    Return the conflict info
    """
    if options is not None and options.get("conflict"):
        return options["conflict"]
    return None


def _check_errored(response: ClientBatchCheckClientResponse):
    """
    Helper function to return whether the response is errored
    """
    return response.error is not None


def _check_allowed(response: ClientBatchCheckClientResponse):
    """
    Helper function to return whether the response is check is allowed
    """
    return response.allowed


class OpenFgaClient:
    """
    OpenFgaClient is the entry point for invoking calls against the OpenFGA API.
    """

    def __init__(self, configuration: ClientConfiguration) -> None:
        self._client_configuration = configuration
        self._api_client = ApiClient(configuration)
        self._api = OpenFgaApi(self._api_client)

        # Set default headers from configuration
        if configuration.headers:
            for header_name, header_value in configuration.headers.items():
                self._api_client.set_default_header(header_name, header_value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._api.close()

    def _get_authorization_model_id(
        self,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ) -> str | None:
        """
        Return the authorization model ID if specified in the options.
        Otherwise, return the authorization model ID stored in the client's configuration
        """
        authorization_model_id = self._client_configuration.authorization_model_id
        if options is not None and "authorization_model_id" in options:
            authorization_model_id = options["authorization_model_id"]
        if authorization_model_id is None or authorization_model_id == "":
            return None
        if is_well_formed_ulid_string(authorization_model_id) is False:
            raise FgaValidationException(
                f"authorization_model_id ('{authorization_model_id}') is not in a valid ulid format"
            )
        return authorization_model_id

    def _get_consistency(
        self,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ) -> str | None:
        """
        Returns the consistency requested if specified in the options.
        Otherwise, returns None.
        """
        consistency: int | str | dict[str, int | str] | None = (
            options.get("consistency", None) if options is not None else None
        )

        if type(consistency) is str:
            return consistency

        return None

    def set_store_id(self, value):
        """
        Update the store ID in the configuration
        """
        self._api_client.set_store_id(value)

    def get_store_id(self):
        """
        Return the store id (if any) store in the configuration
        """
        return self._api_client.get_store_id()

    def set_authorization_model_id(self, value):
        """
        Update the authorization model id in the configuration
        """
        self._client_configuration.authorization_model_id = value

    def get_authorization_model_id(self):
        """
        Return the authorization model id
        """
        return self._client_configuration.authorization_model_id

    #################
    # Stores
    #################

    def list_stores(
        self, options: dict[str, int | str | dict[str, int | str]] | None = None
    ):
        """
        List the stores in the system
        :param name(options) - The name parameter instructs the API to only include results that match that name. Multiple results may be returned. Only exact matches will be returned; substring matches and regexes will not be evaluated.
        :param page_size(options) - Number of items returned per request
        :param continuation_token(options) - No continuation_token by default
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        # convert options to kwargs
        kwargs = options_to_kwargs(options)
        api_response = self._api.list_stores(
            **kwargs,
        )
        return api_response

    def create_store(
        self,
        body: CreateStoreRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Create the stores in the system
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        kwargs = options_to_kwargs(options)
        api_response = self._api.create_store(body, **kwargs)
        return api_response

    def get_store(
        self, options: dict[str, int | str | dict[str, int | str]] | None = None
    ):
        """
        Get the store info in the system. Store id is from the configuration.
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        kwargs = options_to_kwargs(options)
        api_response = self._api.get_store(
            **kwargs,
        )
        return api_response

    def delete_store(
        self, options: dict[str, int | str | dict[str, int | str]] | None = None
    ):
        """
        Delete the store from the system. Store id is from the configuration.
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        kwargs = options_to_kwargs(options)
        api_response = self._api.delete_store(
            **kwargs,
        )
        return api_response

    #######################
    # Authorization Models
    #######################

    def read_authorization_models(
        self, options: dict[str, int | str | dict[str, int | str]] | None = None
    ):
        """
        Return all the authorization models for a particular store.
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        kwargs = options_to_kwargs(options)
        api_response = self._api.read_authorization_models(
            **kwargs,
        )
        return api_response

    def write_authorization_model(
        self,
        body: WriteAuthorizationModelRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Write authorization model.
        :param body - WriteAuthorizationModelRequest
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        kwargs = options_to_kwargs(options)
        api_response = self._api.write_authorization_model(
            body,
            **kwargs,
        )
        return api_response

    def read_authorization_model(
        self, options: dict[str, int | str | dict[str, int | str]] | None = None
    ):
        """
        Read an authorization model.
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        kwargs = options_to_kwargs(options)
        authorization_model_id = self._get_authorization_model_id(options)
        api_response = self._api.read_authorization_model(
            authorization_model_id,
            **kwargs,
        )
        return api_response

    def read_latest_authorization_model(
        self, options: dict[str, int | str | dict[str, int | str]] | None = None
    ):
        """
        Convenient method of reading the latest authorization model
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        options = set_heading_if_not_set(
            options, CLIENT_METHOD_HEADER, "ReadLatestAuthorizationModel"
        )
        options["page_size"] = 1
        api_response = self.read_authorization_models(options)
        model = (
            api_response.authorization_models[0]
            if len(api_response.authorization_models) > 0
            else None
        )
        return ReadAuthorizationModelResponse(model)

    #######################
    # Relationship Tuples
    #######################

    def read_changes(
        self,
        body: ClientReadChangesRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Read changes for specified type
        :param body - the type we want to look for change
        :param page_size(options) - Number of items returned per request
        :param continuation_token(options) - No continuation_token by default
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        kwargs = options_to_kwargs(options)

        if body.type is not None:
            kwargs["type"] = body.type

        if body.start_time is not None:
            kwargs["start_time"] = body.start_time

        api_response = self._api.read_changes(
            **kwargs,
        )
        return api_response

    def read(
        self,
        body: ReadRequestTupleKey,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Read changes for specified type
        :param body - the tuples we want to read
        :param page_size(options) - Number of items returned per request
        :param continuation_token(options) - No continuation_token by default
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        :param consistency(options) - The type of consistency preferred for the request
        """
        page_size = None
        continuation_token = None
        if options:
            if options.get("page_size"):
                page_size = options.get("page_size")
                options.pop("page_size")
            if options.get("continuation_token"):
                continuation_token = options.get("continuation_token")
                options.pop("continuation_token")
        kwargs = options_to_kwargs(options)

        if body is None or (
            body.object is None and body.relation is None and body.user is None
        ):
            tuple_key = None
        else:
            tuple_key = body

        api_response = self._api.read(
            ReadRequest(
                tuple_key=tuple_key,
                page_size=page_size,
                continuation_token=continuation_token,
                consistency=self._get_consistency(options),
            ),
            **kwargs,
        )
        return api_response

    def _write_single_batch(
        self,
        batch: list[ClientTuple],
        is_write: bool,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        try:
            write_batch = None
            delete_batch = None
            if is_write:
                write_batch = batch
            else:
                delete_batch = batch
            self._write_with_transaction(
                ClientWriteRequest(writes=write_batch, deletes=delete_batch), options
            )
            return [construct_write_single_response(i, True, None) for i in batch]
        except (AuthenticationError, UnauthorizedException) as err:
            raise err
        except Exception as err:
            return [construct_write_single_response(i, False, err) for i in batch]

    def _write_batches(
        self,
        tuple_keys: list[ClientTuple],
        transaction: WriteTransactionOpts,
        is_write: bool,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Internal function for write/delete batches
        """
        chunks = _chuck_array(tuple_keys, transaction.max_per_chunk)

        write_batches = _chuck_array(chunks, transaction.max_parallel_requests)
        batch_write_responses = []
        for write_batch in write_batches:
            response = [
                self._write_single_batch(i, is_write, options) for i in write_batch
            ]
            flatten_list = [
                item
                for batch_single_response in response
                for item in batch_single_response
            ]
            batch_write_responses.extend(flatten_list)

        return batch_write_responses

    def _write_with_transaction(
        self,
        body: ClientWriteRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Write or deletes tuples
        """
        kwargs = options_to_kwargs(options)
        conflict_options = options_to_conflict_info(options)

        # Extract conflict options to pass to the tuple key methods
        on_duplicate = None
        on_missing = None
        if conflict_options:
            if conflict_options.on_duplicate_writes:
                on_duplicate = conflict_options.on_duplicate_writes.value
            if conflict_options.on_missing_deletes:
                on_missing = conflict_options.on_missing_deletes.value

        writes_tuple_keys = None
        deletes_tuple_keys = None
        if body.writes:
            writes_tuple_keys = body.get_writes_tuple_keys(on_duplicate=on_duplicate)
        if body.deletes:
            deletes_tuple_keys = body.get_deletes_tuple_keys(on_missing=on_missing)

        self._api.write(
            WriteRequest(
                writes=writes_tuple_keys,
                deletes=deletes_tuple_keys,
                authorization_model_id=self._get_authorization_model_id(options),
            ),
            **kwargs,
        )
        # any error will result in exception being thrown and not reached below code
        writes_response = None
        if body.writes:
            writes_response = [
                construct_write_single_response(i, True, None) for i in body.writes
            ]
        deletes_response = None
        if body.deletes:
            deletes_response = [
                construct_write_single_response(i, True, None) for i in body.deletes
            ]
        return ClientWriteResponse(writes=writes_response, deletes=deletes_response)

    def write(
        self,
        body: ClientWriteRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Write or deletes tuples
        :param body - the write request
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        options = set_heading_if_not_set(options, CLIENT_METHOD_HEADER, "Writes")
        transaction = options_to_transaction_info(options)
        if not transaction.disabled:
            results = self._write_with_transaction(body, options)
            return results

        options = set_heading_if_not_set(
            options, CLIENT_BULK_REQUEST_ID_HEADER, str(uuid.uuid4())
        )

        # otherwise, it is not a transaction and it is a batch write requests
        writes_response = None
        if body.writes:
            writes_response = self._write_batches(
                body.writes, transaction, True, options
            )
        deletes_response = None
        if body.deletes:
            deletes_response = self._write_batches(
                body.deletes, transaction, False, options
            )
        return ClientWriteResponse(writes=writes_response, deletes=deletes_response)

    def write_tuples(
        self,
        body: list[ClientTuple],
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Convenient method for writing tuples
        :param body - the list of tuples we want to write
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        options = set_heading_if_not_set(options, CLIENT_METHOD_HEADER, "WriteTuples")
        result = self.write(ClientWriteRequest(body, None), options)
        return result

    def delete_tuples(
        self,
        body: list[ClientTuple],
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Convenient method for deleteing tuples
        :param body - the list of tuples we want to delete
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        options = set_heading_if_not_set(options, CLIENT_METHOD_HEADER, "DeleteTuples")
        result = self.write(ClientWriteRequest(None, body), options)
        return result

    #######################
    # Relationship Queries
    #######################
    def check(
        self,
        body: ClientCheckRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Check whether a user is authorized to access an object
        :param body - ClientCheckRequest defining check request
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        :param consistency(options) - The type of consistency preferred for the request
        """
        kwargs = options_to_kwargs(options)

        req_body = CheckRequest(
            tuple_key=TupleKey(
                user=body.user,
                relation=body.relation,
                object=body.object,
            ),
            context=body.context,
            authorization_model_id=self._get_authorization_model_id(options),
            consistency=self._get_consistency(options),
        )
        if body.contextual_tuples:
            req_body.contextual_tuples = ContextualTupleKeys(
                tuple_keys=convert_tuple_keys(body.contextual_tuples)
            )
        api_response = self._api.check(body=req_body, **kwargs)
        return api_response

    def _single_client_batch_check(
        self,
        body: ClientCheckRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Run a single batch request and return body in a SingleBatchCheckResponse
        :param body - ClientCheckRequest defining check request
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        """
        try:
            api_response = self.check(body, options)
            return ClientBatchCheckClientResponse(
                allowed=api_response.allowed,
                request=body,
                response=api_response,
                error=None,
            )
        except (AuthenticationError, UnauthorizedException) as err:
            raise err
        except Exception as err:
            return ClientBatchCheckClientResponse(
                allowed=False, request=body, response=None, error=err
            )

    def client_batch_check(
        self,
        body: list[ClientCheckRequest],
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Run a set of checks
        :param body - list of ClientCheckRequest defining check request
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param max_parallel_requests(options) - Max number of requests to issue in parallel. Defaults to 10
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        :param consistency(options) - The type of consistency preferred for the request
        """
        options = set_heading_if_not_set(options, CLIENT_METHOD_HEADER, "BatchCheck")
        options = set_heading_if_not_set(
            options, CLIENT_BULK_REQUEST_ID_HEADER, str(uuid.uuid4())
        )

        max_parallel_requests = CLIENT_MAX_METHOD_PARALLEL_REQUESTS
        if options is not None and "max_parallel_requests" in options:
            if (
                isinstance(options["max_parallel_requests"], str)
                and options["max_parallel_requests"].isdigit()
            ):
                max_parallel_requests = int(options["max_parallel_requests"])
            elif isinstance(options["max_parallel_requests"], int):
                max_parallel_requests = options["max_parallel_requests"]

        batch_check_response = []

        def single_batch_check(request):
            return self._single_client_batch_check(request, options)

        with ThreadPoolExecutor(max_workers=max_parallel_requests) as executor:
            for response in executor.map(single_batch_check, body):
                batch_check_response.append(response)

        return batch_check_response

    def _single_batch_check(
        self,
        body: BatchCheckRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Run a single BatchCheck request
        :param body - list[ClientCheckRequest] defining check request
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        """
        try:
            kwargs = options_to_kwargs(options)
            api_response = self._api.batch_check(body, **kwargs)
            return api_response
        # Does this cover all error cases? If one fails with a 4xx/5xx then all should?
        except Exception as err:
            raise err

    def batch_check(
        self,
        body: ClientBatchCheckRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Run a batchcheck request
        :param body - BatchCheck request
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param max_parallel_requests(options) - Max number of requests to issue in parallel. Defaults to 10
        :param max_batch_size(options) - Max number of checks to include in a request. Defaults to 50
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        options = set_heading_if_not_set(
            options, CLIENT_BULK_REQUEST_ID_HEADER, str(uuid.uuid4())
        )

        max_parallel_requests = CLIENT_MAX_METHOD_PARALLEL_REQUESTS
        if options is not None and "max_parallel_requests" in options:
            if (
                isinstance(options["max_parallel_requests"], str)
                and options["max_parallel_requests"].isdigit()
            ):
                max_parallel_requests = int(options["max_parallel_requests"])
            elif isinstance(options["max_parallel_requests"], int):
                max_parallel_requests = options["max_parallel_requests"]

        max_batch_size = CLIENT_MAX_BATCH_SIZE
        if options is not None and "max_batch_size" in options:
            if (
                isinstance(options["max_batch_size"], str)
                and options["max_batch_size"].isdigit()
            ):
                max_batch_size = int(options["max_batch_size"])
            elif isinstance(options["max_batch_size"], int):
                max_batch_size = options["max_batch_size"]

        id_to_check: dict[str, ClientBatchCheckItem] = {}

        def track_and_transform(checks):
            transformed = []
            for check in checks:
                if check.correlation_id is None:
                    check.correlation_id = str(uuid.uuid4())

                if check.correlation_id in id_to_check:
                    raise FgaValidationException(
                        f"Duplicate correlation_id ({check.correlation_id}) provided"
                    )

                id_to_check[check.correlation_id] = check

                transformed.append(construct_batch_item(check))
            return transformed

        checks = [
            track_and_transform(
                body.checks[i * max_batch_size : (i + 1) * max_batch_size]
            )
            for i in range((len(body.checks) + max_batch_size - 1) // max_batch_size)
        ]

        def map_response(id, result):
            check = id_to_check[id]
            return ClientBatchCheckSingleResponse(
                allowed=result.allowed,
                request=check,
                correlation_id=id,
                error=result.error,
            )

        def single_batch_check(checks):
            res = self._single_batch_check(
                BatchCheckRequest(
                    checks=checks,
                    authorization_model_id=self._get_authorization_model_id(options),
                    consistency=self._get_consistency(options),
                ),
                options,
            )

            return res

        result = []

        with ThreadPoolExecutor(max_workers=max_parallel_requests) as executor:
            for response in executor.map(single_batch_check, checks):
                result.extend(
                    [
                        map_response(c_id, c_result)
                        for c_id, c_result in response.result.items()
                    ]
                )

        return ClientBatchCheckResponse(result)

    def expand(
        self,
        body: ClientExpandRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Run expand request
        :param body - list of ClientExpandRequest defining expand request
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        :param consistency(options) - The type of consistency preferred for the request
        """
        kwargs = options_to_kwargs(options)

        req_body = ExpandRequest(
            tuple_key=ExpandRequestTupleKey(
                relation=body.relation,
                object=body.object,
            ),
            authorization_model_id=self._get_authorization_model_id(options),
            consistency=self._get_consistency(options),
        )
        if body.contextual_tuples:
            req_body.contextual_tuples = ContextualTupleKeys(
                tuple_keys=convert_tuple_keys(body.contextual_tuples)
            )
        api_response = self._api.expand(body=req_body, **kwargs)
        return api_response

    def list_objects(
        self,
        body: ClientListObjectsRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Run list object request
        :param body - list object parameters
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        :param consistency(options) - The type of consistency preferred for the request
        """
        kwargs = options_to_kwargs(options)

        req_body = ListObjectsRequest(
            authorization_model_id=self._get_authorization_model_id(options),
            user=body.user,
            relation=body.relation,
            type=body.type,
            context=body.context,
            consistency=self._get_consistency(options),
        )
        if body.contextual_tuples:
            req_body.contextual_tuples = ContextualTupleKeys(
                tuple_keys=convert_tuple_keys(body.contextual_tuples)
            )
        api_response = self._api.list_objects(body=req_body, **kwargs)
        return api_response

    def streamed_list_objects(
        self,
        body: ClientListObjectsRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Retrieve all objects of the given type that the user has a relation with, using the streaming ListObjects API.

        :param body - list object parameters
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        :param consistency(options) - The type of consistency preferred for the request
        """
        kwargs = options_to_kwargs(options)
        kwargs["_streaming"] = True

        req_body = ListObjectsRequest(
            authorization_model_id=self._get_authorization_model_id(options),
            user=body.user,
            relation=body.relation,
            type=body.type,
            context=body.context,
            consistency=self._get_consistency(options),
        )

        if body.contextual_tuples:
            req_body.contextual_tuples = ContextualTupleKeys(
                tuple_keys=convert_tuple_keys(body.contextual_tuples)
            )

        for response in self._api.streamed_list_objects(body=req_body, **kwargs):
            if response and "result" in response and "object" in response["result"]:
                yield StreamedListObjectsResponse(response["result"]["object"])

        return

    def list_relations(
        self,
        body: ClientListRelationsRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Return all the relations for which user has a relationship with the object
        :param body - list relation request
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        :param consistency(options) - The type of consistency preferred for the request
        """
        options = set_heading_if_not_set(options, CLIENT_METHOD_HEADER, "ListRelations")
        options = set_heading_if_not_set(
            options, CLIENT_BULK_REQUEST_ID_HEADER, str(uuid.uuid4())
        )

        request_body = [
            construct_check_request(
                user=body.user,
                relation=i,
                object=body.object,
                contextual_tuples=body.contextual_tuples,
                context=body.context,
            )
            for i in body.relations
        ]
        result = self.client_batch_check(request_body, options)

        # filter out any errored responses and raise the first error
        errored_result_iterator = filter(_check_errored, result)
        errored_result_list = list(errored_result_iterator)
        if len(errored_result_list) > 0:
            raise errored_result_list[0].error

        # need to filter with the allowed response
        result_iterator = filter(_check_allowed, result)
        result_list = list(result_iterator)
        return [i.request.relation for i in result_list]

    def list_users(
        self,
        body: ClientListUsersRequest,
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Run list users request
        :param body - list user parameters
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        :param consistency(options) - The type of consistency preferred for the request
        """
        kwargs = options_to_kwargs(options)

        req_body = ListUsersRequest(
            authorization_model_id=self._get_authorization_model_id(options),
            object=body.object,
            relation=body.relation,
            user_filters=body.user_filters,
            contextual_tuples=body.contextual_tuples,
            context=body.context,
            consistency=self._get_consistency(options),
        )

        if body.contextual_tuples:
            req_body.contextual_tuples = convert_tuple_keys(body.contextual_tuples)

        api_response = self._api.list_users(body=req_body, **kwargs)

        return api_response

    #######################
    # Assertions
    #######################
    def read_assertions(
        self, options: dict[str, int | str | dict[str, int | str]] | None = None
    ):
        """
        Return the assertions
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """

        kwargs = options_to_kwargs(options)
        authorization_model_id = self._get_authorization_model_id(options)
        api_response = self._api.read_assertions(authorization_model_id, **kwargs)
        return api_response

    def write_assertions(
        self,
        body: list[ClientAssertion],
        options: dict[str, int | str | dict[str, int | str]] | None = None,
    ):
        """
        Upsert the assertions
        :param body - Write assertion request
        :param authorization_model_id(options) - Overrides the authorization model id in the configuration
        :param header(options) - Custom headers to send alongside the request
        :param retryParams(options) - Override the retry parameters for this request
        :param retryParams.maxRetry(options) - Override the max number of retries on each API request
        :param retryParams.minWaitInMs(options) - Override the minimum wait before a retry is initiated
        """
        kwargs = options_to_kwargs(options)
        authorization_model_id = self._get_authorization_model_id(options)

        def map_to_assertion(client_assertion: ClientAssertion) -> Assertion:
            return Assertion(
                TupleKey(
                    user=client_assertion.user,
                    relation=client_assertion.relation,
                    object=client_assertion.object,
                ),
                client_assertion.expectation,
            )

        api_request_body = WriteAssertionsRequest(
            [map_to_assertion(client_assertion) for client_assertion in body]
        )
        api_response = self._api.write_assertions(
            authorization_model_id, api_request_body, **kwargs
        )
        return api_response
