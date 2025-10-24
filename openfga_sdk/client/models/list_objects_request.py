from openfga_sdk.client.models.tuple import ClientTuple


class ClientListObjectsRequest:
    """
    ClientListObjectsRequest encapsulates the parameters required for list objects
    """

    def __init__(
        self,
        user: str,
        relation: str,
        type: str,
        contextual_tuples: list[ClientTuple] | None = None,
        context: object | None = None,
    ) -> None:
        self._user = user
        self._relation = relation
        self._type = type
        self._contextual_tuples = contextual_tuples
        self._context = context

    @property
    def user(self) -> str:
        """
        Return user
        """
        return self._user

    @user.setter
    def user(self, value: str) -> None:
        """
        Set user
        """
        self._user = value

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
    def type(self) -> str:
        """
        Return type
        """
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        """
        Set type
        """
        self._type = value

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

    @property
    def context(self) -> object | None:
        """
        Return context
        """
        return self._context

    @context.setter
    def context(self, value: object | None) -> None:
        """
        Set context
        """
        self._context = value
