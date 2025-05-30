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


class WriteAuthorizationModelRequest:
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
    openapi_types: dict[str, str] = {
        "type_definitions": "list[TypeDefinition]",
        "schema_version": "str",
        "conditions": "dict[str, Condition]",
    }

    attribute_map: dict[str, str] = {
        "type_definitions": "type_definitions",
        "schema_version": "schema_version",
        "conditions": "conditions",
    }

    def __init__(
        self,
        type_definitions=None,
        schema_version=None,
        conditions=None,
        local_vars_configuration=None,
    ):
        """WriteAuthorizationModelRequest - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._type_definitions = None
        self._schema_version = None
        self._conditions = None
        self.discriminator = None

        self.type_definitions = type_definitions
        self.schema_version = schema_version
        if conditions is not None:
            self.conditions = conditions

    @property
    def type_definitions(self):
        """Gets the type_definitions of this WriteAuthorizationModelRequest.


        :return: The type_definitions of this WriteAuthorizationModelRequest.
        :rtype: list[TypeDefinition]
        """
        return self._type_definitions

    @type_definitions.setter
    def type_definitions(self, type_definitions):
        """Sets the type_definitions of this WriteAuthorizationModelRequest.


        :param type_definitions: The type_definitions of this WriteAuthorizationModelRequest.
        :type type_definitions: list[TypeDefinition]
        """
        if (
            self.local_vars_configuration.client_side_validation
            and type_definitions is None
        ):
            raise ValueError("Invalid value for `type_definitions`, must not be `None`")

        self._type_definitions = type_definitions

    @property
    def schema_version(self):
        """Gets the schema_version of this WriteAuthorizationModelRequest.


        :return: The schema_version of this WriteAuthorizationModelRequest.
        :rtype: str
        """
        return self._schema_version

    @schema_version.setter
    def schema_version(self, schema_version):
        """Sets the schema_version of this WriteAuthorizationModelRequest.


        :param schema_version: The schema_version of this WriteAuthorizationModelRequest.
        :type schema_version: str
        """
        if (
            self.local_vars_configuration.client_side_validation
            and schema_version is None
        ):
            raise ValueError("Invalid value for `schema_version`, must not be `None`")

        self._schema_version = schema_version

    @property
    def conditions(self):
        """Gets the conditions of this WriteAuthorizationModelRequest.


        :return: The conditions of this WriteAuthorizationModelRequest.
        :rtype: dict[str, Condition]
        """
        return self._conditions

    @conditions.setter
    def conditions(self, conditions):
        """Sets the conditions of this WriteAuthorizationModelRequest.


        :param conditions: The conditions of this WriteAuthorizationModelRequest.
        :type conditions: dict[str, Condition]
        """

        self._conditions = conditions

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
        if not isinstance(other, WriteAuthorizationModelRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, WriteAuthorizationModelRequest):
            return True

        return self.to_dict() != other.to_dict()
