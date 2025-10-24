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
        Return the writes as tuple keys (backward compatibility property)
        """
        return self.get_writes_tuple_keys()

    @property
    def deletes_tuple_keys(self) -> WriteRequestDeletes | None:
        """
        Return the deletes as tuple keys (backward compatibility property)
        """
        return self.get_deletes_tuple_keys()

    def get_writes_tuple_keys(
        self, on_duplicate: str | None = None
    ) -> WriteRequestWrites | None:
        """
        Return the writes as tuple keys with optional conflict handling

        Args:
            on_duplicate: Optional conflict resolution strategy for duplicate writes

        Returns:
            WriteRequestWrites object with tuple keys and optional on_duplicate setting
        """
        if self._writes is None:
            return None

        keys = convert_tuple_keys(self._writes)

        if keys is None:
            return None

        if on_duplicate is not None:
            return WriteRequestWrites(tuple_keys=keys, on_duplicate=on_duplicate)
        return WriteRequestWrites(tuple_keys=keys)

    def get_deletes_tuple_keys(
        self, on_missing: str | None = None
    ) -> WriteRequestDeletes | None:
        """
        Return the deletes as tuple keys with optional conflict handling

        Args:
            on_missing: Optional conflict resolution strategy for missing deletes

        Returns:
            WriteRequestDeletes object with tuple keys and optional on_missing setting
        """
        if self._deletes is None:
            return None

        keys = convert_tuple_keys(self._deletes)

        if keys is None:
            return None

        if on_missing is not None:
            return WriteRequestDeletes(tuple_keys=keys, on_missing=on_missing)
        return WriteRequestDeletes(tuple_keys=keys)
