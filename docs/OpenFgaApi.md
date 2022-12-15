# openfga_sdk.OpenFgaApi

All URIs are relative to *api.fga.example*

Method | HTTP request | Description
------------- | ------------- | -------------
[**check**](OpenFgaApi.md#check) | **POST** /stores/{store_id}/check | Check whether a user is authorized to access an object
[**create_store**](OpenFgaApi.md#create_store) | **POST** /stores | Create a store
[**delete_store**](OpenFgaApi.md#delete_store) | **DELETE** /stores/{store_id} | Delete a store
[**expand**](OpenFgaApi.md#expand) | **POST** /stores/{store_id}/expand | Expand all relationships in userset tree format, and following userset rewrite rules.  Useful to reason about and debug a certain relationship
[**get_store**](OpenFgaApi.md#get_store) | **GET** /stores/{store_id} | Get a store
[**list_objects**](OpenFgaApi.md#list_objects) | **POST** /stores/{store_id}/list-objects | [EXPERIMENTAL] Get all object ids of the given type that the user has a relation with
[**list_stores**](OpenFgaApi.md#list_stores) | **GET** /stores | List all stores
[**read**](OpenFgaApi.md#read) | **POST** /stores/{store_id}/read | Get tuples from the store that matches a query, without following userset rewrite rules
[**read_assertions**](OpenFgaApi.md#read_assertions) | **GET** /stores/{store_id}/assertions/{authorization_model_id} | Read assertions for an authorization model ID
[**read_authorization_model**](OpenFgaApi.md#read_authorization_model) | **GET** /stores/{store_id}/authorization-models/{id} | Return a particular version of an authorization model
[**read_authorization_models**](OpenFgaApi.md#read_authorization_models) | **GET** /stores/{store_id}/authorization-models | Return all the authorization models for a particular store
[**read_changes**](OpenFgaApi.md#read_changes) | **GET** /stores/{store_id}/changes | Return a list of all the tuple changes
[**write**](OpenFgaApi.md#write) | **POST** /stores/{store_id}/write | Add or delete tuples from the store
[**write_assertions**](OpenFgaApi.md#write_assertions) | **PUT** /stores/{store_id}/assertions/{authorization_model_id} | Upsert assertions for an authorization model ID
[**write_authorization_model**](OpenFgaApi.md#write_authorization_model) | **POST** /stores/{store_id}/authorization-models | Create a new authorization model


# **check**
> CheckResponse check(body)

Check whether a user is authorized to access an object

The Check API queries to check if the user has a certain relationship with an object in a certain store. A `contextual_tuples` object may also be included in the body of the request. This object contains one field `tuple_keys`, which is an array of tuple keys. You may also provide an `authorization_model_id` in the body. This will be used to assert that the input `tuple_key` is valid for the model specified. If not specified, the assertion will be made against the latest authorization model ID. The response will return whether the relationship exists in the field `allowed`.  ## Example In order to check if user `user:anne` of type `user` has a `reader` relationship with object `document:2021-budget` given the following contextual tuple ```json {   \"user\": \"user:anne\",   \"relation\": \"member\",   \"object\": \"time_slot:office_hours\" } ``` the Check API can be used with the following request body: ```json {   \"tuple_key\": {     \"user\": \"user:anne\",     \"relation\": \"reader\",     \"object\": \"document:2021-budget\"   },   \"contextual_tuples\": {     \"tuple_keys\": [       {         \"user\": \"user:anne\",         \"relation\": \"member\",         \"object\": \"time_slot:office_hours\"       }     ]   } } ``` OpenFGA's response will include `{ \"allowed\": true }` if there is a relationship and `{ \"allowed\": false }` if there isn't.

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    body = openfga_sdk.CheckRequest() # CheckRequest | 

    try:
        # Check whether a user is authorized to access an object
        api_response = await api_instance.api_instance.check(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->check: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CheckRequest**](CheckRequest.md)|  |

### Return type

[**CheckResponse**](CheckResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_store**
> CreateStoreResponse create_store(body)

Create a store

Create a unique OpenFGA store which will be used to store authorization models and relationship tuples.

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    body = openfga_sdk.CreateStoreRequest() # CreateStoreRequest | 

    try:
        # Create a store
        api_response = await api_instance.api_instance.create_store(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->create_store: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CreateStoreRequest**](CreateStoreRequest.md)|  |

### Return type

[**CreateStoreResponse**](CreateStoreResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_store**
> delete_store()

Delete a store

Delete an OpenFGA store. This does not delete the data associated with the store, like tuples or authorization models.

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)

    try:
        # Delete a store
        await api_instance.api_instance.delete_store()
    except ApiException as e:
        print("Exception when calling OpenFgaApi->delete_store: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **expand**
> ExpandResponse expand(body)

Expand all relationships in userset tree format, and following userset rewrite rules.  Useful to reason about and debug a certain relationship

The Expand API will return all users and usersets that have certain relationship with an object in a certain store. This is different from the `/stores/{store_id}/read` API in that both users and computed usersets are returned. Body parameters `tuple_key.object` and `tuple_key.relation` are all required. The response will return a tree whose leaves are the specific users and usersets. Union, intersection and difference operator are located in the intermediate nodes.  ## Example To expand all users that have the `reader` relationship with object `document:2021-budget`, use the Expand API with the following request body ```json {   \"tuple_key\": {     \"object\": \"document:2021-budget\",     \"relation\": \"reader\"   } } ``` OpenFGA's response will be a userset tree of the users and usersets that have read access to the document. ```json {   \"tree\":{     \"root\":{       \"type\":\"document:2021-budget#reader\",       \"union\":{         \"nodes\":[           {             \"type\":\"document:2021-budget#reader\",             \"leaf\":{               \"users\":{                 \"users\":[                   \"user:bob\"                 ]               }             }           },           {             \"type\":\"document:2021-budget#reader\",             \"leaf\":{               \"computed\":{                 \"userset\":\"document:2021-budget#writer\"               }             }           }         ]       }     }   } } ``` The caller can then call expand API for the `writer` relationship for the `document:2021-budget`.

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    body = openfga_sdk.ExpandRequest() # ExpandRequest | 

    try:
        # Expand all relationships in userset tree format, and following userset rewrite rules.  Useful to reason about and debug a certain relationship
        api_response = await api_instance.api_instance.expand(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->expand: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ExpandRequest**](ExpandRequest.md)|  |

### Return type

[**ExpandResponse**](ExpandResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_store**
> GetStoreResponse get_store()

Get a store

Returns an OpenFGA store by its identifier

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)

    try:
        # Get a store
        api_response = await api_instance.api_instance.get_store()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->get_store: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

### Return type

[**GetStoreResponse**](GetStoreResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_objects**
> ListObjectsResponse list_objects(body)

[EXPERIMENTAL] Get all object ids of the given type that the user has a relation with

The ListObjects API returns a list of all the objects of the given type that the user has a relation with. To achieve this, both the store tuples and the authorization model are used. An `authorization_model_id` may be specified in the body. If it is, it will be used to decide the underlying implementation used. If it is not specified, the latest authorization model ID will be used. You may also specify `contextual_tuples` that will be treated as regular tuples. 

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    body = openfga_sdk.ListObjectsRequest() # ListObjectsRequest | 

    try:
        # [EXPERIMENTAL] Get all object ids of the given type that the user has a relation with
        api_response = await api_instance.api_instance.list_objects(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->list_objects: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ListObjectsRequest**](ListObjectsRequest.md)|  |

### Return type

[**ListObjectsResponse**](ListObjectsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stores**
> ListStoresResponse list_stores()

List all stores

Returns a paginated list of OpenFGA stores.

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    page_size = 56 # int |  (optional)
    continuation_token = 'continuation_token_example' # str |  (optional)

    try:
        # List all stores
        api_response = await api_instance.api_instance.list_stores(page_size=page_size, continuation_token=continuation_token)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->list_stores: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | [optional]
 **continuation_token** | **str**|  | [optional]

### Return type

[**ListStoresResponse**](ListStoresResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read**
> ReadResponse read(body)

Get tuples from the store that matches a query, without following userset rewrite rules

The Read API will return the tuples for a certain store that match a query filter specified in the body of the request. It is different from the `/stores/{store_id}/expand` API in that it only returns relationship tuples that are stored in the system and satisfy the query.  In the body: 1. tuple_key is optional.  If tuple_key is not specified, it will return all tuples in the store.2. `tuple_key.object` is mandatory if tuple_key is specified. It can be a full object (e.g., `type:object_id`) or type only (e.g., `type:`). 3. `tuple_key.user` is mandatory if tuple_key is specified in the case the `tuple_key.object` is a type only. ## Examples ### Query for all objects in a type definition To query for all objects that `user:bob` has `reader` relationship in the document type definition, call read API with body of ```json {  \"tuple_key\": {      \"user\": \"user:bob\",      \"relation\": \"reader\",      \"object\": \"document:\"   } } ``` The API will return tuples and an optional continuation token, something like ```json {   \"tuples\": [     {       \"key\": {         \"user\": \"user:bob\",         \"relation\": \"reader\",         \"object\": \"document:2021-budget\"       },       \"timestamp\": \"2021-10-06T15:32:11.128Z\"     }   ] } ``` This means that `user:bob` has a `reader` relationship with 1 document `document:2021-budget`. ### Query for all stored relationship tuples that have a particular relation and object To query for all users that have `reader` relationship with `document:2021-budget`, call read API with body of  ```json {   \"tuple_key\": {      \"object\": \"document:2021-budget\",      \"relation\": \"reader\"    } } ``` The API will return something like  ```json {   \"tuples\": [     {       \"key\": {         \"user\": \"user:bob\",         \"relation\": \"reader\",         \"object\": \"document:2021-budget\"       },       \"timestamp\": \"2021-10-06T15:32:11.128Z\"     }   ] } ``` This means that `document:2021-budget` has 1 `reader` (`user:bob`).  Note that the API will not return writers such as `user:anne` even when all writers are readers.  This is because only direct relationship are returned for the READ API. ### Query for all users with all relationships for a particular document To query for all users that have any relationship with `document:2021-budget`, call read API with body of  ```json {   \"tuple_key\": {       \"object\": \"document:2021-budget\"    } } ``` The API will return something like  ```json {   \"tuples\": [     {       \"key\": {         \"user\": \"user:anne\",         \"relation\": \"writer\",         \"object\": \"document:2021-budget\"       },       \"timestamp\": \"2021-10-05T13:42:12.356Z\"     },     {       \"key\": {         \"user\": \"user:bob\",         \"relation\": \"reader\",         \"object\": \"document:2021-budget\"       },       \"timestamp\": \"2021-10-06T15:32:11.128Z\"     }   ] } ``` This means that `document:2021-budget` has 1 `reader` (`user:bob`) and 1 `writer` (`user:anne`). 

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    body = openfga_sdk.ReadRequest() # ReadRequest | 

    try:
        # Get tuples from the store that matches a query, without following userset rewrite rules
        api_response = await api_instance.api_instance.read(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->read: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ReadRequest**](ReadRequest.md)|  |

### Return type

[**ReadResponse**](ReadResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_assertions**
> ReadAssertionsResponse read_assertions(authorization_model_id)

Read assertions for an authorization model ID

The ReadAssertions API will return, for a given authorization model id, all the assertions stored for it. An assertion is an object that contains a tuple key, and the expectation of whether a call to the Check API of that tuple key will return true or false. 

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    authorization_model_id = 'authorization_model_id_example' # str | 

    try:
        # Read assertions for an authorization model ID
        api_response = await api_instance.api_instance.read_assertions(authorization_model_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->read_assertions: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization_model_id** | **str**|  |

### Return type

[**ReadAssertionsResponse**](ReadAssertionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_authorization_model**
> ReadAuthorizationModelResponse read_authorization_model(id)

Return a particular version of an authorization model

The ReadAuthorizationModel API returns an authorization model by its identifier. The response will return the authorization model for the particular version.  ## Example To retrieve the authorization model with ID `01G5JAVJ41T49E9TT3SKVS7X1J` for the store, call the GET authorization-models by ID API with `01G5JAVJ41T49E9TT3SKVS7X1J` as the `id` path parameter.  The API will return: ```json {   \"authorization_model\":{     \"id\":\"01G5JAVJ41T49E9TT3SKVS7X1J\",     \"type_definitions\":[       {         \"type\":\"user\"       },       {         \"type\":\"document\",         \"relations\":{           \"reader\":{             \"union\":{               \"child\":[                 {                   \"this\":{}                 },                 {                   \"computedUserset\":{                     \"object\":\"\",                     \"relation\":\"writer\"                   }                 }               ]             }           },           \"writer\":{             \"this\":{}           }         }       }     ]   } } ``` In the above example, there are 2 types (`user` and `document`). The `document` type has 2 relations (`writer` and `reader`).

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    id = 'id_example' # str | 

    try:
        # Return a particular version of an authorization model
        api_response = await api_instance.api_instance.read_authorization_model(id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->read_authorization_model: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |

### Return type

[**ReadAuthorizationModelResponse**](ReadAuthorizationModelResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_authorization_models**
> ReadAuthorizationModelsResponse read_authorization_models()

Return all the authorization models for a particular store

The ReadAuthorizationModels API will return all the authorization models for a certain store. OpenFGA's response will contain an array of all authorization models, sorted in descending order of creation.  ## Example Assume that a store's authorization model has been configured twice. To get all the authorization models that have been created in this store, call GET authorization-models. The API will return a response that looks like: ```json {   \"authorization_models\": [     {       \"id\": \"01G50QVV17PECNVAHX1GG4Y5NC\",       \"type_definitions\": [...]     },     {       \"id\": \"01G4ZW8F4A07AKQ8RHSVG9RW04\",       \"type_definitions\": [...]     },   ] } ``` If there are more authorization models available, the response will contain an extra field `continuation_token`: ```json {   \"authorization_models\": [     {       \"id\": \"01G50QVV17PECNVAHX1GG4Y5NC\",       \"type_definitions\": [...]     },     {       \"id\": \"01G4ZW8F4A07AKQ8RHSVG9RW04\",       \"type_definitions\": [...]     },   ],   \"continuation_token\": \"eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==\" } ``` 

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    page_size = 56 # int |  (optional)
    continuation_token = 'continuation_token_example' # str |  (optional)

    try:
        # Return all the authorization models for a particular store
        api_response = await api_instance.api_instance.read_authorization_models(page_size=page_size, continuation_token=continuation_token)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->read_authorization_models: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | [optional]
 **continuation_token** | **str**|  | [optional]

### Return type

[**ReadAuthorizationModelsResponse**](ReadAuthorizationModelsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_changes**
> ReadChangesResponse read_changes()

Return a list of all the tuple changes

The ReadChanges API will return a paginated list of tuple changes (additions and deletions) that occurred in a given store, sorted by ascending time. The response will include a continuation token that is used to get the next set of changes. If there are no changes after the provided continuation token, the same token will be returned in order for it to be used when new changes are recorded. If the store never had any tuples added or removed, this token will be empty. You can use the `type` parameter to only get the list of tuple changes that affect objects of that type. 

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    type = 'type_example' # str |  (optional)
    page_size = 56 # int |  (optional)
    continuation_token = 'continuation_token_example' # str |  (optional)

    try:
        # Return a list of all the tuple changes
        api_response = await api_instance.api_instance.read_changes(type=type, page_size=page_size, continuation_token=continuation_token)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->read_changes: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type** | **str**|  | [optional]
 **page_size** | **int**|  | [optional]
 **continuation_token** | **str**|  | [optional]

### Return type

[**ReadChangesResponse**](ReadChangesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **write**
> object write(body)

Add or delete tuples from the store

The Write API will update the tuples for a certain store. Tuples and type definitions allow OpenFGA to determine whether a relationship exists between an object and an user. In the body, `writes` adds new tuples while `deletes` removes existing tuples. The API is not idempotent: if, later on, you try to add the same tuple, or if you try to delete a non-existing tuple, it will throw an error. An `authorization_model_id` may be specified in the body. If it is, it will be used to assert that each written tuple (not deleted) is valid for the model specified. If it is not specified, the latest authorization model ID will be used. ## Example ### Adding relationships To add `user:anne` as a `writer` for `document:2021-budget`, call write API with the following  ```json {   \"writes\": {     \"tuple_keys\": [       {         \"user\": \"user:anne\",         \"relation\": \"writer\",         \"object\": \"document:2021-budget\"       }     ]   } } ``` ### Removing relationships To remove `user:bob` as a `reader` for `document:2021-budget`, call write API with the following  ```json {   \"deletes\": {     \"tuple_keys\": [       {         \"user\": \"user:bob\",         \"relation\": \"reader\",         \"object\": \"document:2021-budget\"       }     ]   } } ``` 

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    body = openfga_sdk.WriteRequest() # WriteRequest | 

    try:
        # Add or delete tuples from the store
        api_response = await api_instance.api_instance.write(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->write: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WriteRequest**](WriteRequest.md)|  |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **write_assertions**
> write_assertions(authorization_model_id, body)

Upsert assertions for an authorization model ID

The WriteAssertions API will upsert new assertions for an authorization model id, or overwrite the existing ones. An assertion is an object that contains a tuple key, and the expectation of whether a call to the Check API of that tuple key will return true or false. 

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    authorization_model_id = 'authorization_model_id_example' # str | 
    body = openfga_sdk.WriteAssertionsRequest() # WriteAssertionsRequest | 

    try:
        # Upsert assertions for an authorization model ID
        await api_instance.api_instance.write_assertions(authorization_model_id, body)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->write_assertions: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization_model_id** | **str**|  |
 **body** | [**WriteAssertionsRequest**](WriteAssertionsRequest.md)|  |

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **write_authorization_model**
> WriteAuthorizationModelResponse write_authorization_model(body)

Create a new authorization model

The WriteAuthorizationModel API will add a new authorization model to a store. Each item in the `type_definitions` array is a type definition as specified in the field `type_definition`. The response will return the authorization model's ID in the `id` field.  ## Example To add an authorization model with `user` and `document` type definitions, call POST authorization-models API with the body:  ```json {   \"type_definitions\":[     {       \"type\":\"user\"     },     {       \"type\":\"document\",       \"relations\":{         \"reader\":{           \"union\":{             \"child\":[               {                 \"this\":{}               },               {                 \"computedUserset\":{                   \"object\":\"\",                   \"relation\":\"writer\"                 }               }             ]           }         },         \"writer\":{           \"this\":{}         }       }     }   ] } ``` OpenFGA's response will include the version id for this authorization model, which will look like  ``` {\"authorization_model_id\": \"01G50QVV17PECNVAHX1GG4Y5NC\"} ``` 

### Example

```python
import time
import openfga_sdk
from openfga_sdk.rest import ApiException
from pprint import pprint
# To configure the configuration
# host is mandatory
# api_scheme is optional and default to https
# store_id is mandatory
# See configuration.py for a list of all supported configuration parameters.
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
)


# When authenticating via the API TOKEN method
credentials = Credentials(method='api_token', configuration=CredentialConfiguration(api_token='TOKEN1'))
configuration = openfga_sdk.Configuration(
    scheme = "https",
    api_host = "api.fga.example",
    store_id = 'YOUR_STORE_ID',
    credentials = credentials
)

# Enter a context with an instance of the API client
async with openfga_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openfga_sdk.OpenFgaApi(api_client)
    body = openfga_sdk.WriteAuthorizationModelRequest() # WriteAuthorizationModelRequest | 

    try:
        # Create a new authorization model
        api_response = await api_instance.api_instance.write_authorization_model(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->write_authorization_model: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WriteAuthorizationModelRequest**](WriteAuthorizationModelRequest.md)|  |

### Return type

[**WriteAuthorizationModelResponse**](WriteAuthorizationModelResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | A successful response. |  -  |
**400** | Request failed due to invalid input. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

