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


class WriteRequestWrites:
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
    openapi_types: dict[str, str] = {"tuple_keys": "list[TupleKey]"}

    attribute_map: dict[str, str] = {"tuple_keys": "tuple_keys"}

    def __init__(self, tuple_keys=None, local_vars_configuration=None):
        """WriteRequestWrites - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._tuple_keys = None
        self.discriminator = None

        self.tuple_keys = tuple_keys

    @property
    def tuple_keys(self):
        """Gets the tuple_keys of this WriteRequestWrites.


        :return: The tuple_keys of this WriteRequestWrites.
        :rtype: list[TupleKey]
        """
        return self._tuple_keys

    @tuple_keys.setter
    def tuple_keys(self, tuple_keys):
        """Sets the tuple_keys of this WriteRequestWrites.


        :param tuple_keys: The tuple_keys of this WriteRequestWrites.
        :type tuple_keys: list[TupleKey]
        """
        if self.local_vars_configuration.client_side_validation and tuple_keys is None:
            raise ValueError("Invalid value for `tuple_keys`, must not be `None`")

        self._tuple_keys = tuple_keys

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
        if not isinstance(other, WriteRequestWrites):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, WriteRequestWrites):
            return True

        return self.to_dict() != other.to_dict()
