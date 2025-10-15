from openfga_sdk.client.models.tuple import ClientTuple


class ClientListRelationsRequest:
    """
    ClientListRelationsRequest encapsulates the parameters required for list all relations user have with object
    """

    def __init__(
        self,
        user: str,
        relations: list[str],
        object: str,
        contextual_tuples: list[ClientTuple] | None = None,
        context: dict[str, int | str] | None = None,
    ) -> None:
        self._user = user
        self._relations = relations
        self._object = object
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
    def relations(self) -> list[str]:
        """
        Return relations
        """
        return self._relations

    @relations.setter
    def relations(self, value: list[str]) -> None:
        """
        Set relations
        """
        self._relations = value

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

    @property
    def context(self) -> dict[str, int | str] | None:
        """
        Return context
        """
        return self._context

    @context.setter
    def context(self, value: dict[str, int | str] | None) -> None:
        """
        Set context
        """
        self._context = value
