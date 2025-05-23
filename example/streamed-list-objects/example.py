# ruff: noqa: E402

"""
Python SDK for OpenFGA

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

import asyncio
import json
import os
import sys


###
# The following two lines are just a convenience for SDK development and testing,
# and should not be used in your code. They allow you to run this example using the
# local SDK code from the parent directory, rather than using the installed package.
###
sdk_path = os.path.realpath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sys.path.insert(0, sdk_path)

from openfga_sdk.client import OpenFgaClient
from openfga_sdk.client.configuration import ClientConfiguration
from openfga_sdk.client.models.list_objects_request import ClientListObjectsRequest
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.models.create_store_request import CreateStoreRequest


async def create_store(openfga: OpenFgaClient) -> str:
    """
    Create a temporary store. The store will be deleted at the end of the example.
    """

    response = await openfga.create_store(CreateStoreRequest(name="Demo Store"))
    return response.id


async def write_model(openfga: OpenFgaClient) -> str:
    """
    Load the authentication model from a file and write it to the server.
    """

    with open("model.json") as model:
        response = await openfga.write_authorization_model(json.loads(model.read()))
        return response.authorization_model_id


async def write_tuples(openfga: OpenFgaClient, quantity: int) -> int:
    """
    Write a variable number of tuples to the temporary store.
    """

    chunks = quantity // 100

    for chunk in range(0, chunks):
        await openfga.write_tuples(
            [
                ClientTuple(
                    user="user:anne",
                    relation="owner",
                    object=f"document:{chunk * 100 + t}",
                )
                for t in range(0, 100)
            ],
        )

    return quantity


async def streamed_list_objects(
    openfga: OpenFgaClient, request: ClientListObjectsRequest
):
    """
    Send our request to the streaming endpoint, and iterate over the streamed responses.
    """
    results = []

    # Note that streamed_list_objects() is an asynchronous generator, so we could yield results as they come in.
    # For the sake of this example, we'll just collect all the results into a list and yield them all at once.

    async for response in openfga.streamed_list_objects(request):
        results.append(response.object)

    return results


async def list_objects(openfga: OpenFgaClient, request: ClientListObjectsRequest):
    """
    For comparison sake, here is the non-streamed version of the same call, using list_objects().
    Note that in the non-streamed version, the server will return a maximum of 1000 results.
    """
    results = await openfga.list_objects(request)
    return results.objects


async def main():
    configure = ClientConfiguration(
        api_url="http://localhost:8080",
    )

    async with OpenFgaClient(configure) as openfga:
        # Create our temporary store
        store = await create_store(openfga)
        print(f"Created temporary store ({store})")

        # Configure the SDK to use the temporary store for the rest of the example
        openfga.set_store_id(store)

        # Load the authorization model from a file and write it to the server
        model = await write_model(openfga)
        print(f"Created temporary authorization model ({model})\n")

        # Configure the SDK to use this authorization model for the rest of the example
        openfga.set_authorization_model_id(model)

        # Write a bunch of example tuples to the temporary store
        wrote = await write_tuples(openfga, 2000)
        print(f"Wrote {wrote} tuples to the store.\n")

        ################################

        # Craft a request to list all `documents` owned by `user:anne``
        request = ClientListObjectsRequest(
            type="document",
            relation="owner",
            user="user:anne",
        )

        # Send a single request to the server using both the streamed and standard endpoints
        streamed_results = await streamed_list_objects(openfga, request)
        standard_results = await list_objects(openfga, request)

        print(
            f"/streamed-list-objects returned {streamed_results.__len__()} objects in a single request.",
        )
        # print([r for r in streamed_results])

        print(
            f"/list-objects returned {standard_results.__len__()} objects in a single request.",
        )
        # print([r for r in standard_results])

        ################################

        # Finally, delete the temporary store.
        await openfga.delete_store()
        print(f"\nDeleted temporary store ({store})")


if __name__ == "__main__":
    asyncio.run(main())
