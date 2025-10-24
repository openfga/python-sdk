from openfga_sdk.client.models.tuple import ClientTuple, convert_tuple_keys
from openfga_sdk.models.batch_check_item import BatchCheckItem
from openfga_sdk.models.check_request_tuple_key import CheckRequestTupleKey
from openfga_sdk.models.contextual_tuple_keys import ContextualTupleKeys


def construct_batch_item(check) -> BatchCheckItem:
    batch_item = BatchCheckItem(
        tuple_key=CheckRequestTupleKey(
            user=check.user,
            relation=check.relation,
            object=check.object,
        ),
        context=check.context,
        correlation_id=check.correlation_id,
    )

    if check.contextual_tuples:
        batch_item.contextual_tuples = ContextualTupleKeys(
            tuple_keys=convert_tuple_keys(check.contextual_tuples)
        )

    return batch_item


class ClientBatchCheckItem:
    def __init__(
        self,
        user: str,
        relation: str,
        object: str,
        correlation_id: str | None = None,
        contextual_tuples: list[ClientTuple] | None = None,
        context: dict[str, int | str] | None = None,
    ) -> None:
        self._user = user
        self._relation = relation
        self._object = object
        self._correlation_id = correlation_id
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
    def correlation_id(self) -> str | None:
        """
        Return correlation id
        """
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value: str | None) -> None:
        """
        Set correlation id
        """
        self._correlation_id = value

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
