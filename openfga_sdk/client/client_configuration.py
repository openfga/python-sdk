from openfga_sdk.configuration import Configuration


class ClientConfiguration(Configuration):

    def __init__(
            self,
            api_scheme="https",
            api_host=None,
            store_id=None,
            credentials=None,
            retry_params=None,
            authorization_model_id=None, ):
        super().__init__(api_scheme, api_host, store_id, credentials, retry_params)
        self._authorization_model_id = authorization_model_id

    @property
    def authorization_model_id(self):
        return self._authorization_model_id

    @authorization_model_id.setter
    def authorization_model_id(self, value):
        self._authorization_model_id = value
