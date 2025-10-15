from unittest import IsolatedAsyncioTestCase

import openfga_sdk

from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.exceptions import ApiValueError


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

    def test_configuration_client_credentials_with_scopes_list(self):
        """
        Test credential with method client_credentials and scopes as list is valid
        """
        credential = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
                scopes=["read", "write", "admin"],
            ),
        )
        credential.validate_credentials_config()
        self.assertEqual(credential.method, "client_credentials")
        self.assertEqual(credential.configuration.scopes, ["read", "write", "admin"])

    def test_configuration_client_credentials_with_scopes_string(self):
        """
        Test credential with method client_credentials and scopes as string is valid
        """
        credential = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
                scopes="read write admin",
            ),
        )
        credential.validate_credentials_config()
        self.assertEqual(credential.method, "client_credentials")
        self.assertEqual(credential.configuration.scopes, "read write admin")

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


class TestCredentialsIssuer(IsolatedAsyncioTestCase):
    def setUp(self):
        # Setup a basic configuration that can be modified per test case
        self.configuration = CredentialConfiguration(api_issuer="https://example.com")
        self.credentials = Credentials(
            method="client_credentials", configuration=self.configuration
        )

    def test_valid_issuer_https(self):
        # Test a valid HTTPS URL
        self.configuration.api_issuer = "issuer.fga.example	"
        result = self.credentials._parse_issuer(self.configuration.api_issuer)
        self.assertEqual(result, "https://issuer.fga.example/oauth/token")

    def test_valid_issuer_with_oauth_endpoint_https(self):
        # Test a valid HTTPS URL
        self.configuration.api_issuer = "https://example.com/oauth/token"
        result = self.credentials._parse_issuer(self.configuration.api_issuer)
        self.assertEqual(result, "https://example.com/oauth/token")

    def test_valid_issuer_with_some_endpoint_https(self):
        # Test a valid HTTPS URL
        self.configuration.api_issuer = "https://example.com/oauth/some/endpoint"
        result = self.credentials._parse_issuer(self.configuration.api_issuer)
        self.assertEqual(result, "https://example.com/oauth/some/endpoint")

    def test_valid_issuer_http(self):
        # Test a valid HTTP URL
        self.configuration.api_issuer = "fga.example/some_endpoint"
        result = self.credentials._parse_issuer(self.configuration.api_issuer)
        self.assertEqual(result, "https://fga.example/some_endpoint")

    def test_invalid_issuer_no_scheme(self):
        # Test an issuer URL without a scheme
        self.configuration.api_issuer = (
            "https://issuer.fga.example:8080/some_endpoint	"
        )
        result = self.credentials._parse_issuer(self.configuration.api_issuer)
        self.assertEqual(result, "https://issuer.fga.example:8080/some_endpoint")

    def test_invalid_issuer_bad_scheme(self):
        # Test an issuer with an unsupported scheme
        self.configuration.api_issuer = "ftp://example.com"
        with self.assertRaises(ApiValueError):
            self.credentials._parse_issuer(self.configuration.api_issuer)

    def test_invalid_issuer_with_port(self):
        # Test an issuer with an unsupported scheme
        self.configuration.api_issuer = "https://issuer.fga.example:8080 "
        result = self.credentials._parse_issuer(self.configuration.api_issuer)
        self.assertEqual(result, "https://issuer.fga.example:8080/oauth/token")
