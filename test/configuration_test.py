import copy

from unittest.mock import Mock

import pytest

from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.exceptions import ApiValueError, FgaValidationException


@pytest.fixture
def configuration():
    return Configuration()


@pytest.fixture
def servers():
    return [
        {"url": "https://example1.fga.example", "description": "Example 1"},
        {"url": "https://example2.fga.example", "description": "Example 2"},
    ]


@pytest.mark.parametrize(
    "scheme,expected",
    [
        ("https", True),
        ("http", True),
        ("ftp", False),
    ],
)
def test_configuration_api_scheme(configuration, scheme, expected):
    assert configuration.api_scheme == "https"

    if expected is True:
        configuration.api_scheme = scheme
        assert configuration.api_scheme == scheme
    else:
        with pytest.raises(FgaValidationException):
            configuration.api_scheme = scheme


def test_configuration_api_host(configuration):
    assert configuration.api_host is None
    configuration.api_host = "fga.example"
    assert configuration.api_host == "fga.example"

    with pytest.raises(ApiValueError):
        configuration.api_host = "ftp://fga.example"
        configuration.is_valid()


def test_configuration_api_url(configuration):
    assert configuration.api_url is None
    configuration.api_url = "https://fga.example/api"
    assert configuration.api_url == "https://fga.example/api"


def test_configuration_store_id(configuration):
    assert configuration.store_id is None
    configuration.store_id = "store123"
    assert configuration.store_id == "store123"


def test_configuration_credentials(configuration):
    assert configuration.credentials is None
    credentials_mock = Mock()
    configuration.credentials = credentials_mock
    assert configuration.credentials == credentials_mock


def test_configuration_retry_params_default_values(configuration):
    assert configuration.retry_params.max_retry == 3
    assert configuration.retry_params.min_wait_in_ms == 100


def test_configuration_retry_params_custom_values(configuration):
    retry_params = RetryParams(max_retry=10, min_wait_in_ms=50)
    configuration.retry_params = retry_params
    assert configuration.retry_params.max_retry == 10
    assert configuration.retry_params.min_wait_in_ms == 50


def test_configuration_retry_params_invalid_max_retry(configuration):
    with pytest.raises(FgaValidationException):
        configuration.retry_params.max_retry = -1


def test_configuration_retry_params_max_retry_greater_than_max(configuration):
    with pytest.raises(FgaValidationException):
        configuration.retry_params.max_retry = 20


def test_configuration_retry_params_invalid_min_wait_in_ms(configuration):
    with pytest.raises(FgaValidationException):
        configuration.retry_params.min_wait_in_ms = -1


class TestConfigurationSetDefaultAndGetDefaultCopy:
    def test_configuration_set_default(self, configuration):
        default_config = Configuration()
        default_config.api_scheme = "https"
        default_config.api_host = "fga.example"
        default_config.store_id = "store123"
        default_config.credentials = Mock(
            _client_id="client123",
            _client_secret="secret123",
            _api_audience="audience123",
            _api_issuer="issuer123",
            _api_token="token123",
        )
        default_config.retry_params = RetryParams(max_retry=10, min_wait_in_ms=50)
        default_config.api_key = {"api_key1": "key1", "api_key2": "key2"}
        default_config.api_key_prefix = {"api_key1": "Bearer", "api_key2": "Bearer"}
        default_config.username = "user"
        default_config.password = "pass"
        default_config.discard_unknown_keys = True
        default_config.server_index = 1
        default_config.server_variables = {"variable1": "value1", "variable2": "value2"}
        default_config.server_operation_index = {"operation1": 1, "operation2": 2}
        default_config.server_operation_variables = {
            "operation1": {"var1": "val1"},
            "operation2": {"var2": "val2"},
        }
        default_config.ssl_ca_cert = "/path/to/ca_cert.pem"
        default_config.api_url = "https://fga.example/api"
        default_config.timeout_millisec = 10000
        Configuration.set_default(default_config)

        assert Configuration._default.api_scheme == "https"
        assert Configuration._default.api_host == "fga.example"
        assert Configuration._default.store_id == "store123"
        assert (
            isinstance(Configuration._default.credentials, Mock)
            or Configuration._default.credentials is None
        )
        if Configuration._default.credentials:
            assert Configuration._default.credentials._client_id == "client123"
            assert Configuration._default.credentials._client_secret == "secret123"
            assert Configuration._default.credentials._api_audience == "audience123"
            assert Configuration._default.credentials._api_issuer == "issuer123"
            assert Configuration._default.credentials._api_token == "token123"
        assert Configuration._default.retry_params.max_retry == 10
        assert Configuration._default.retry_params.min_wait_in_ms == 50
        assert Configuration._default.api_key == {
            "api_key1": "key1",
            "api_key2": "key2",
        }
        assert Configuration._default.api_key_prefix == {
            "api_key1": "Bearer",
            "api_key2": "Bearer",
        }
        assert Configuration._default.username == "user"
        assert Configuration._default.password == "pass"
        assert Configuration._default.discard_unknown_keys is True
        assert Configuration._default.server_index == 1
        assert Configuration._default.server_variables == {
            "variable1": "value1",
            "variable2": "value2",
        }
        assert Configuration._default.server_operation_index == {
            "operation1": 1,
            "operation2": 2,
        }
        assert Configuration._default.server_operation_variables == {
            "operation1": {"var1": "val1"},
            "operation2": {"var2": "val2"},
        }
        assert Configuration._default.ssl_ca_cert == "/path/to/ca_cert.pem"
        assert Configuration._default.api_url == "https://fga.example/api"
        assert Configuration._default.timeout_millisec == 10000

    def test_configuration_get_default_copy(self, configuration):
        default_config = Configuration()
        default_config.api_scheme = "https"
        default_config.api_host = "fga.example"
        default_config.store_id = "store123"
        default_config.credentials = Mock(
            _client_id="client123",
            _client_secret="secret123",
            _api_audience="audience123",
            _api_issuer="issuer123",
            _api_token="token123",
        )
        default_config.retry_params = RetryParams(max_retry=10, min_wait_in_ms=50)
        default_config.api_key = {"api_key1": "key1", "api_key2": "key2"}
        default_config.api_key_prefix = {"api_key1": "Bearer", "api_key2": "Bearer"}
        default_config.username = "user"
        default_config.password = "pass"
        default_config.discard_unknown_keys = True
        default_config.server_index = 1
        default_config.server_variables = {"variable1": "value1", "variable2": "value2"}
        default_config.server_operation_index = {"operation1": 1, "operation2": 2}
        default_config.server_operation_variables = {
            "operation1": {"var1": "val1"},
            "operation2": {"var2": "val2"},
        }
        default_config.ssl_ca_cert = "/path/to/ca_cert.pem"
        default_config.api_url = "https://fga.example/api"
        default_config.timeout_millisec = 10000
        Configuration.set_default(default_config)

        copied_config = Configuration.get_default_copy()

        assert copied_config.api_scheme == "https"
        assert copied_config.api_host == "fga.example"
        assert copied_config.store_id == "store123"
        assert (
            isinstance(copied_config.credentials, Mock)
            or copied_config.credentials is None
        )
        if copied_config.credentials:
            assert copied_config.credentials._client_id == "client123"
            assert copied_config.credentials._client_secret == "secret123"
            assert copied_config.credentials._api_audience == "audience123"
            assert copied_config.credentials._api_issuer == "issuer123"
            assert copied_config.credentials._api_token == "token123"
        assert Configuration._default.timeout_millisec == 10000


class TestConfigurationValidityChecks:
    def test_configuration_is_valid_missing_api_url(self, configuration):
        with pytest.raises(FgaValidationException):
            configuration.is_valid()

    def test_configuration_is_valid_invalid_store_id(self, configuration):
        configuration.api_url = "https://fga.example"
        configuration.store_id = "invalid_ulid"
        with pytest.raises(FgaValidationException):
            configuration.is_valid()

    def test_configuration_is_valid(self, configuration):
        configuration.api_url = "https://fga.example"
        configuration.store_id = "01F9ZCDXDZBXK83WVMY1VZT23V"
        assert configuration.is_valid() is None


class TestConfigurationLogging:
    def test_configuration_logger_format(self, configuration):
        assert configuration.logger_format == "%(asctime)s %(levelname)s %(message)s"
        configuration.logger_format = "%(levelname)s: %(message)s"
        assert configuration.logger_format == "%(levelname)s: %(message)s"

    def test_configuration_debug(self, configuration):
        assert not configuration.debug
        configuration.debug = True
        assert configuration.debug
        configuration.debug = False
        assert not configuration.debug

    def test_configuration_logger_file(self, configuration):
        assert configuration.logger_file is None
        configuration.logger_file = "debug.log"
        assert configuration.logger_file == "debug.log"


class TestConfigurationHostSettings:
    def test_configuration_get_host_settings(self, configuration):
        assert configuration.get_host_settings() == [
            {"url": "", "description": "No description provided"}
        ]

    def test_configuration_get_host_from_settings(self, configuration, servers):
        assert (
            configuration.get_host_from_settings(0, servers=servers)
            == "https://example1.fga.example"
        )
        assert (
            configuration.get_host_from_settings(1, servers=servers)
            == "https://example2.fga.example"
        )

    def test_configuration_get_host_from_settings_invalid_value(self, configuration):
        with pytest.raises(ValueError):
            configuration.get_host_from_settings(999, variables={"var": "value"})


class TestConfigurationHeaders:
    def test_configuration_headers_default_none(self, configuration):
        """Test that headers default to an empty dict"""
        assert configuration.headers == {}

    def test_configuration_headers_initialization_with_dict(self):
        """Test initializing Configuration with headers"""
        headers = {
            "X-Custom-Header": "custom-value",
            "X-Request-Source": "test-app",
        }
        config = Configuration(
            api_url="https://fga.example",
            headers=headers,
        )
        assert config.headers == headers
        assert config.headers["X-Custom-Header"] == "custom-value"
        assert config.headers["X-Request-Source"] == "test-app"

    def test_configuration_headers_initialization_with_none(self):
        """Test initializing Configuration with headers=None"""
        config = Configuration(
            api_url="https://fga.example",
            headers=None,
        )
        assert config.headers == {}

    def test_configuration_headers_setter_with_dict(self, configuration):
        """Test setting headers using the property setter"""
        headers = {"X-Test": "test-value"}
        configuration.headers = headers
        assert configuration.headers == headers
        assert configuration.headers["X-Test"] == "test-value"

    def test_configuration_headers_setter_with_none(self, configuration):
        """Test setting headers to None using the property setter"""
        configuration.headers = {"X-Test": "value"}
        assert configuration.headers == {"X-Test": "value"}

        configuration.headers = None
        assert configuration.headers == {}

    def test_configuration_headers_modification(self, configuration):
        """Test that headers can be modified after initialization"""
        configuration.headers = {"X-Initial": "initial"}
        assert configuration.headers["X-Initial"] == "initial"

        configuration.headers["X-Additional"] = "additional"
        assert configuration.headers["X-Additional"] == "additional"
        assert len(configuration.headers) == 2

    def test_configuration_headers_with_multiple_headers(self):
        """Test Configuration with multiple custom headers"""
        headers = {
            "X-Request-ID": "123e4567-e89b-12d3-a456-426614174000",
            "X-API-Key": "secret-key",
            "X-Tenant-ID": "tenant-123",
            "X-User-Agent": "custom-agent/1.0",
        }
        config = Configuration(
            api_url="https://fga.example",
            headers=headers,
        )
        assert config.headers == headers
        assert len(config.headers) == 4

    def test_configuration_headers_empty_dict(self):
        """Test initializing Configuration with empty headers dict"""
        config = Configuration(
            api_url="https://fga.example",
            headers={},
        )
        assert config.headers == {}

    def test_configuration_headers_deepcopy(self):
        """Test that headers are properly deep copied"""
        headers = {"X-Test": "value"}
        config = Configuration(
            api_url="https://fga.example",
            headers=headers,
        )

        copied_config = copy.deepcopy(config)

        assert copied_config.headers == config.headers
        assert copied_config.headers is not config.headers  # Different object

        # Modify original and verify copy is unaffected
        config.headers["X-New"] = "new-value"
        assert "X-New" not in copied_config.headers

    def test_configuration_headers_setter_validation_non_dict(self):
        """Test that setting headers to non-dict raises FgaValidationException"""
        from openfga_sdk.exceptions import FgaValidationException

        config = Configuration(api_url="https://fga.example")

        with pytest.raises(
            FgaValidationException, match="headers must be a dict or None"
        ):
            config.headers = "not a dict"

        with pytest.raises(
            FgaValidationException, match="headers must be a dict or None"
        ):
            config.headers = ["list", "of", "values"]

        with pytest.raises(
            FgaValidationException, match="headers must be a dict or None"
        ):
            config.headers = 123

    def test_configuration_headers_validation_non_string_keys(self):
        """Test that headers with non-string keys fail validation"""
        from openfga_sdk.exceptions import FgaValidationException

        config = Configuration(
            api_url="https://fga.example",
            headers={123: "value", "valid": "value"},
        )

        with pytest.raises(FgaValidationException, match="header keys must be strings"):
            config.is_valid()

    def test_configuration_headers_validation_non_string_values(self):
        """Test that headers with non-string values fail validation"""
        from openfga_sdk.exceptions import FgaValidationException

        config = Configuration(
            api_url="https://fga.example",
            headers={"key": 456, "valid": "value"},
        )

        with pytest.raises(
            FgaValidationException, match="header values must be strings"
        ):
            config.is_valid()

    def test_configuration_headers_validation_passes_with_valid_headers(self):
        """Test that valid headers pass validation"""
        config = Configuration(
            api_url="https://fga.example",
            headers={"X-Custom": "value", "X-Another": "another-value"},
        )

        # Should not raise any exception
        config.is_valid()


class TestConfigurationMiscellaneous:
    def test_configuration_get_api_key_with_prefix(self, configuration):
        configuration.api_key = {"api_key": "123"}
        configuration.api_key_prefix = {"api_key": "Bearer"}
        assert configuration.get_api_key_with_prefix("api_key") == "Bearer 123"

    def test_configuration_get_basic_auth_token(self, configuration):
        configuration.username = "user"
        configuration.password = "pass"
        assert configuration.get_basic_auth_token() == "Basic dXNlcjpwYXNz"

    def test_configuration_auth_settings(self, configuration):
        assert configuration.auth_settings() == {}

    def test_configuration_to_debug_report(self, configuration):
        report = configuration.to_debug_report()
        assert "Python SDK Debug Report" in report
        assert "OS" in report
        assert "Python Version" in report
        assert "Version of the API" in report
        assert "SDK Package Version" in report

    def test_configuration_deepcopy(self, configuration):
        # Create a Configuration object with some values
        config = Configuration(
            api_scheme="https",
            api_host="fga.example",
            store_id="store123",
            credentials=Mock(
                _client_id="client123",
                _client_secret="secret123",
                _api_audience="audience123",
                _api_issuer="issuer123",
                _api_token="token123",
            ),
            retry_params=RetryParams(max_retry=10, min_wait_in_ms=50),
            api_key={"api_key1": "key1", "api_key2": "key2"},
            api_key_prefix={"api_key1": "Bearer", "api_key2": "Bearer"},
            username="user",
            password="pass",
            discard_unknown_keys=True,
            server_index=1,
            server_variables={"variable1": "value1", "variable2": "value2"},
            server_operation_index={"operation1": 1, "operation2": 2},
            server_operation_variables={
                "operation1": {"var1": "val1"},
                "operation2": {"var2": "val2"},
            },
            ssl_ca_cert="/path/to/ca_cert.pem",
            api_url="https://fga.example/api",
            timeout_millisec=10000,
        )

        # Perform deep copy
        copied_config = copy.deepcopy(config)

        # Verify all attributes of copied object are equal to original object
        assert copied_config.api_scheme == config.api_scheme
        assert copied_config.api_host == config.api_host
        assert copied_config.store_id == config.store_id
        assert (
            isinstance(Configuration._default.credentials, Mock)
            or Configuration._default.credentials is None
        )
        assert Configuration._default.retry_params.max_retry == 10
        assert Configuration._default.retry_params.min_wait_in_ms == 50
        assert copied_config.api_key == config.api_key
        assert copied_config.api_key_prefix == config.api_key_prefix
        assert copied_config.username == config.username
        assert copied_config.password == config.password
        assert copied_config.discard_unknown_keys == config.discard_unknown_keys
        assert copied_config.server_index == config.server_index
        assert copied_config.server_variables == config.server_variables
        assert copied_config.server_operation_index == config.server_operation_index
        assert (
            copied_config.server_operation_variables
            == config.server_operation_variables
        )
        assert copied_config.ssl_ca_cert == config.ssl_ca_cert
        assert copied_config.api_url == config.api_url
        assert copied_config.timeout_millisec == config.timeout_millisec
