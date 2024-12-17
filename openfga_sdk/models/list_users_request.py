"""
   Python SDK for OpenFGA

   API version: 1.x
   Website: https://openfga.dev
   Documentation: https://openfga.dev/docs
   Support: https://openfga.dev/community
   License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

   NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint

from openfga_sdk.configuration import Configuration


class ListUsersRequest:
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        "authorization_model_id": "str",
        "object": "FgaObject",
        "relation": "str",
        "user_filters": "list[UserTypeFilter]",
        "contextual_tuples": "list[TupleKey]",
        "context": "object",
        "consistency": "ConsistencyPreference",
    }

    attribute_map = {
        "authorization_model_id": "authorization_model_id",
        "object": "object",
        "relation": "relation",
        "user_filters": "user_filters",
        "contextual_tuples": "contextual_tuples",
        "context": "context",
        "consistency": "consistency",
    }

    def __init__(
        self,
        authorization_model_id=None,
        object=None,
        relation=None,
        user_filters=None,
        contextual_tuples=None,
        context=None,
        consistency=None,
        local_vars_configuration=None,
    ):
        """ListUsersRequest - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._authorization_model_id = None
        self._object = None
        self._relation = None
        self._user_filters = None
        self._contextual_tuples = None
        self._context = None
        self._consistency = None
        self.discriminator = None

        if authorization_model_id is not None:
            self.authorization_model_id = authorization_model_id
        self.object = object
        self.relation = relation
        self.user_filters = user_filters
        if contextual_tuples is not None:
            self.contextual_tuples = contextual_tuples
        if context is not None:
            self.context = context
        if consistency is not None:
            self.consistency = consistency

    @property
    def authorization_model_id(self):
        """Gets the authorization_model_id of this ListUsersRequest.


        :return: The authorization_model_id of this ListUsersRequest.
        :rtype: str
        """
        return self._authorization_model_id

    @authorization_model_id.setter
    def authorization_model_id(self, authorization_model_id):
        """Sets the authorization_model_id of this ListUsersRequest.


        :param authorization_model_id: The authorization_model_id of this ListUsersRequest.
        :type authorization_model_id: str
        """

        self._authorization_model_id = authorization_model_id

    @property
    def object(self):
        """Gets the object of this ListUsersRequest.


        :return: The object of this ListUsersRequest.
        :rtype: FgaObject
        """
        return self._object

    @object.setter
    def object(self, object):
        """Sets the object of this ListUsersRequest.


        :param object: The object of this ListUsersRequest.
        :type object: FgaObject
        """
        if self.local_vars_configuration.client_side_validation and object is None:
            raise ValueError("Invalid value for `object`, must not be `None`")

        self._object = object

    @property
    def relation(self):
        """Gets the relation of this ListUsersRequest.


        :return: The relation of this ListUsersRequest.
        :rtype: str
        """
        return self._relation

    @relation.setter
    def relation(self, relation):
        """Sets the relation of this ListUsersRequest.


        :param relation: The relation of this ListUsersRequest.
        :type relation: str
        """
        if self.local_vars_configuration.client_side_validation and relation is None:
            raise ValueError("Invalid value for `relation`, must not be `None`")

        self._relation = relation

    @property
    def user_filters(self):
        """Gets the user_filters of this ListUsersRequest.

        The type of results returned. Only accepts exactly one value.

        :return: The user_filters of this ListUsersRequest.
        :rtype: list[UserTypeFilter]
        """
        return self._user_filters

    @user_filters.setter
    def user_filters(self, user_filters):
        """Sets the user_filters of this ListUsersRequest.

        The type of results returned. Only accepts exactly one value.

        :param user_filters: The user_filters of this ListUsersRequest.
        :type user_filters: list[UserTypeFilter]
        """
        if (
            self.local_vars_configuration.client_side_validation
            and user_filters is None
        ):
            raise ValueError("Invalid value for `user_filters`, must not be `None`")

        self._user_filters = user_filters

    @property
    def contextual_tuples(self):
        """Gets the contextual_tuples of this ListUsersRequest.


        :return: The contextual_tuples of this ListUsersRequest.
        :rtype: list[TupleKey]
        """
        return self._contextual_tuples

    @contextual_tuples.setter
    def contextual_tuples(self, contextual_tuples):
        """Sets the contextual_tuples of this ListUsersRequest.


        :param contextual_tuples: The contextual_tuples of this ListUsersRequest.
        :type contextual_tuples: list[TupleKey]
        """

        self._contextual_tuples = contextual_tuples

    @property
    def context(self):
        """Gets the context of this ListUsersRequest.

        Additional request context that will be used to evaluate any ABAC conditions encountered in the query evaluation.

        :return: The context of this ListUsersRequest.
        :rtype: object
        """
        return self._context

    @context.setter
    def context(self, context):
        """Sets the context of this ListUsersRequest.

        Additional request context that will be used to evaluate any ABAC conditions encountered in the query evaluation.

        :param context: The context of this ListUsersRequest.
        :type context: object
        """

        self._context = context

    @property
    def consistency(self):
        """Gets the consistency of this ListUsersRequest.


        :return: The consistency of this ListUsersRequest.
        :rtype: ConsistencyPreference
        """
        return self._consistency

    @consistency.setter
    def consistency(self, consistency):
        """Sets the consistency of this ListUsersRequest.


        :param consistency: The consistency of this ListUsersRequest.
        :type consistency: ConsistencyPreference
        """

        self._consistency = consistency

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in self.openapi_types.items():
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(lambda x: convert(x), value))
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(lambda item: (item[0], convert(item[1])), value.items())
                )
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ListUsersRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ListUsersRequest):
            return True

        return self.to_dict() != other.to_dict()
