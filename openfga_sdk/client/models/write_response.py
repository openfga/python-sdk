from openfga_sdk.client.models.write_single_response import ClientWriteSingleResponse


class ClientWriteResponse:
    """
    ClientWriteResponse returns the set of responses and their statuses
    """

    def __init__(
        self,
        writes: list[ClientWriteSingleResponse] | None = None,
        deletes: list[ClientWriteSingleResponse] | None = None,
    ) -> None:
        self._writes = writes
        self._deletes = deletes

    @property
    def writes(self) -> list[ClientWriteSingleResponse] | None:
        """
        Return the writes response
        """
        return self._writes

    @writes.setter
    def writes(self, value: list[ClientWriteSingleResponse] | None) -> None:
        """
        Set the writes response
        """
        self._writes = value

    @property
    def deletes(self):
        """
        Return the delete response
        """
        return self._deletes

    @deletes.setter
    def deletes(self, value: list[ClientWriteSingleResponse] | None) -> None:
        """
        Set the delete response
        """
        self._deletes = value
