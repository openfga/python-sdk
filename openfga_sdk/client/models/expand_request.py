from openfga_sdk.client.models.tuple import ClientTuple


class ClientExpandRequest:
    """
    ClientExpandRequest encapsulates the parameters required to expand request
    """

    def __init__(
        self,
        relation: str,
        object: str,
        contextual_tuples: list[ClientTuple] | None = None,
    ) -> None:
        self._relation = relation
        self._object = object
        self._contextual_tuples = contextual_tuples

    @property
    def relation(self) -> str:
        """
        Return relation
        """
        return self._relation

    @relation.setter
    def relation(self, value: str) -> None:
        """
        Set relation
        """
        self._relation = value

    @property
    def object(self) -> str:
        """
        Return object
        """
        return self._object

    @object.setter
    def object(self, value: str) -> None:
        """
        Set object
        """
        self._object = value

    @property
    def contextual_tuples(self) -> list[ClientTuple] | None:
        """
        Return contextual_tuples
        """
        return self._contextual_tuples

    @contextual_tuples.setter
    def contextual_tuples(self, value: list[ClientTuple] | None) -> None:
        """
        Set contextual tuples
        """
        self._contextual_tuples = value
