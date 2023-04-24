from openfga_sdk.client.client_tuple_key import ClientTupleKey


class ClientCheckRequest(ClientTupleKey):

    def __init__(self, object=None, relation=None, user=None, local_vars_configuration=None):
        super().__init__(object, relation, user, local_vars_configuration)
        self._contextual_tuples = None

    @property
    def contextual_tuples(self):
        """Gets the contextual_tuples of this CheckRequest.  # noqa: E501


        :return: The contextual_tuples of this CheckRequest.  # noqa: E501
        :rtype: List[ClientTupleKey]
        """
        return self._contextual_tuples

    @contextual_tuples.setter
    def contextual_tuples(self, contextual_tuples):
        """Sets the contextual_tuples of this CheckRequest.


        :param contextual_tuples: The contextual_tuples of this CheckRequest.  # noqa: E501
        :type contextual_tuples: List[ClientTupleKey]
        """

        self._contextual_tuples = contextual_tuples


class ClientRequestOptions(object):
    pass


class ClientRequestOptionsWithAuthZModelId(ClientRequestOptions):
    def __init__(self, authorization_model_id):
        self._authorization_model_id = authorization_model_id

    @property
    def authorization_model_id(self):
        """Gets the authorization_model_id.  # noqa: E501


        :return: The authorization_model_id.  # noqa: E501
        :rtype: str
        """
        return self._authorization_model_id

    @authorization_model_id.setter
    def authorization_model_id(self, authorization_model_id):
        """Sets the authorization_model_id.


        :param authorization_model_id: The authorization_model_id.  # noqa: E501
        :type authorization_model_id: str
        """

        self._authorization_model_id = authorization_model_id


class ClientCheckRequestOpts(ClientRequestOptionsWithAuthZModelId):
    pass
