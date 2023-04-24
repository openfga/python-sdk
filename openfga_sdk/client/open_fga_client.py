from openfga_sdk.models import CheckRequest, TupleKey
from openfga_sdk.api.open_fga_api import OpenFgaApi
from openfga_sdk.api_client import ApiClient


class OpenFgaClient():
    def __init__(self, client_configuration):
        self._client_configuration: client_configuration

        api_client = ApiClient()
        self._api_client = api_client
        self._api = OpenFgaApi(api_client)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        await self.api.close()

    def get_authorization_model_id(self, options):
        if options is not None and options.authorization_model_id is not None:
            return options.authorization_model_id
        else:
            self._client_configuration.authorization_model_id

    """Check whether a user is authorized to access an object  # noqa: E501
    :param body: (required)
    :type body: CheckRequest
    """
    async def check(self, body, options, **kwargs):  # noqa: E501
        body = CheckRequest(
            tuple_key=TupleKey(
                user=body.user,
                relation=body.relation,
                object=body.object,
            ),
            # contextual_tuples=
            authorization_model_id=self.get_authorization_model_id(options),
        )
        api_response = await self._api.check(
            body=body,
        )

        return api_response
