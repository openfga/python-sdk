from openfga_sdk.client.models.tuple import ClientTuple, convert_tuple_keys
from openfga_sdk.models.write_request_deletes import WriteRequestDeletes
from openfga_sdk.models.write_request_writes import WriteRequestWrites


class ClientWriteRequest:
    """
    ClientWriteRequest encapsulates the parameters required to write
    """

    def __init__(
        self,
        writes: list[ClientTuple] | None = None,
        deletes: list[ClientTuple] | None = None,
    ) -> None:
        self._writes = writes
        self._deletes = deletes

    @property
    def writes(self) -> list[ClientTuple] | None:
        """
        Return writes
        """
        return self._writes

    @writes.setter
    def writes(self, value: list[ClientTuple] | None) -> None:
        """
        Set writes
        """
        self._writes = value

    @property
    def deletes(self) -> list[ClientTuple] | None:
        """
        Return deletes
        """
        return self._deletes

    @deletes.setter
    def deletes(self, value: list[ClientTuple] | None) -> None:
        """
        Set deletes
        """
        self._deletes = value

    @property
    def writes_tuple_keys(self) -> WriteRequestWrites | None:
        """
        Return the writes as tuple keys
        """
        if self._writes is None:
            return None

        keys = convert_tuple_keys(self._writes)

        if keys is None:
            return None

        return WriteRequestWrites(tuple_keys=keys)

    @property
    def deletes_tuple_keys(self) -> WriteRequestDeletes | None:
        """
        Return the delete as tuple keys
        """
        if self._deletes is None:
            return None

        keys = convert_tuple_keys(self._deletes)

        if keys is None:
            return None

        return WriteRequestDeletes(tuple_keys=keys)
