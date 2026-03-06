# ruff: noqa: E402

"""
execute_api_request example — calls real OpenFGA endpoints and compares
the results with the regular SDK methods to verify correctness.

Requires a running OpenFGA server (default: http://localhost:8080).
    export FGA_API_URL=http://localhost:8080   # optional, this is the default
    python3 execute_api_request_example.py
"""

import asyncio
import os
import sys

sdk_path = os.path.realpath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sys.path.insert(0, sdk_path)

from openfga_sdk import (
    ClientConfiguration,
    CreateStoreRequest,
    Metadata,
    ObjectRelation,
    OpenFgaClient,
    RelationMetadata,
    RelationReference,
    TypeDefinition,
    Userset,
    Usersets,
    WriteAuthorizationModelRequest,
)
from openfga_sdk.client.models import (
    ClientCheckRequest,
    ClientTuple,
    ClientWriteRequest,
)
from openfga_sdk.credentials import Credentials


async def main():
    api_url = os.getenv("FGA_API_URL", "http://localhost:8080")

    configuration = ClientConfiguration(
        api_url=api_url,
        credentials=Credentials(),
    )

    async with OpenFgaClient(configuration) as fga_client:

        # ─── Setup: create a store, model, and tuple ─────────────
        print("=== Setup ===")

        # Create a test store via the SDK
        store = await fga_client.create_store(
            CreateStoreRequest(name="execute_api_request_test")
        )
        fga_client.set_store_id(store.id)
        print(f"Created store: {store.id}")

        # Write an authorization model
        model_resp = await fga_client.write_authorization_model(
            WriteAuthorizationModelRequest(
                schema_version="1.1",
                type_definitions=[
                    TypeDefinition(type="user"),
                    TypeDefinition(
                        type="document",
                        relations=dict(
                            writer=Userset(this=dict()),
                            viewer=Userset(
                                union=Usersets(
                                    child=[
                                        Userset(this=dict()),
                                        Userset(
                                            computed_userset=ObjectRelation(
                                                object="", relation="writer"
                                            )
                                        ),
                                    ]
                                )
                            ),
                        ),
                        metadata=Metadata(
                            relations=dict(
                                writer=RelationMetadata(
                                    directly_related_user_types=[
                                        RelationReference(type="user"),
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
            )
        )
        auth_model_id = model_resp.authorization_model_id
        fga_client.set_authorization_model_id(auth_model_id)
        print(f"Created model: {auth_model_id}")

        # Write a tuple
        await fga_client.write(
            ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user="user:anne",
                        relation="writer",
                        object="document:roadmap",
                    ),
                ]
            )
        )
        print("Wrote tuple: user:anne → writer → document:roadmap")

        # ─── Tests ────────────────────────────────────────────────
        print("\n=== execute_api_request tests ===\n")

        # ── 1. GET /stores ────────────────────────────────────────
        print("1. ListStores (GET /stores)")
        raw = await fga_client.execute_api_request(
            operation_name="ListStores",
            method="GET",
            path="/stores",
            query_params={"page_size": 100},
        )
        sdk = await fga_client.list_stores()
        body = raw.json()
        assert raw.status == 200, f"Expected 200, got {raw.status}"
        assert "stores" in body
        assert len(body["stores"]) == len(sdk.stores), (
            f"Count mismatch: {len(body['stores'])} vs {len(sdk.stores)}"
        )
        print(f"   ✅ {len(body['stores'])} stores (status {raw.status})")

        # ── 2. GET /stores/{store_id} (auto-substitution) ────────
        print("2. GetStore (GET /stores/{store_id})")
        raw = await fga_client.execute_api_request(
            operation_name="GetStore",
            method="GET",
            path="/stores/{store_id}",
        )
        sdk = await fga_client.get_store()
        body = raw.json()
        assert raw.status == 200
        assert body["id"] == sdk.id
        assert body["name"] == sdk.name
        print(f"   ✅ id={body['id']}, name={body['name']}")

        # ── 3. GET /stores/{store_id}/authorization-models ────────
        print("3. ReadAuthorizationModels (GET /stores/{store_id}/authorization-models)")
        raw = await fga_client.execute_api_request(
            operation_name="ReadAuthorizationModels",
            method="GET",
            path="/stores/{store_id}/authorization-models",
        )
        sdk = await fga_client.read_authorization_models()
        body = raw.json()
        assert raw.status == 200
        assert len(body["authorization_models"]) == len(sdk.authorization_models)
        print(f"   ✅ {len(body['authorization_models'])} models")

        # ── 4. POST /stores/{store_id}/check ──────────────────────
        print("4. Check (POST /stores/{store_id}/check)")
        raw = await fga_client.execute_api_request(
            operation_name="Check",
            method="POST",
            path="/stores/{store_id}/check",
            body={
                "tuple_key": {
                    "user": "user:anne",
                    "relation": "viewer",
                    "object": "document:roadmap",
                },
                "authorization_model_id": auth_model_id,
            },
        )
        sdk = await fga_client.check(
            ClientCheckRequest(
                user="user:anne",
                relation="viewer",
                object="document:roadmap",
            )
        )
        body = raw.json()
        assert raw.status == 200
        assert body["allowed"] == sdk.allowed
        print(f"   ✅ allowed={body['allowed']}")

        # ── 5. POST /stores/{store_id}/read ───────────────────────
        print("5. Read (POST /stores/{store_id}/read)")
        raw = await fga_client.execute_api_request(
            operation_name="Read",
            method="POST",
            path="/stores/{store_id}/read",
            body={
                "tuple_key": {
                    "user": "user:anne",
                    "object": "document:",
                },
            },
        )
        body = raw.json()
        assert raw.status == 200
        assert "tuples" in body
        assert len(body["tuples"]) >= 1
        print(f"   ✅ {len(body['tuples'])} tuples returned")

        # ── 6. POST /stores — create store via raw request ────────
        print("6. CreateStore (POST /stores)")
        raw = await fga_client.execute_api_request(
            operation_name="CreateStore",
            method="POST",
            path="/stores",
            body={"name": "raw_request_test_store"},
        )
        body = raw.json()
        assert raw.status == 201, f"Expected 201, got {raw.status}"
        assert "id" in body
        new_store_id = body["id"]
        print(f"   ✅ created store: {new_store_id}")

        # ── 7. DELETE /stores/{store_id} — clean up ───────────────
        print("7. DeleteStore (DELETE /stores/{store_id})")
        raw = await fga_client.execute_api_request(
            operation_name="DeleteStore",
            method="DELETE",
            path="/stores/{store_id}",
            path_params={"store_id": new_store_id},
        )
        assert raw.status == 204, f"Expected 204, got {raw.status}"
        print(f"   ✅ deleted store: {new_store_id} (status 204 No Content)")

        # ── 8. Custom headers ─────────────────────────────────────
        print("8. Custom headers (GET /stores/{store_id})")
        raw = await fga_client.execute_api_request(
            operation_name="GetStoreWithHeaders",
            method="GET",
            path="/stores/{store_id}",
            headers={"X-Custom-Header": "test-value"},
        )
        assert raw.status == 200
        print(f"   ✅ custom headers accepted (status {raw.status})")

        # ── 9. Explicit path_params override for store_id ─────────
        print("9. Explicit store_id in path_params")
        raw = await fga_client.execute_api_request(
            operation_name="GetStore",
            method="GET",
            path="/stores/{store_id}",
            path_params={"store_id": store.id},
        )
        body = raw.json()
        assert raw.status == 200
        assert body["id"] == store.id
        print(f"   ✅ explicit store_id matched: {body['id']}")

        # ─── Cleanup ─────────────────────────────────────────────
        print("\n=== Cleanup ===")
        await fga_client.delete_store()
        print(f"Deleted test store: {store.id}")

        print("\n All execute_api_request integration tests passed!\n")


asyncio.run(main())


