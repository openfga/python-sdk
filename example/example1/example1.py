import asyncio
import json

import openfga_sdk
from openfga_sdk.client.models import ClientAssertion, ClientCheckRequest, ClientReadChangesRequest, ClientTuple, ClientWriteRequest
from openfga_sdk.models import CreateStoreRequest, Metadata, ObjectRelation, RelationMetadata, TupleKey, TypeDefinition, Userset, Usersets, WriteAuthorizationModelRequest
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
        # ListStores (before create)
        print('Listing Stores')
        response = await fga_client.list_stores()
        print(f"Stores Count: {len(response.stores)}")

        store_name = 'Test Store'

        # CreateStore (before create)
        print('Creating Test Store')
        body = CreateStoreRequest(name=store_name)
        response = await fga_client.create_store(body)
        print(f"Test Store ID: {response.id}")

        # Set the store ID
        fga_client.set_store_id(response.id)

        # ListStores (after create)
        print('Listing Stores')
        response = await fga_client.list_stores()
        print(f"Stores Count: {len(response.stores)}")

        # GetStore (after create)
        print('Getting Current Store')
        response = await fga_client.get_store()
        print(f"Current Store Name: {response.name}")

        # ReadAuthorizationModels (before write)
        print('Reading Authorization Models')
        response = await fga_client.read_authorization_models()
        print(f"Models Count: {len(response.authorization_models)}")

        # ReadLatestAuthorizationModel (before write)
        try:
            response = await fga_client.read_latest_authorization_model()
            if response.authorization_model is not None:
                print(f"Latest Authorization Model ID: {response.authorization_model.id}")
        except:
            print('Latest Authorization Model not found')

        # WriteAuthorizationModel
        print('Writing an Authorization Model')
        with open(os.path.join(os.path.dirname(__file__), 'auth-model.json')) as f:
            auth_model_request = json.load(f)
        response = await fga_client.write_authorization_model(auth_model_request)
        print(f"Authorization Model ID: {response.authorization_model_id}")

        # ReadAuthorizationModels (after write)
        print('Reading Authorization Models')
        response = await fga_client.read_authorization_models()
        print(f"Models Count: {len(response.authorization_models)}")

        # ReadLatestAuthorizationModel (after write)
        response = await fga_client.read_latest_authorization_model()
        if response.authorization_model is not None:
            print(f"Latest Authorization Model ID: {response.authorization_model.id}")

        auth_model_id = response.authorization_model.id

        # Write
        print('Writing Tuples')
        body = ClientWriteRequest(
            writes=[
                ClientTuple(
                    user='user:anne',
                    relation='writer',
                    object='document:roadmap',
                    # condition=RelationshipCondition(
                    #   name='ViewCountLessThan200',
                    #   context=dict(
                    #       Name='Roadmap',
                    #       Type='Document',
                    #   ),
                    # ),
                ),
            ],
        )
        options = {
            # You can rely on the model id set in the configuration or override it for this specific request
            "authorization_model_id": auth_model_id
        }
        await fga_client.write(body, options)
        print('Done Writing Tuples')

        # Set the model ID
        fga_client.set_authorization_model_id(auth_model_id)

        # Read
        print('Reading Tuples')
        response = await fga_client.read(TupleKey(user='user:anne', object='document:'))
        print(f"Read Tuples: {response.tuples}")

        # ReadChanges
        print('Reading Tuple Changes')
        body = ClientReadChangesRequest('document')
        response = await fga_client.read_changes(body)
        print(f"Read Changes Tuples: {response.changes}")

        # Check
        print('Checking for access')
        response = await fga_client.check(ClientCheckRequest(
            user='user:anne',
            relation='reader',
            object='document:roadmap',
        ))
        print(f"Allowed: {response.allowed}")

        # Checking for access with context
        # TODO

        # WriteAssertions
        await fga_client.write_assertions([
            ClientAssertion(
                user='user:carl',
                relation='writer',
                object='document:budget',
                expectation=True,
            ),
            ClientAssertion(
                user='user:anne',
                relation='reader',
                object='document:roadmap',
                expectation=False,
            ),
        ])
        print('Assertions updated')

        # ReadAssertions
        print('Reading Assertions')
        response = await fga_client.read_assertions()
        print(f"Assertions: {response.assertions}")

        # DeleteStore
        print('Deleting Current Store')
        await fga_client.delete_store()
        print(f"Deleted Store: {store_name}")


asyncio.run(main())
