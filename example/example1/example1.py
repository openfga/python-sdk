import asyncio
import os
import uuid

from openfga_sdk import (
    ClientConfiguration,
    Condition,
    ConditionParamTypeRef,
    CreateStoreRequest,
    Metadata,
    ObjectRelation,
    OpenFgaClient,
    ReadRequestTupleKey,
    RelationMetadata,
    RelationReference,
    RelationshipCondition,
    TypeDefinition,
    Userset,
    Usersets,
    UserTypeFilter,
    WriteAuthorizationModelRequest,
)
from openfga_sdk.client.models import (
    ClientAssertion,
    ClientBatchCheckItem,
    ClientBatchCheckRequest,
    ClientCheckRequest,
    ClientListObjectsRequest,
    ClientListRelationsRequest,
    ClientReadChangesRequest,
    ClientTuple,
    ClientWriteRequest,
    WriteTransactionOpts,
)
from openfga_sdk.client.models.list_users_request import ClientListUsersRequest
from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.models.fga_object import FgaObject


async def main():
    credentials = Credentials()
    if os.getenv("FGA_CLIENT_ID") is not None:
        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                api_issuer=os.getenv("FGA_API_TOKEN_ISSUER"),
                api_audience=os.getenv("FGA_API_AUDIENCE"),
                client_id=os.getenv("FGA_CLIENT_ID"),
                client_secret=os.getenv("FGA_CLIENT_SECRET"),
            ),
        )

    if os.getenv("FGA_API_URL") is not None:
        configuration = ClientConfiguration(
            api_url=os.getenv("FGA_API_URL"), credentials=credentials
        )
    else:
        configuration = ClientConfiguration(
            api_url="http://localhost:8080", credentials=credentials
        )

    async with OpenFgaClient(configuration) as fga_client:
        # ListStores (before create)
        print("Listing Stores")
        response = await fga_client.list_stores()
        print(f"Stores Count: {len(response.stores)}")

        store_name = "Test Store"

        # CreateStore (before create)
        print("Creating Test Store")
        body = CreateStoreRequest(name=store_name)
        response = await fga_client.create_store(body)
        print(f"Test Store ID: {response.id}")

        store_id = response.id

        # ListStores (after create)
        print("Listing Stores")
        response = await fga_client.list_stores()
        print(f"Stores Count: {len(response.stores)}")

        # GetStore (after create)
        print("Getting Current Store")
        response = await fga_client.get_store({"store_id": store_id})
        print(f"Current Store Name: {response.name}")

        # ReadAuthorizationModels (before write)
        print("Reading Authorization Models")
        response = await fga_client.read_authorization_models({"store_id": store_id})
        print(f"Models Count: {len(response.authorization_models)}")

        # ReadLatestAuthorizationModel (before write)
        try:
            response = await fga_client.read_latest_authorization_model(
                {"store_id": store_id}
            )
            if response.authorization_model is not None:
                print(
                    f"Latest Authorization Model ID: {response.authorization_model.id}"
                )
        except Exception as err:
            print("Latest Authorization Model not found")
            raise err

        # WriteAuthorizationModel
        print("Writing an Authorization Model")
        response = await fga_client.write_authorization_model(
            WriteAuthorizationModelRequest(
                schema_version="1.1",
                type_definitions=[
                    TypeDefinition(type="user"),
                    TypeDefinition(
                        type="document",
                        relations=dict(
                            writer=Userset(
                                this=dict(),
                            ),
                            viewer=Userset(
                                union=Usersets(
                                    child=[
                                        Userset(this=dict()),
                                        Userset(
                                            computed_userset=ObjectRelation(
                                                object="",
                                                relation="writer",
                                            )
                                        ),
                                    ],
                                ),
                            ),
                        ),
                        metadata=Metadata(
                            relations=dict(
                                writer=RelationMetadata(
                                    directly_related_user_types=[
                                        RelationReference(type="user"),
                                        RelationReference(
                                            type="user",
                                            condition="ViewCountLessThan200",
                                        ),
                                    ]
                                ),
                                viewer=RelationMetadata(
                                    directly_related_user_types=[
                                        RelationReference(type="user"),
                                    ]
                                ),
                            )
                        ),
                    ),
                ],
                conditions=dict(
                    ViewCountLessThan200=Condition(
                        name="ViewCountLessThan200",
                        expression="ViewCount < 200",
                        parameters=dict(
                            ViewCount=ConditionParamTypeRef(type_name="TYPE_NAME_INT"),
                            Type=ConditionParamTypeRef(type_name="TYPE_NAME_STRING"),
                            Name=ConditionParamTypeRef(type_name="TYPE_NAME_STRING"),
                        ),
                    )
                ),
            ),
            {
                "store_id": store_id,
            },
        )
        print(f"Authorization Model ID: {response.authorization_model_id}")

        # ReadAuthorizationModels (after write)
        print("Reading Authorization Models")
        response = await fga_client.read_authorization_models({"store_id": store_id})
        print(f"Models Count: {len(response.authorization_models)}")

        # ReadLatestAuthorizationModel (after write)
        response = await fga_client.read_latest_authorization_model(
            {"store_id": store_id}
        )
        if response.authorization_model is not None:
            print(f"Latest Authorization Model ID: {response.authorization_model.id}")

        auth_model_id = response.authorization_model.id

        # Write
        print("Writing Tuples")
        body = ClientWriteRequest(
            writes=[
                ClientTuple(
                    user="user:anne",
                    relation="writer",
                    object="document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
                    condition=RelationshipCondition(
                        name="ViewCountLessThan200",
                        context=dict(
                            Name="Roadmap",
                            Type="Document",
                        ),
                    ),
                ),
            ],
        )
        options = {
            # You can rely on the model id set in the configuration or override it for this specific request
            "authorization_model_id": auth_model_id,
            "store_id": store_id,
        }
        await fga_client.write(body, options)
        print("Done Writing Tuples")

        # Write
        print("Writing Tuples - non txn")
        body = ClientWriteRequest(
            writes=[
                ClientTuple(
                    user="user:beth",
                    relation="writer",
                    object="document:1",
                    condition=RelationshipCondition(
                        name="ViewCountLessThan200",
                        context=dict(
                            Name="Roadmap",
                            Type="Document",
                        ),
                    ),
                ),
                ClientTuple(user="user:beth", relation="viewer", object="document:2"),
            ],
        )
        options = {
            # You can rely on the model id set in the configuration or override it for this specific request
            "authorization_model_id": auth_model_id,
            "transaction": WriteTransactionOpts(max_per_chunk=1),
            "store_id": store_id,
        }
        await fga_client.write(body, options)
        print("Done Writing Tuples")

        # Set the model ID
        fga_client.set_authorization_model_id(auth_model_id)

        # Read
        print("Reading Tuples")
        response = await fga_client.read(
            ReadRequestTupleKey(user="user:anne", object="document:"),
            options={
                "store_id": store_id,
            },
        )
        print(f"Read Tuples: {response.tuples}")

        # ReadChanges
        print("Reading Tuple Changes")
        body = ClientReadChangesRequest(type="document")
        response = await fga_client.read_changes(
            body,
            {
                "store_id": store_id,
            },
        )
        print(f"Read Changes Tuples: {response.changes}")

        # Check
        print("Checking for access w/o context")
        try:
            response = await fga_client.check(
                ClientCheckRequest(
                    user="user:anne",
                    relation="viewer",
                    object="document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
                ),
                options={
                    "store_id": store_id,
                },
            )
            print(f"Allowed: {response.allowed}")
        except Exception as err:
            print(f"Failed due to: {err}")

        # Checking for access with context
        print("Checking for access with context")

        response = await fga_client.check(
            ClientCheckRequest(
                user="user:anne",
                relation="viewer",
                object="document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
                context=dict(ViewCount=100),
            ),
            options={
                "store_id": store_id,
            },
        )
        print(f"Allowed: {response.allowed}")

        # Performing a BatchCheck
        print("Checking for access via BatchCheck")

        anne_cor_id = str(uuid.uuid4())
        response = await fga_client.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    ClientBatchCheckItem(
                        user="user:anne",
                        relation="viewer",
                        object="document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
                        context=dict(ViewCount=100),
                        correlation_id=anne_cor_id,  # correlation_id is an optional parameter, the SDK will insert a value if not provided.
                    ),
                    ClientBatchCheckItem(
                        user="user:bob",
                        relation="viewer",
                        object="document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
                        context=dict(ViewCount=100),
                    ),
                ]
            ),
            options={
                "store_id": store_id,
            },
        )

        for result in response.result:
            if result.correlation_id == anne_cor_id:
                print(f"Anne allowed: {result.allowed}")
            else:
                print(f"{result.request.user} allowed: {result.allowed}")

        # List objects with context
        print("Listing objects for access with context")

        response = await fga_client.list_objects(
            ClientListObjectsRequest(
                user="user:anne",
                relation="viewer",
                type="document",
                context=dict(ViewCount=100),
            ),
            options={
                "store_id": store_id,
            },
        )
        print(f"Objects: {response.objects}")

        # List relations w/o context
        print("Listing relations for access w/o context")

        response = await fga_client.list_relations(
            ClientListRelationsRequest(
                user="user:anne",
                relations=["viewer", "writer"],
                object="document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
            ),
            options={
                "store_id": store_id,
            },
        )
        print(f"Relations: {response}")

        # List relations with context
        print("Listing relations for access with context")

        response = await fga_client.list_relations(
            ClientListRelationsRequest(
                user="user:anne",
                relations=["viewer", "writer"],
                object="document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
                context=dict(ViewCount=100),
            ),
            options={
                "store_id": store_id,
            },
        )
        print(f"Relations: {response}")

        # ListUsers
        print("Listing user who have access to object")

        response = await fga_client.list_users(
            ClientListUsersRequest(
                relation="viewer",
                object=FgaObject(type="document", id="roadmap"),
                user_filters=[
                    UserTypeFilter(type="user"),
                ],
                context=dict(ViewCount=100),
            ),
            options={
                "store_id": store_id,
            },
        )
        print(f"Users: {response.users}")

        # WriteAssertions
        await fga_client.write_assertions(
            [
                ClientAssertion(
                    user="user:carl",
                    relation="writer",
                    object="document:budget",
                    expectation=True,
                ),
                ClientAssertion(
                    user="user:anne",
                    relation="viewer",
                    object="document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
                    expectation=False,
                ),
            ],
            {
                "store_id": store_id,
            },
        )
        print("Assertions updated")

        # ReadAssertions
        print("Reading Assertions")
        response = await fga_client.read_assertions({"store_id": store_id})
        print(f"Assertions: {response.assertions}")

        # DeleteStore
        print("Deleting Current Store")
        await fga_client.delete_store({"store_id": store_id})
        print(f"Deleted Store: {store_name}")


asyncio.run(main())
