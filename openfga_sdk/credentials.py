from urllib.parse import urlparse, urlunparse

from openfga_sdk.exceptions import ApiValueError


def none_or_empty(value):
    """
    Return true if value is either none or empty string
    """
    return value is None or value == ""


class CredentialConfiguration:
    """
    Configuration for SDK credential
    :param client_id: Client ID which will be matched with client_secret
    :param client_secret: Client secret which will be matched with client_id
    :param api_token: Bearer token to be sent for authentication
    :param api_audience: API audience used for OAuth2
    :param api_issuer: API issuer used for OAuth2
    :param scopes: OAuth2 scopes to request, can be a list of strings or a space-separated string
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        api_audience: str | None = None,
        api_issuer: str | None = None,
        api_token: str | None = None,
        scopes: str | list[str] | None = None,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_audience = api_audience
        self._api_issuer = api_issuer
        self._api_token = api_token
        self._scopes = scopes

    @property
    def client_id(self):
        """
        Return the client id configured
        """
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        """
        Update the client id
        """
        self._client_id = value

    @property
    def client_secret(self):
        """
        Return the client secret configured
        """
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value):
        """
        Update the client secret
        """
        self._client_secret = value

    @property
    def api_audience(self):
        """
        Return the api audience configured
        """
        return self._api_audience

    @api_audience.setter
    def api_audience(self, value):
        """
        Update the api audience
        """
        self._api_audience = value

    @property
    def api_issuer(self):
        """
        Return the api issuer configured
        """
        return self._api_issuer

    @api_issuer.setter
    def api_issuer(self, value):
        """
        Update the api issuer
        """
        self._api_issuer = value

    @property
    def api_token(self):
        """
        Return the api token configured
        """
        return self._api_token

    @api_token.setter
    def api_token(self, value):
        """
        Update the api token
        """
        self._api_token = value

    @property
    def scopes(self):
        """
        Return the scopes configured
        """
        return self._scopes

    @scopes.setter
    def scopes(self, value):
        """
        Update the scopes
        """
        self._scopes = value


class Credentials:
    """
    Manage the credential for the API Client
    :param method: Type of authentication. Possible value is 'none', 'api_token' and 'client_credentials'. Default as 'none'.
    :param configuration: Credential configuration of type CredentialConfiguration. Default as None.
    """

    def __init__(
        self,
        method: str | None = "none",
        configuration: CredentialConfiguration | None = None,
    ):
        self._method = method
        self._configuration = configuration

    @property
    def method(self):
        """
        Return the method configured
        """
        return self._method

    @method.setter
    def method(self, value):
        """
        Update the method
        """
        self._method = value

    @property
    def configuration(self):
        """
        Return the configuration
        """
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        """
        Update the configuration
        """
        self._configuration = value

    def _parse_issuer(self, issuer: str):
        default_endpoint_path = "/oauth/token"

        parsed_url = urlparse(issuer.strip())

        try:
            parsed_url.port
        except ValueError as e:
            raise ApiValueError(e)

        if parsed_url.netloc is None and parsed_url.path is None:
            raise ApiValueError("Invalid issuer")

        if parsed_url.scheme == "":
            parsed_url = urlparse(f"https://{issuer}")
        elif parsed_url.scheme not in ("http", "https"):
            raise ApiValueError(
                f"Invalid issuer scheme {parsed_url.scheme} must be HTTP or HTTPS"
            )

        if parsed_url.path in ("", "/"):
            parsed_url = parsed_url._replace(path=default_endpoint_path)

        valid_url = urlunparse(parsed_url)

        return valid_url

    def validate_credentials_config(self):
        """
        Check whether credentials configuration is valid
        """
        if (
            self.method != "none"
            and self.method != "api_token"
            and self.method != "client_credentials"
        ):
            raise ApiValueError(
                f"method `{self.method}` must be either `none`, `api_token` or `client_credentials`"
            )
        if self.method == "api_token" and (
            self.configuration is None or none_or_empty(self.configuration.api_token)
        ):
            raise ApiValueError(
                f"configuration `{self.configuration}` api_token must be defined and non empty when method is api_token"
            )
        if self.method == "client_credentials":
            if (
                self.configuration is None
                or none_or_empty(self.configuration.client_id)
                or none_or_empty(self.configuration.client_secret)
                or none_or_empty(self.configuration.api_audience)
                or none_or_empty(self.configuration.api_issuer)
            ):
                raise ApiValueError(
                    "configuration `{}` requires client_id, client_secret, api_audience and api_issuer defined for client_credentials method."
                )

            # validate token issuer
            self._parse_issuer(self.configuration.api_issuer)
