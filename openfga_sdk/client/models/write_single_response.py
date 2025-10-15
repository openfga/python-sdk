from openfga_sdk.client.models.tuple import ClientTuple


class ClientWriteSingleResponse:
    """
    ClientWriteSingleResponse encapsulates the response of a single write
    """

    def __init__(
        self,
        tuple_key: ClientTuple,
        success: bool,
        error: Exception | None = None,
    ) -> None:
        self._tuple_key = tuple_key
        self._success = success
        self._error = error

    def __eq__(self, other):
        return (
            self.tuple_key == other.tuple_key
            and self.success == other.success
            and self.error == other.error
        )

    @property
    def tuple_key(self) -> ClientTuple:
        """
        Return tuple_key
        """
        return self._tuple_key

    @tuple_key.setter
    def tuple_key(self, value: ClientTuple) -> None:
        """
        Set tuple_key
        """
        self._tuple_key = value

    @property
    def success(self) -> bool:
        """
        Return success
        """
        return self._success

    @success.setter
    def success(self, value: bool) -> None:
        """
        Set success
        """
        self._success = value

    @property
    def error(self) -> Exception | None:
        """
        Return error
        """
        return self._error

    @error.setter
    def error(self, value: Exception | None) -> None:
        """
        Set error
        """
        self._error = value


def construct_write_single_response(
    tuple_key: ClientTuple,
    success: bool,
    error: Exception | None = None,
) -> ClientWriteSingleResponse:
    """
    Helper function to return a single write response
    """
    return ClientWriteSingleResponse(tuple_key, success, error)
