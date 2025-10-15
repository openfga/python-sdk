from openfga_sdk.models.relationship_condition import RelationshipCondition
from openfga_sdk.models.tuple_key import TupleKey


class ClientTuple:
    """
    ClientTuple encapsulates the client tuple
    """

    def __init__(
        self,
        user: str,
        relation: str,
        object: str,
        condition: RelationshipCondition | None = None,
    ) -> None:
        self._user = user
        self._relation = relation
        self._object = object
        self._condition = condition

    def __eq__(self, other) -> bool:
        if (
            self.user == other.user
            and self.relation == other.relation
            and self.object == other.object
            and self.condition == other.condition
        ):
            return True

        return False

    @property
    def user(self) -> str:
        return self._user

    @user.setter
    def user(self, value: str) -> None:
        self._user = value

    @property
    def relation(self) -> str:
        return self._relation

    @relation.setter
    def relation(self, value: str) -> None:
        self._relation = value

    @property
    def object(self) -> str:
        return self._object

    @object.setter
    def object(self, value: str) -> None:
        self._object = value

    @property
    def condition(self) -> RelationshipCondition | None:
        return self._condition

    @condition.setter
    def condition(self, value: RelationshipCondition | None) -> None:
        self._condition = value

    @property
    def tuple_key(self) -> TupleKey:
        """
        Return the ClientTuple as TupleKey
        """
        return TupleKey(
            object=self.object,
            relation=self.relation,
            user=self.user,
            condition=self.condition,
        )


def convert_tuple_keys(lists: list[ClientTuple]) -> list[TupleKey] | None:
    """
    Return the items as tuple_keys
    """
    if lists is None:
        return None

    return list(map(lambda item: item.tuple_key, lists))
