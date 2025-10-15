from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.models.check_error import CheckError


class ClientBatchCheckSingleResponse:
    def __init__(
        self,
        allowed: bool,
        request: ClientTuple,
        correlation_id: str,
        error: CheckError | None = None,
    ) -> None:
        self._allowed = allowed
        self._request = request
        self._correlation_id = correlation_id
        self._error = error

        # Set `allowed` to `false` if there was an error and allowed isn't otherwise set.
        if error is not None and allowed is None:
            self._allowed = False

    @property
    def allowed(self) -> bool:
        """
        Return allowed
        """
        return self._allowed

    @allowed.setter
    def allowed(self, allowed: bool) -> None:
        """
        Set allowed
        """
        self._allowed = allowed

    @property
    def request(self) -> ClientTuple:
        """
        Return request
        """
        return self._request

    @request.setter
    def request(self, request: ClientTuple) -> None:
        """
        Set request
        """
        self._request = request

    @property
    def correlation_id(self) -> str:
        """
        Return correlation_id
        """
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, correlation_id: str) -> None:
        """
        Set correlation_id
        """
        self._correlation_id = correlation_id

    @property
    def error(self) -> CheckError | None:
        """
        Return error
        """
        return self._error

    @error.setter
    def error(self, error: CheckError | None) -> None:
        """
        Set error
        """
        self._error = error
