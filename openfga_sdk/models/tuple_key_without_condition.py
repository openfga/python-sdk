# coding: utf-8

"""
   Python SDK for OpenFGA

   API version: 0.1
   Website: https://openfga.dev
   Documentation: https://openfga.dev/docs
   Support: https://discord.gg/8naAwJfWN6
   License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

   NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from openfga_sdk.configuration import Configuration


class TupleKeyWithoutCondition(object):
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
        'user': 'str',
        'relation': 'str',
        'object': 'str'
    }

    attribute_map = {
        'user': 'user',
        'relation': 'relation',
        'object': 'object'
    }

    def __init__(self, user=None, relation=None, object=None, local_vars_configuration=None):  # noqa: E501
        """TupleKeyWithoutCondition - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._user = None
        self._relation = None
        self._object = None
        self.discriminator = None

        self.user = user
        self.relation = relation
        self.object = object

    @property
    def user(self):
        """Gets the user of this TupleKeyWithoutCondition.  # noqa: E501


        :return: The user of this TupleKeyWithoutCondition.  # noqa: E501
        :rtype: str
        """
        return self._user

    @user.setter
    def user(self, user):
        """Sets the user of this TupleKeyWithoutCondition.


        :param user: The user of this TupleKeyWithoutCondition.  # noqa: E501
        :type user: str
        """
        if self.local_vars_configuration.client_side_validation and user is None:  # noqa: E501
            raise ValueError("Invalid value for `user`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                user is not None and len(user) > 512):
            raise ValueError("Invalid value for `user`, length must be less than or equal to `512`")  # noqa: E501

        self._user = user

    @property
    def relation(self):
        """Gets the relation of this TupleKeyWithoutCondition.  # noqa: E501


        :return: The relation of this TupleKeyWithoutCondition.  # noqa: E501
        :rtype: str
        """
        return self._relation

    @relation.setter
    def relation(self, relation):
        """Sets the relation of this TupleKeyWithoutCondition.


        :param relation: The relation of this TupleKeyWithoutCondition.  # noqa: E501
        :type relation: str
        """
        if self.local_vars_configuration.client_side_validation and relation is None:  # noqa: E501
            raise ValueError("Invalid value for `relation`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                relation is not None and len(relation) > 50):
            raise ValueError("Invalid value for `relation`, length must be less than or equal to `50`")  # noqa: E501

        self._relation = relation

    @property
    def object(self):
        """Gets the object of this TupleKeyWithoutCondition.  # noqa: E501


        :return: The object of this TupleKeyWithoutCondition.  # noqa: E501
        :rtype: str
        """
        return self._object

    @object.setter
    def object(self, object):
        """Sets the object of this TupleKeyWithoutCondition.


        :param object: The object of this TupleKeyWithoutCondition.  # noqa: E501
        :type object: str
        """
        if self.local_vars_configuration.client_side_validation and object is None:  # noqa: E501
            raise ValueError("Invalid value for `object`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                object is not None and len(object) > 256):
            raise ValueError("Invalid value for `object`, length must be less than or equal to `256`")  # noqa: E501

        self._object = object

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

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
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
        if not isinstance(other, TupleKeyWithoutCondition):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TupleKeyWithoutCondition):
            return True

        return self.to_dict() != other.to_dict()
