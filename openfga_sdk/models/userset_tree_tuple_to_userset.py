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


class UsersetTreeTupleToUserset:
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
    openapi_types: dict[str, str] = {"tupleset": "str", "computed": "list[Computed]"}

    attribute_map: dict[str, str] = {"tupleset": "tupleset", "computed": "computed"}

    def __init__(self, tupleset=None, computed=None, local_vars_configuration=None):
        """UsersetTreeTupleToUserset - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._tupleset = None
        self._computed = None
        self.discriminator = None

        self.tupleset = tupleset
        self.computed = computed

    @property
    def tupleset(self):
        """Gets the tupleset of this UsersetTreeTupleToUserset.


        :return: The tupleset of this UsersetTreeTupleToUserset.
        :rtype: str
        """
        return self._tupleset

    @tupleset.setter
    def tupleset(self, tupleset):
        """Sets the tupleset of this UsersetTreeTupleToUserset.


        :param tupleset: The tupleset of this UsersetTreeTupleToUserset.
        :type tupleset: str
        """
        if self.local_vars_configuration.client_side_validation and tupleset is None:
            raise ValueError("Invalid value for `tupleset`, must not be `None`")

        self._tupleset = tupleset

    @property
    def computed(self):
        """Gets the computed of this UsersetTreeTupleToUserset.


        :return: The computed of this UsersetTreeTupleToUserset.
        :rtype: list[Computed]
        """
        return self._computed

    @computed.setter
    def computed(self, computed):
        """Sets the computed of this UsersetTreeTupleToUserset.


        :param computed: The computed of this UsersetTreeTupleToUserset.
        :type computed: list[Computed]
        """
        if self.local_vars_configuration.client_side_validation and computed is None:
            raise ValueError("Invalid value for `computed`, must not be `None`")

        self._computed = computed

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
        if not isinstance(other, UsersetTreeTupleToUserset):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UsersetTreeTupleToUserset):
            return True

        return self.to_dict() != other.to_dict()
