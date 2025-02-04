"""
Python SDK for OpenFGA

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

import os

from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.credentials import CredentialConfiguration
from openfga_sdk.exceptions import FgaValidationException
from openfga_sdk.validation import is_well_formed_ulid_string


class ClientConfiguration(Configuration):
    """
    OpenFGA client configuration
    """

    _authorization_model_id: str | None = None

    def __init__(
        self,
        api_url: str,
        store_id: str | None = None,
        credentials: CredentialConfiguration | None = None,
        retry_params: RetryParams | None = None,
        authorization_model_id: str | None = None,
        ssl_ca_cert: str | bytes | os.PathLike | None = None,
        timeout_millisec: int = 300000,
    ):
        super().__init__(
            api_url=api_url,
            store_id=store_id,
            credentials=credentials,
            retry_params=retry_params,
            ssl_ca_cert=ssl_ca_cert,
            timeout_millisec=timeout_millisec,
        )

        self._authorization_model_id = authorization_model_id

    def is_valid(self):
        super().is_valid()

        if (
            self.authorization_model_id is not None
            and self.authorization_model_id != ""
            and is_well_formed_ulid_string(self.authorization_model_id) is False
        ):
            raise FgaValidationException(
                f"authorization_model_id ('{self.authorization_model_id}') is not in a valid ulid format"
            )

    @property
    def authorization_model_id(self) -> str | None:
        return self._authorization_model_id

    @authorization_model_id.setter
    def authorization_model_id(self, value: str | None) -> None:
        self._authorization_model_id = value
