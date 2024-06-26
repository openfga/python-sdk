"""
   Python SDK for OpenFGA

   API version: 1.x
   Website: https://openfga.dev
   Documentation: https://openfga.dev/docs
   Support: https://openfga.dev/community
   License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

   NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

from openfga_sdk.client.models.write_single_response import ClientWriteSingleResponse


class ClientWriteResponse:
    """
    ClientWriteResponse returns the set of responses and their statuses
    """

    def __init__(
        self,
        writes: list[ClientWriteSingleResponse],
        deletes: list[ClientWriteSingleResponse],
    ):
        self._writes = writes
        self._deletes = deletes

    @property
    def writes(self):
        """
        Return the writes response
        """
        return self._writes

    @property
    def deletes(self):
        """
        Return the delete response
        """
        return self._deletes
