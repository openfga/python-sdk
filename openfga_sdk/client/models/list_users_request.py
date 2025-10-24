from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.models.fga_object import FgaObject
from openfga_sdk.models.user_type_filter import UserTypeFilter


class ClientListUsersRequest:
    """
    ClientListUsersRequest encapsulates the parameters required for list users
    """

    def __init__(
        self,
        object: FgaObject | None = None,
        relation: str | None = None,
        user_filters: list[UserTypeFilter] | None = None,
        contextual_tuples: list[ClientTuple] | None = None,
        context: dict[str, int | str] | None = None,
    ) -> None:
        self._object = object
        self._relation = relation
        self._user_filters = user_filters
        self._contextual_tuples = contextual_tuples
        self._context = context

    @property
    def object(self) -> FgaObject | None:
        """
        Gets the object of this ClientListUsersRequest.

        :return: The object of this ClientListUsersRequest.
        :rtype: str
        """
        return self._object

    @object.setter
    def object(self, object: FgaObject | None) -> None:
        """
        Sets the object of this ClientListUsersRequest.

        :param object: The object of this ClientListUsersRequest.
        :type object: str
        """
        self._object = object

    @property
    def relation(self) -> str | None:
        """
        Gets the relation of this ClientListUsersRequest.

        :return: The relation of this ClientListUsersRequest.
        :rtype: str
        """
        return self._relation

    @relation.setter
    def relation(self, relation: str | None) -> None:
        """
        Sets the relation of this ClientListUsersRequest.

        :param relation: The relation of this ClientListUsersRequest.
        :type relation: str
        """
        self._relation = relation

    @property
    def user_filters(self) -> list[UserTypeFilter] | None:
        """
        Gets the user_filters of this ClientListUsersRequest.

        :return: The user_filters of this ClientListUsersRequest.
        :rtype: str
        """
        return self._user_filters

    @user_filters.setter
    def user_filters(self, user_filters: list[UserTypeFilter] | None) -> None:
        """
        Sets the user_filters of this ClientListUsersRequest.

        :param user_filters: The user_filters of this ClientListUsersRequest.
        :type user_filters: str
        """
        self._user_filters = user_filters

    @property
    def contextual_tuples(self) -> list[ClientTuple] | None:
        """
        Gets the contextual_tuples of this ClientListUsersRequest.

        :return: The contextual_tuples of this ClientListUsersRequest.
        :rtype: ContextualTupleKeys
        """
        return self._contextual_tuples

    @contextual_tuples.setter
    def contextual_tuples(self, contextual_tuples: list[ClientTuple] | None) -> None:
        """
        Sets the contextual_tuples of this ClientListUsersRequest.

        :param contextual_tuples: The contextual_tuples of this ClientListUsersRequest.
        :type contextual_tuples: ContextualTupleKeys
        """
        self._contextual_tuples = contextual_tuples

    @property
    def context(self) -> dict[str, int | str] | None:
        """
        Gets the context of this ClientListUsersRequest.

        Additional request context that will be used to evaluate any ABAC conditions encountered in the query evaluation.
        """
        return self._context

    @context.setter
    def context(self, context: dict[str, int | str] | None) -> None:
        """
        Sets the context of this ClientListUsersRequest.

        Additional request context that will be used to evaluate any ABAC conditions encountered in the query evaluation.
        """
        self._context = context
