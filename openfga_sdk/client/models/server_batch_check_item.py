from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.models.batch_check_item import BatchCheckItem
from openfga_sdk.models.check_request_tuple_key import CheckRequestTupleKey

class ServerBatchCheckItem:
    def __init__(
        self,
        user: str,
        relation: str,
        object: str,
        correlation_id: str,
        contextual_tuples: list[ClientTuple] = None,
        context: object = None,
    ):
        self._user = user
        self._relation = relation
        self._object = object
        self._correlation_id = correlation_id
        self._contextual_tuples = None
        if contextual_tuples:
            self._contextual_tuples = contextual_tuples
        self._context = context


    @property
    def user(self):
        """
        Return user
        """
        return self._user

    @property
    def relation(self):
        """
        Return relation
        """
        return self._relation

    @property
    def object(self):
        """
        Return object
        """
        return self._object
        

    @property
    def contextual_tuples(self):
        """
        Return contextual tuples
        """
        return self._contextual_tuples

    @property
    def context(self):
        """
        Return context
        """
        return self._context
    
    @property
    def correlation_id(self):
        """
        """
        return self._correlation_id


    @user.setter
    def user(self, value):
        """
        Set user
        """
        self._user = value

    @relation.setter
    def relation(self, value):
        """
        Set relation
        """
        self._relation = value

    @object.setter
    def object(self, value):
        """
        Set object
        """
        self._object = value

    @contextual_tuples.setter
    def contextual_tuples(self, value):
        """
        Set contextual tuples
        """
        self._contextual_tuples = value

    @context.setter
    def context(self, value):
        """
        Set context
        """
        self._context = value
        
    @correlation_id.setter
    def correlation_id(self, value):
        """
        """
        self._correlation_id = value
