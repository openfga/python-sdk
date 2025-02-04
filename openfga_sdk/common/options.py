from dataclasses import asdict, dataclass, field

from openfga_sdk.common.cookies import HttpCookies
from openfga_sdk.common.headers import HttpHeaders
from openfga_sdk.configuration import RetryParams
from openfga_sdk.protocols import (
    HttpCookiesProtocol,
    HttpHeadersProtocol,
    MergeableDataclassMixin,
    RetryParamsProtocol,
    StoreRequestOptionsProtocol,
)


@dataclass
class StoreRequestOptionsBase(MergeableDataclassMixin, StoreRequestOptionsProtocol):
    store_id: str | None = None
    authorization_model_id: str | None = None
    headers: HttpHeadersProtocol = field(default_factory=lambda: HttpHeaders())
    cookies: HttpCookiesProtocol = field(default_factory=lambda: HttpCookies())
    retry_params: RetryParamsProtocol = field(default_factory=lambda: RetryParams())
    return_response: bool = False
    timeout: int | None = None


@dataclass
class CreateStoreRequestOptions(StoreRequestOptionsBase):
    pass


@dataclass
class ListStoresRequestOptions(StoreRequestOptionsBase):
    page_size: int | None = None
    continuation_token: str | None = None


@dataclass
class GetStoreRequestOptions(StoreRequestOptionsBase):
    pass


@dataclass
class DeleteStoreRequestOptions(StoreRequestOptionsBase):
    pass


@dataclass
class ReadAuthorizationModelsRequestOptions(StoreRequestOptionsBase):
    page_size: int | None = None
    continuation_token: str | None = None


@dataclass
class WriteAuthorizationModelRequestOptions(StoreRequestOptionsBase):
    store_id: str | None = None


@dataclass
class ReadAuthorizationModelRequestOptions(StoreRequestOptionsBase):
    pass


@dataclass
class ReadLatestAuthorizationModelRequestOptions(StoreRequestOptionsBase):
    pass


@dataclass
class ReadChangesRequestOptions(StoreRequestOptionsBase):
    page_size: int | None = None
    continuation_token: str | None = None


@dataclass
class ReadRequestOptions(StoreRequestOptionsBase):
    page_size: int | None = None
    continuation_token: str | None = None
    consistency: str | None = None


@dataclass
class WriteTransactionOptions:
    disabled: bool = False
    max_per_chunk: int = 1
    max_parallel_requests: int = 10


@dataclass
class BatchCheckRequestOptions(StoreRequestOptionsBase):
    max_batch_size: int = 50
    max_parallel_requests: int = 10
    consistency: str | None = None


@dataclass
class WriteRequestOptions(StoreRequestOptionsBase):
    transaction: WriteTransactionOptions = field(
        default_factory=WriteTransactionOptions
    )


@dataclass
class CheckRequestOptions(StoreRequestOptionsBase):
    consistency: str | None = None


@dataclass
class ExpandRequestOptions(StoreRequestOptionsBase):
    consistency: str | None = None


@dataclass
class ListObjectsRequestOptions(StoreRequestOptionsBase):
    consistency: str | None = None


@dataclass
class ListRelationsRequestOptions(StoreRequestOptionsBase):
    pass


@dataclass
class ListUsersRequestOptions(StoreRequestOptionsBase):
    consistency: str | None = None


@dataclass
class ReadAssertionsRequestOptions(StoreRequestOptionsBase):
    pass


@dataclass
class WriteAssertionsRequestOptions(StoreRequestOptionsBase):
    pass
