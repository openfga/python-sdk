"""
Python SDK for OpenFGA

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

import pprint

from inspect import getfullargspec

from openfga_sdk.configuration import Configuration


class UserTypeFilter:
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
    openapi_types: dict[str, str] = {"type": "str", "relation": "str"}

    attribute_map: dict[str, str] = {"type": "type", "relation": "relation"}

    def __init__(self, type=None, relation=None, local_vars_configuration=None):
        """UserTypeFilter - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._type = None
        self._relation = None
        self.discriminator = None

        self.type = type
        if relation is not None:
            self.relation = relation

    @property
    def type(self):
        """Gets the type of this UserTypeFilter.


        :return: The type of this UserTypeFilter.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this UserTypeFilter.


        :param type: The type of this UserTypeFilter.
        :type type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")

        self._type = type

    @property
    def relation(self):
        """Gets the relation of this UserTypeFilter.


        :return: The relation of this UserTypeFilter.
        :rtype: str
        """
        return self._relation

    @relation.setter
    def relation(self, relation):
        """Sets the relation of this UserTypeFilter.


        :param relation: The relation of this UserTypeFilter.
        :type relation: str
        """

        self._relation = relation

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
        if not isinstance(other, UserTypeFilter):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UserTypeFilter):
            return True

        return self.to_dict() != other.to_dict()
