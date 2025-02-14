# Streamed List Objects Example

This example demonstrates working with [OpenFGA's `/streamed-list-objects` endpoint](https://openfga.dev/api/service#/Relationship%20Queries/StreamedListObjects) using the Python SDK's `streamed_list_objects()` method.

## Prerequisites

- Python 3.10+
- OpenFGA running on `localhost:8080`

You can start OpenFGA with Docker by running the following command:

```bash
docker pull openfga/openfga && docker run -it --rm -p 8080:8080 openfga/openfga run
```

## Running the example

No additional setup is required to run this example. Simply run the following command:

```bash
python example.py
```
