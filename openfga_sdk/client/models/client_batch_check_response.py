from openfga_sdk.client.models.check_request import ClientCheckRequest
from openfga_sdk.models.check_response import CheckResponse


class ClientBatchCheckClientResponse:
    """
    ClientBatchCheckClientResponse encapsulates the response for a single batch check
    """

    def __init__(
        self,
        allowed: bool,
        request: ClientCheckRequest,
        response: CheckResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self._allowed = allowed
        self._request = request
        self._response = response
        self._error = error

    @property
    def allowed(self) -> bool:
        """
        Return whether request is allowed
        """
        return self._allowed

    @allowed.setter
    def allowed(self, value: bool) -> None:
        """
        Set whether request is allowed
        """
        self._allowed = value

    @property
    def request(self) -> ClientCheckRequest:
        """
        Return original request
        """
        return self._request

    @request.setter
    def request(self, value: ClientCheckRequest) -> None:
        """
        Set original request
        """
        self._request = value

    @property
    def response(self) -> CheckResponse | None:
        """
        Return original request
        """
        return self._response

    @response.setter
    def response(self, value: CheckResponse | None) -> None:
        """
        Set original request
        """
        self._response = value

    @property
    def error(self) -> Exception | None:
        """
        Return error associated with batch request (if any)
        """
        return self._error

    @error.setter
    def error(self, value: Exception | None) -> None:
        """
        Set error associated with batch request
        """
        self._error = value

    def __str__(self):
        """
        Return the class string
        """
        return f"allowed {self._allowed} request {self._request} error {self._error}"
