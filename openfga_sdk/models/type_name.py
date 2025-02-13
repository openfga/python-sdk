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


class TypeName:
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    allowed enum values
    """
    UNSPECIFIED = "TYPE_NAME_UNSPECIFIED"
    ANY = "TYPE_NAME_ANY"
    BOOL = "TYPE_NAME_BOOL"
    STRING = "TYPE_NAME_STRING"
    INT = "TYPE_NAME_INT"
    UINT = "TYPE_NAME_UINT"
    DOUBLE = "TYPE_NAME_DOUBLE"
    DURATION = "TYPE_NAME_DURATION"
    TIMESTAMP = "TYPE_NAME_TIMESTAMP"
    MAP = "TYPE_NAME_MAP"
    LIST = "TYPE_NAME_LIST"
    IPADDRESS = "TYPE_NAME_IPADDRESS"

    allowable_values = [
        UNSPECIFIED,
        ANY,
        BOOL,
        STRING,
        INT,
        UINT,
        DOUBLE,
        DURATION,
        TIMESTAMP,
        MAP,
        LIST,
        IPADDRESS,
    ]

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types: dict[str, str] = {}

    attribute_map: dict[str, str] = {}

    def __init__(self, local_vars_configuration=None):
        """TypeName - a model defined in OpenAPI"""

        self.local_vars_configuration: dict = local_vars_configuration or {}
        self.discriminator = None

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
        if not isinstance(other, TypeName):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TypeName):
            return True

        return self.to_dict() != other.to_dict()
