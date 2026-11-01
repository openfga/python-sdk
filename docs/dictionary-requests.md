# Dictionary request bodies

Both the asynchronous and synchronous `OpenFgaClient` accept dictionaries in
place of request model instances. Dictionary keys use the same names as the
corresponding Python constructor arguments, rather than the low-level HTTP
request shape.

For example, these checks are equivalent:

```python
from openfga_sdk.client.models import ClientCheckRequest

result = await fga_client.check(
    ClientCheckRequest(
        user="user:bob",
        relation="viewer",
        object="document:roadmap",
    )
)

result = await fga_client.check(
    {
        "user": "user:bob",
        "relation": "viewer",
        "object": "document:roadmap",
    }
)
```

The synchronous client accepts the same bodies without `await`.

## Nested tuples and batch checks

Nested contextual tuples, write/delete tuples, and batch check items can also
be dictionaries. Existing model instances can be included in those lists.

```python
await fga_client.write(
    {
        "writes": [
            {
                "user": "user:bob",
                "relation": "viewer",
                "object": "document:roadmap",
            }
        ]
    }
)

result = await fga_client.batch_check(
    {
        "checks": [
            {
                "user": "user:bob",
                "relation": "viewer",
                "object": "document:roadmap",
                "correlation_id": "roadmap-view",
            }
        ]
    }
)
```

Methods that take a list (`write_tuples`, `delete_tuples`, `client_batch_check`,
and `write_assertions`) continue to take a list, with dictionaries permitted
as its elements. Options remain a separate argument.

For dictionary-only requests, the SDK does not insert generated correlation IDs
or replace nested tuples in the supplied dictionaries. Existing model instances
keep their existing behavior: for example, BatchCheck assigns a correlation ID
to a supplied `ClientBatchCheckItem` if it does not have one.

Request context and condition context retain their dictionary values. The SDK
constructs the outer request and nested client tuples/checks, so missing required
constructor arguments and unexpected keys there raise constructor errors.
Nested generated-model fields, such as a tuple's `condition`, a ListUsers
`object`, and authorization-model definitions, are serialized directly when
provided as dictionaries; their contents are validated by the server. Supply
generated model instances in these fields if you also want their constructor
validation locally.

This support applies to dictionaries passed as request bodies. It does not
change the accepted constructor arguments of existing request model classes.
