---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**Version of SDK**
v0.2.0

**Version of OpenFGA (if known)**
v1.1.0

**To Reproduce**
Steps to reproduce the behavior:
1. Initialize OpenFgaClient with openfga_sdk.ClientConfiguration parameter api_host=127.0.0.1, credentials method client_credentials
2. Invoke method read_authorization_models
3. See exception thrown

**Sample Code That Produces Issues**

```
    configuration = openfga_sdk.ClientConfiguration(
        api_scheme = OPENFGA_API_SCHEME, # optional, defaults to "https"
        api_host = OPENFGA_API_HOST, # required, define without the scheme (e.g. api.fga.example instead of https://api.fga.example)
        store_id = OPENFGA_STORE_ID, # optional, not needed when calling `CreateStore` or `ListStores`
        authorization_model_id = OPENFGA_AUTHORIZATION_MODEL_ID, # Optional, can be overridden per request
        credentials = Credentials(
            method='client_credentials',
            configuration=CredentialConfiguration(
                api_issuer= OPENFGA_API_TOKEN_ISSUER,
                api_audience= OPENFGA_API_AUDIENCE,
                client_id= OPENFGA_CLIENT_ID,
                client_secret= OPENFGA_CLIENT_SECRET,
            )
        )
    )
    # Enter a context with an instance of the OpenFgaClient
    async with OpenFgaClient(configuration) as fga_client:
        api_response = await fga_client.read_authorization_models()
        await fga_client.close()
```
**Backtrace (if any)**

```
<backtrace>
```

**Expected behavior**
A clear and concise description of what you expected to happen.

**Additional context**
Add any other context about the problem here.
