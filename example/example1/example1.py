import asyncio
import openfga_sdk
from openfga_sdk.models import CreateStoreRequest
from openfga_sdk import ClientConfiguration, OpenFgaClient
from openfga_sdk.credentials import CredentialConfiguration, Credentials
import os

async def main():
    credentials = Credentials()
    if os.getenv("FGA_CLIENT_ID") is not None:
        credentials = Credentials(
            method='client_credentials',
            configuration=CredentialConfiguration(
                api_issuer=os.getenv('FGA_API_TOKEN_ISSUER'),
                api_audience=os.getenv('FGA_API_AUDIENCE'),
                client_id=os.getenv('FGA_CLIENT_ID'),
                client_secret=os.getenv('FGA_CLIENT_SECRET')
            )
        )

    if os.getenv('FGA_API_HOST') is not None:
        configuration = ClientConfiguration(
            api_host=os.getenv('FGA_API_HOST'),
            credentials=credentials
        )
    else:
        configuration = ClientConfiguration(
            api_scheme='http',
            api_host='localhost:8080',
            credentials=credentials
        )

    async with OpenFgaClient(configuration) as fga_client:
        # ListStores
        print('Listing Stores')
        response = await fga_client.list_stores()
        print(f"Stores Count: {len(response.stores)}")

        # // CreateStore
        print('Creating Test Store')
        body = CreateStoreRequest(name='Test Store')
        response = await fga_client.create_store(body)
        print(f"Test Store ID: {response.id}")

        # // Set the store id
        fga_client.set_store_id(response.id)

        # // ListStores after Create
        print('Listing Stores')
        response = await fga_client.list_stores()
        print(f"Stores Count: {len(response.stores)}")

        # // GetStore
        print('Getting Current Store')
        response = await fga_client.get_store()
        print(f"Current Store Name: {response.name}")

        # // ReadAuthorizationModels
        print('Reading Authorization Models')
        response = await fga_client.read_authorization_models()
        print(f"Models Count: {len(response.authorization_models)}")

        # // ReadLatestAuthorizationModel
        try:
            response = await fga_client.read_latest_authorization_model()
            if response.authorization_model is not None:
                print(f"Latest Authorization Model ID: {response.authorization_model.id}")
        except:
            print('Latest Authorization Model not found')

        # TODO: Continue fleshing this out
        print('Survived!')

asyncio.run(main())
