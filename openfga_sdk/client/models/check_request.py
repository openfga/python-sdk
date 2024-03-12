"""
   Python SDK for OpenFGA

   API version: 0.1
   Website: https://openfga.dev
   Documentation: https://openfga.dev/docs
   Support: https://openfga.dev/community
   License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

   NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

from openfga_sdk.client.models.tuple import ClientTuple


def construct_check_request(
    user: str,
    relation: str,
    object: str,
    contextual_tuples: list[ClientTuple] = None,
    context: object = None,
):
    """
    helper function to construct the check request body
    """
    return ClientCheckRequest(user, relation, object, contextual_tuples, context)


class ClientCheckRequest:
    """
    ClientCheckRequest encapsulates the parameters for check request
    """

    def __init__(
        self,
        user: str,
        relation: str,
        object: str,
        contextual_tuples: list[ClientTuple] = None,
        context: object = None,
    ):
        self._user = user
        self._relation = relation
        self._object = object
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
