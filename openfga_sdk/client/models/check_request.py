from openfga_sdk.client.models.tuple import ClientTuple


class ClientCheckRequest:
    """
    ClientCheckRequest encapsulates the parameters for check request
    """

    def __init__(
        self,
        user: str,
        relation: str,
        object: str,
        contextual_tuples: list[ClientTuple] | None = None,
        context: dict[str, int | str] | None = None,
    ) -> None:
        self._user = user
        self._relation = relation
        self._object = object
        self._contextual_tuples = None
        self._context = context

        if contextual_tuples:
            self._contextual_tuples = contextual_tuples

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
        Return contextual tuples
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


def construct_check_request(
    user: str,
    relation: str,
    object: str,
    contextual_tuples: list[ClientTuple] | None = None,
    context: dict[str, int | str] | None = None,
) -> ClientCheckRequest:
    """
    helper function to construct the check request body
    """
    return ClientCheckRequest(user, relation, object, contextual_tuples, context)
