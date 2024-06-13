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


class ListUsersResponse:
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
    openapi_types = {"users": "list[User]", "excluded_users": "list[ObjectOrUserset]"}

    attribute_map = {"users": "users", "excluded_users": "excluded_users"}

    def __init__(self, users=None, excluded_users=None, local_vars_configuration=None):
        """ListUsersResponse - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._users = None
        self._excluded_users = None
        self.discriminator = None

        self.users = users
        self.excluded_users = excluded_users

    @property
    def users(self):
        """Gets the users of this ListUsersResponse.


        :return: The users of this ListUsersResponse.
        :rtype: list[User]
        """
        return self._users

    @users.setter
    def users(self, users):
        """Sets the users of this ListUsersResponse.


        :param users: The users of this ListUsersResponse.
        :type users: list[User]
        """
        if self.local_vars_configuration.client_side_validation and users is None:
            raise ValueError("Invalid value for `users`, must not be `None`")

        self._users = users

    @property
    def excluded_users(self):
        """Gets the excluded_users of this ListUsersResponse.


        :return: The excluded_users of this ListUsersResponse.
        :rtype: list[ObjectOrUserset]
        """
        return self._excluded_users

    @excluded_users.setter
    def excluded_users(self, excluded_users):
        """Sets the excluded_users of this ListUsersResponse.


        :param excluded_users: The excluded_users of this ListUsersResponse.
        :type excluded_users: list[ObjectOrUserset]
        """
        if (
            self.local_vars_configuration.client_side_validation
            and excluded_users is None
        ):
            raise ValueError("Invalid value for `excluded_users`, must not be `None`")

        self._excluded_users = excluded_users

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
        if not isinstance(other, ListUsersResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ListUsersResponse):
            return True

        return self.to_dict() != other.to_dict()