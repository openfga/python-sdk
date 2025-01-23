# Streamed List Objects example for OpenFGA's Python SDK

This example demonstrates working with the `POST` `/stores/:id/streamed-list-objects` endpoint in OpenFGA using the Python SDK.

## Prerequisites

If you do not already have an OpenFGA instance running, you can start one using the following command:

```bash
docker run -d -p 8080:8080 openfga/openfga
```

## Configure the example

You may need to configure the example for your environment:

```bash
cp .env.example .env
```

Now edit the `.env` file and set the values as appropriate.

## Running the example

Begin by installing the required dependencies:

```bash
pip install -r requirements.txt
```

Next, run the example. You can use either the synchronous or asynchronous client:

```bash
python asynchronous.py
```

```bash
python synchronous.py
```
