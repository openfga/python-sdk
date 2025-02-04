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


class Status:
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
        "code": "int",
        "message": "str",
        "details": "list[Any]",
    }

    attribute_map: dict[str, str] = {
        "code": "code",
        "message": "message",
        "details": "details",
    }

    def __init__(
        self, code=None, message=None, details=None, local_vars_configuration=None
    ):
        """Status - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._code = None
        self._message = None
        self._details = None
        self.discriminator = None

        if code is not None:
            self.code = code
        if message is not None:
            self.message = message
        if details is not None:
            self.details = details

    @property
    def code(self):
        """Gets the code of this Status.


        :return: The code of this Status.
        :rtype: int
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this Status.


        :param code: The code of this Status.
        :type code: int
        """

        self._code = code

    @property
    def message(self):
        """Gets the message of this Status.


        :return: The message of this Status.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this Status.


        :param message: The message of this Status.
        :type message: str
        """

        self._message = message

    @property
    def details(self):
        """Gets the details of this Status.


        :return: The details of this Status.
        :rtype: list[Any]
        """
        return self._details

    @details.setter
    def details(self, details):
        """Sets the details of this Status.


        :param details: The details of this Status.
        :type details: list[Any]
        """

        self._details = details

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
        if not isinstance(other, Status):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Status):
            return True

        return self.to_dict() != other.to_dict()
