"""
   Python SDK for OpenFGA

   API version: 1.x
   Website: https://openfga.dev
   Documentation: https://openfga.dev/docs
   Support: https://openfga.dev/community
   License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

   NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

from unittest import IsolatedAsyncioTestCase

import openfga_sdk
from openfga_sdk.credentials import CredentialConfiguration, Credentials


class TestCredentials(IsolatedAsyncioTestCase):
    """Credentials unit test"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_bad_method(self):
        """
        Check whether assertion is raised if method is not allowed
        """
        credential = Credentials("bad")
        with self.assertRaises(openfga_sdk.ApiValueError):
            credential.validate_credentials_config()

    def test_method_none(self):
        """
        Test credential with method none is valid
        """
        credential = Credentials("none")
        credential.validate_credentials_config()
        self.assertEqual(credential.method, "none")

    def test_method_default(self):
        """
        Test credential with not method is default to none
        """
        credential = Credentials()
        credential.validate_credentials_config()
        self.assertEqual(credential.method, "none")

    def test_configuration_api_token(self):
        """
        Test credential with method api_token and appropriate configuration is valid
        """
        credential = Credentials(
            method="api_token",
            configuration=CredentialConfiguration(api_token="ABCDEFG"),
        )
        credential.validate_credentials_config()
        self.assertEqual(credential.method, "api_token")
        self.assertEqual(credential.configuration.api_token, "ABCDEFG")

    def test_configuration_api_token_missing_configuration(self):
        """
        Test credential with method api_token but configuration is not specified
        """
        credential = Credentials(method="api_token")
        with self.assertRaises(openfga_sdk.ApiValueError):
            credential.validate_credentials_config()

    def test_configuration_api_token_missing_token(self):
        """
        Test credential with method api_token but configuration is missing token
        """
        credential = Credentials(
            method="api_token", configuration=CredentialConfiguration()
        )
        with self.assertRaises(openfga_sdk.ApiValueError):
            credential.validate_credentials_config()

    def test_configuration_api_token_empty_token(self):
        """
        Test credential with method api_token but configuration has empty token
        """
        credential = Credentials(
            method="api_token", configuration=CredentialConfiguration(api_token="")
        )
        with self.assertRaises(openfga_sdk.ApiValueError):
            credential.validate_credentials_config()

    def test_configuration_client_credentials(self):
        """
        Test credential with method client_credentials and appropriate configuration is valid
        """
        credential = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        credential.validate_credentials_config()
        self.assertEqual(credential.method, "client_credentials")

    def test_configuration_client_credentials_missing_config(self):
        """
        Test credential with method client_credentials and configuration is missing
        """
        credential = Credentials(method="client_credentials")
        with self.assertRaises(openfga_sdk.ApiValueError):
            credential.validate_credentials_config()

    def test_configuration_client_credentials_missing_client_id(self):
        """
        Test credential with method client_credentials and configuration is missing client id
        """
        credential = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        with self.assertRaises(openfga_sdk.ApiValueError):
            credential.validate_credentials_config()

    def test_configuration_client_credentials_missing_client_secret(self):
        """
        Test credential with method client_credentials and configuration is missing client secret
        """
        credential = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        with self.assertRaises(openfga_sdk.ApiValueError):
            credential.validate_credentials_config()

    def test_configuration_client_credentials_missing_api_issuer(self):
        """
        Test credential with method client_credentials and configuration is missing api issuer
        """
        credential = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_audience="myaudience",
            ),
        )
        with self.assertRaises(openfga_sdk.ApiValueError):
            credential.validate_credentials_config()

    def test_configuration_client_credentials_missing_api_audience(self):
        """
        Test credential with method client_credentials and configuration is missing api audience
        """
        credential = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
            ),
        )
        with self.assertRaises(openfga_sdk.ApiValueError):
            credential.validate_credentials_config()