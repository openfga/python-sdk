# openfga_sdk.OpenFgaApi

All URIs are relative to *api.fga.example*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch_check**](OpenFgaApi.md#batch_check) | **POST** /stores/{store_id}/batch-check | Send a list of &#x60;check&#x60; operations in a single request
[**check**](OpenFgaApi.md#check) | **POST** /stores/{store_id}/check | Check whether a user is authorized to access an object
[**create_store**](OpenFgaApi.md#create_store) | **POST** /stores | Create a store
[**delete_store**](OpenFgaApi.md#delete_store) | **DELETE** /stores/{store_id} | Delete a store
[**expand**](OpenFgaApi.md#expand) | **POST** /stores/{store_id}/expand | Expand all relationships in userset tree format, and following userset rewrite rules.  Useful to reason about and debug a certain relationship
[**get_store**](OpenFgaApi.md#get_store) | **GET** /stores/{store_id} | Get a store
[**list_objects**](OpenFgaApi.md#list_objects) | **POST** /stores/{store_id}/list-objects | List all objects of the given type that the user has a relation with
[**list_stores**](OpenFgaApi.md#list_stores) | **GET** /stores | List all stores
[**list_users**](OpenFgaApi.md#list_users) | **POST** /stores/{store_id}/list-users | List the users matching the provided filter who have a certain relation to a particular type.
[**read**](OpenFgaApi.md#read) | **POST** /stores/{store_id}/read | Get tuples from the store that matches a query, without following userset rewrite rules
[**read_assertions**](OpenFgaApi.md#read_assertions) | **GET** /stores/{store_id}/assertions/{authorization_model_id} | Read assertions for an authorization model ID
[**read_authorization_model**](OpenFgaApi.md#read_authorization_model) | **GET** /stores/{store_id}/authorization-models/{id} | Return a particular version of an authorization model
[**read_authorization_models**](OpenFgaApi.md#read_authorization_models) | **GET** /stores/{store_id}/authorization-models | Return all the authorization models for a particular store
[**read_changes**](OpenFgaApi.md#read_changes) | **GET** /stores/{store_id}/changes | Return a list of all the tuple changes
[**streamed_list_objects**](OpenFgaApi.md#streamed_list_objects) | **POST** /stores/{store_id}/streamed-list-objects | Stream all objects of the given type that the user has a relation with
[**write**](OpenFgaApi.md#write) | **POST** /stores/{store_id}/write | Add or delete tuples from the store
[**write_assertions**](OpenFgaApi.md#write_assertions) | **PUT** /stores/{store_id}/assertions/{authorization_model_id} | Upsert assertions for an authorization model ID
[**write_authorization_model**](OpenFgaApi.md#write_authorization_model) | **POST** /stores/{store_id}/authorization-models | Create a new authorization model


# **batch_check**
> BatchCheckResponse batch_check(body)

Send a list of `check` operations in a single request

The `BatchCheck` API functions nearly identically to `Check`, but instead of checking a single user-object relationship BatchCheck accepts a list of relationships to check and returns a map containing `BatchCheckItem` response for each check it received.  An associated `correlation_id` is required for each check in the batch. This ID is used to correlate a check to the appropriate response. It is a string consisting of only alphanumeric characters or hyphens with a maximum length of 36 characters. This `correlation_id` is used to map the result of each check to the item which was checked, so it must be unique for each item in the batch. We recommend using a UUID or ULID as the `correlation_id`, but you can use whatever unique identifier you need as long  as it matches this regex pattern: `^[\\w\\d-]{1,36}$`  NOTE: The maximum number of checks that can be passed in the `BatchCheck` API is configurable via the [OPENFGA_MAX_CHECKS_PER_BATCH_CHECK](https://openfga.dev/docs/getting-started/setup-openfga/configuration#OPENFGA_MAX_CHECKS_PER_BATCH_CHECK) environment variable. If `BatchCheck` is called using the SDK, the SDK can split the batch check requests for you.  For more details on how `Check` functions, see the docs for `/check`.  ### Examples #### A BatchCheckRequest ```json {   \"checks\": [      {        \"tuple_key\": {          \"object\": \"document:2021-budget\"          \"relation\": \"reader\",          \"user\": \"user:anne\",        },        \"contextual_tuples\": {...}        \"context\": {}        \"correlation_id\": \"01JA8PM3QM7VBPGB8KMPK8SBD5\"      },      {        \"tuple_key\": {          \"object\": \"document:2021-budget\"          \"relation\": \"reader\",          \"user\": \"user:bob\",        },        \"contextual_tuples\": {...}        \"context\": {}        \"correlation_id\": \"01JA8PMM6A90NV5ET0F28CYSZQ\"      }    ] } ```  Below is a possible response to the above request. Note that the result map's keys are the `correlation_id` values from the checked items in the request: ```json {    \"result\": {      \"01JA8PMM6A90NV5ET0F28CYSZQ\": {        \"allowed\": false,         \"error\": {\"message\": \"\"}      },      \"01JA8PM3QM7VBPGB8KMPK8SBD5\": {        \"allowed\": true,         \"error\": {\"message\": \"\"}      } } ``` 

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
    body = openfga_sdk.BatchCheckRequest() # BatchCheckRequest | 

    try:
        # Send a list of `check` operations in a single request
        api_response = await api_instance.api_instance.batch_check(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->batch_check: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BatchCheckRequest**](BatchCheckRequest.md)|  |

### Return type

[**BatchCheckResponse**](BatchCheckResponse.md)

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **check**
> CheckResponse check(body)

Check whether a user is authorized to access an object

The Check API returns whether a given user has a relationship with a given object in a given store. The `user` field of the request can be a specific target, such as `user:anne`, or a userset (set of users) such as `group:marketing#member` or a type-bound public access `user:*`. To arrive at a result, the API uses: an authorization model, explicit tuples written through the Write API, contextual tuples present in the request, and implicit tuples that exist by virtue of applying set theory (such as `document:2021-budget#viewer@document:2021-budget#viewer`; the set of users who are viewers of `document:2021-budget` are the set of users who are the viewers of `document:2021-budget`). A `contextual_tuples` object may also be included in the body of the request. This object contains one field `tuple_keys`, which is an array of tuple keys. Each of these tuples may have an associated `condition`. You may also provide an `authorization_model_id` in the body. This will be used to assert that the input `tuple_key` is valid for the model specified. If not specified, the assertion will be made against the latest authorization model ID. It is strongly recommended to specify authorization model id for better performance. You may also provide a `context` object that will be used to evaluate the conditioned tuples in the system. It is strongly recommended to provide a value for all the input parameters of all the conditions, to ensure that all tuples be evaluated correctly. By default, the Check API caches results for a short time to optimize performance. You may specify a value of `HIGHER_CONSISTENCY` for the optional `consistency` parameter in the body to inform the server that higher conisistency is preferred at the expense of increased latency. Consideration should be given to the increased latency if requesting higher consistency. The response will return whether the relationship exists in the field `allowed`.  Some exceptions apply, but in general, if a Check API responds with `{allowed: true}`, then you can expect the equivalent ListObjects query to return the object, and viceversa.  For example, if `Check(user:anne, reader, document:2021-budget)` responds with `{allowed: true}`, then `ListObjects(user:anne, reader, document)` may include `document:2021-budget` in the response. ## Examples ### Querying with contextual tuples In order to check if user `user:anne` of type `user` has a `reader` relationship with object `document:2021-budget` given the following contextual tuple ```json {   \"user\": \"user:anne\",   \"relation\": \"member\",   \"object\": \"time_slot:office_hours\" } ``` the Check API can be used with the following request body: ```json {   \"tuple_key\": {     \"user\": \"user:anne\",     \"relation\": \"reader\",     \"object\": \"document:2021-budget\"   },   \"contextual_tuples\": {     \"tuple_keys\": [       {         \"user\": \"user:anne\",         \"relation\": \"member\",         \"object\": \"time_slot:office_hours\"       }     ]   },   \"authorization_model_id\": \"01G50QVV17PECNVAHX1GG4Y5NC\" } ``` ### Querying usersets Some Checks will always return `true`, even without any tuples. For example, for the following authorization model ```python model   schema 1.1 type user type document   relations     define reader: [user] ``` the following query ```json {   \"tuple_key\": {      \"user\": \"document:2021-budget#reader\",      \"relation\": \"reader\",      \"object\": \"document:2021-budget\"   } } ``` will always return `{ \"allowed\": true }`. This is because usersets are self-defining: the userset `document:2021-budget#reader` will always have the `reader` relation with `document:2021-budget`. ### Querying usersets with difference in the model A Check for a userset can yield results that must be treated carefully if the model involves difference. For example, for the following authorization model ```python model   schema 1.1 type user type group   relations     define member: [user] type document   relations     define blocked: [user]     define reader: [group#member] but not blocked ``` the following query ```json {   \"tuple_key\": {      \"user\": \"group:finance#member\",      \"relation\": \"reader\",      \"object\": \"document:2021-budget\"   },   \"contextual_tuples\": {     \"tuple_keys\": [       {         \"user\": \"user:anne\",         \"relation\": \"member\",         \"object\": \"group:finance\"       },       {         \"user\": \"group:finance#member\",         \"relation\": \"reader\",         \"object\": \"document:2021-budget\"       },       {         \"user\": \"user:anne\",         \"relation\": \"blocked\",         \"object\": \"document:2021-budget\"       }     ]   }, } ``` will return `{ \"allowed\": true }`, even though a specific user of the userset `group:finance#member` does not have the `reader` relationship with the given object. ### Requesting higher consistency By default, the Check API caches results for a short time to optimize performance. You may request higher consistency to inform the server that higher consistency should be preferred at the expense of increased latency. Care should be taken when requesting higher consistency due to the increased latency. ```json {   \"tuple_key\": {      \"user\": \"group:finance#member\",      \"relation\": \"reader\",      \"object\": \"document:2021-budget\"   },   \"consistency\": \"HIGHER_CONSISTENCY\" } ``` 

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **expand**
> ExpandResponse expand(body)

Expand all relationships in userset tree format, and following userset rewrite rules.  Useful to reason about and debug a certain relationship

The Expand API will return all users and usersets that have certain relationship with an object in a certain store. This is different from the `/stores/{store_id}/read` API in that both users and computed usersets are returned. Body parameters `tuple_key.object` and `tuple_key.relation` are all required. A `contextual_tuples` object may also be included in the body of the request. This object contains one field `tuple_keys`, which is an array of tuple keys. Each of these tuples may have an associated `condition`. The response will return a tree whose leaves are the specific users and usersets. Union, intersection and difference operator are located in the intermediate nodes.  ## Example To expand all users that have the `reader` relationship with object `document:2021-budget`, use the Expand API with the following request body ```json {   \"tuple_key\": {     \"object\": \"document:2021-budget\",     \"relation\": \"reader\"   },   \"authorization_model_id\": \"01G50QVV17PECNVAHX1GG4Y5NC\" } ``` OpenFGA's response will be a userset tree of the users and usersets that have read access to the document. ```json {   \"tree\":{     \"root\":{       \"type\":\"document:2021-budget#reader\",       \"union\":{         \"nodes\":[           {             \"type\":\"document:2021-budget#reader\",             \"leaf\":{               \"users\":{                 \"users\":[                   \"user:bob\"                 ]               }             }           },           {             \"type\":\"document:2021-budget#reader\",             \"leaf\":{               \"computed\":{                 \"userset\":\"document:2021-budget#writer\"               }             }           }         ]       }     }   } } ``` The caller can then call expand API for the `writer` relationship for the `document:2021-budget`. ### Expand Request with Contextual Tuples  Given the model ```python model     schema 1.1  type user  type folder     relations         define owner: [user]  type document     relations         define parent: [folder]         define viewer: [user] or writer         define writer: [user] or owner from parent ``` and the initial tuples ```json [{     \"user\": \"user:bob\",     \"relation\": \"owner\",     \"object\": \"folder:1\" }] ```  To expand all `writers` of `document:1` when `document:1` is put in `folder:1`, the first call could be  ```json {   \"tuple_key\": {     \"object\": \"document:1\",     \"relation\": \"writer\"   },   \"contextual_tuples\": {     \"tuple_keys\": [       {         \"user\": \"folder:1\",         \"relation\": \"parent\",         \"object\": \"document:1\"       }     ]   } } ``` this returns: ```json {   \"tree\": {     \"root\": {       \"name\": \"document:1#writer\",       \"union\": {         \"nodes\": [           {             \"name\": \"document:1#writer\",             \"leaf\": {               \"users\": {                 \"users\": []               }             }           },           {             \"name\": \"document:1#writer\",             \"leaf\": {               \"tupleToUserset\": {                 \"tupleset\": \"document:1#parent\",                 \"computed\": [                   {                     \"userset\": \"folder:1#owner\"                   }                 ]               }             }           }         ]       }     }   } } ``` This tells us that the `owner` of `folder:1` may also be a writer. So our next call could be to find the `owners` of `folder:1` ```json {   \"tuple_key\": {     \"object\": \"folder:1\",     \"relation\": \"owner\"   } } ``` which gives ```json {   \"tree\": {     \"root\": {       \"name\": \"folder:1#owner\",       \"leaf\": {         \"users\": {           \"users\": [             \"user:bob\"           ]         }       }     }   } } ``` 

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_objects**
> ListObjectsResponse list_objects(body)

List all objects of the given type that the user has a relation with

The ListObjects API returns a list of all the objects of the given type that the user has a relation with.  To arrive at a result, the API uses: an authorization model, explicit tuples written through the Write API, contextual tuples present in the request, and implicit tuples that exist by virtue of applying set theory (such as `document:2021-budget#viewer@document:2021-budget#viewer`; the set of users who are viewers of `document:2021-budget` are the set of users who are the viewers of `document:2021-budget`). An `authorization_model_id` may be specified in the body. If it is not specified, the latest authorization model ID will be used. It is strongly recommended to specify authorization model id for better performance. You may also specify `contextual_tuples` that will be treated as regular tuples. Each of these tuples may have an associated `condition`. You may also provide a `context` object that will be used to evaluate the conditioned tuples in the system. It is strongly recommended to provide a value for all the input parameters of all the conditions, to ensure that all tuples be evaluated correctly. By default, the Check API caches results for a short time to optimize performance. You may specify a value of `HIGHER_CONSISTENCY` for the optional `consistency` parameter in the body to inform the server that higher conisistency is preferred at the expense of increased latency. Consideration should be given to the increased latency if requesting higher consistency. The response will contain the related objects in an array in the \"objects\" field of the response and they will be strings in the object format `<type>:<id>` (e.g. \"document:roadmap\"). The number of objects in the response array will be limited by the execution timeout specified in the flag OPENFGA_LIST_OBJECTS_DEADLINE and by the upper bound specified in the flag OPENFGA_LIST_OBJECTS_MAX_RESULTS, whichever is hit first. The objects given will not be sorted, and therefore two identical calls can give a given different set of objects.

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
        # List all objects of the given type that the user has a relation with
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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_stores**
> ListStoresResponse list_stores()

List all stores

Returns a paginated list of OpenFGA stores and a continuation token to get additional stores. The continuation token will be empty if there are no more stores. 

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
    name = 'name_example' # str | The name parameter instructs the API to only include results that match that name.Multiple results may be returned. Only exact matches will be returned; substring matches and regexes will not be evaluated (optional)

    try:
        # List all stores
        api_response = await api_instance.api_instance.list_stores(page_size=page_size, continuation_token=continuation_token, name=name)
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
 **name** | **str**| The name parameter instructs the API to only include results that match that name.Multiple results may be returned. Only exact matches will be returned; substring matches and regexes will not be evaluated | [optional]

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_users**
> ListUsersResponse list_users(body)

List the users matching the provided filter who have a certain relation to a particular type.

The ListUsers API returns a list of all the users of a specific type that have a relation to a given object.  To arrive at a result, the API uses: an authorization model, explicit tuples written through the Write API, contextual tuples present in the request, and implicit tuples that exist by virtue of applying set theory (such as `document:2021-budget#viewer@document:2021-budget#viewer`; the set of users who are viewers of `document:2021-budget` are the set of users who are the viewers of `document:2021-budget`). An `authorization_model_id` may be specified in the body. If it is not specified, the latest authorization model ID will be used. It is strongly recommended to specify authorization model id for better performance. You may also specify `contextual_tuples` that will be treated as regular tuples. Each of these tuples may have an associated `condition`. You may also provide a `context` object that will be used to evaluate the conditioned tuples in the system. It is strongly recommended to provide a value for all the input parameters of all the conditions, to ensure that all tuples be evaluated correctly. The response will contain the related users in an array in the \"users\" field of the response. These results may include specific objects, usersets  or type-bound public access. Each of these types of results is encoded in its own type and not represented as a string.In cases where a type-bound public access result is returned (e.g. `user:*`), it cannot be inferred that all subjects of that type have a relation to the object; it is possible that negations exist and checks should still be queried on individual subjects to ensure access to that document.The number of users in the response array will be limited by the execution timeout specified in the flag OPENFGA_LIST_USERS_DEADLINE and by the upper bound specified in the flag OPENFGA_LIST_USERS_MAX_RESULTS, whichever is hit first. The returned users will not be sorted, and therefore two identical calls may yield different sets of users.

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
    body = openfga_sdk.ListUsersRequest() # ListUsersRequest | 

    try:
        # List the users matching the provided filter who have a certain relation to a particular type.
        api_response = await api_instance.api_instance.list_users(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->list_users: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ListUsersRequest**](ListUsersRequest.md)|  |

### Return type

[**ListUsersResponse**](ListUsersResponse.md)

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read**
> ReadResponse read(body)

Get tuples from the store that matches a query, without following userset rewrite rules

The Read API will return the tuples for a certain store that match a query filter specified in the body of the request.  The API doesn't guarantee order by any field.  It is different from the `/stores/{store_id}/expand` API in that it only returns relationship tuples that are stored in the system and satisfy the query.  In the body: 1. `tuple_key` is optional. If not specified, it will return all tuples in the store. 2. `tuple_key.object` is mandatory if `tuple_key` is specified. It can be a full object (e.g., `type:object_id`) or type only (e.g., `type:`). 3. `tuple_key.user` is mandatory if tuple_key is specified in the case the `tuple_key.object` is a type only. If tuple_key.user is specified, it needs to be a full object (e.g., `type:user_id`). ## Examples ### Query for all objects in a type definition To query for all objects that `user:bob` has `reader` relationship in the `document` type definition, call read API with body of ```json {  \"tuple_key\": {      \"user\": \"user:bob\",      \"relation\": \"reader\",      \"object\": \"document:\"   } } ``` The API will return tuples and a continuation token, something like ```json {   \"tuples\": [     {       \"key\": {         \"user\": \"user:bob\",         \"relation\": \"reader\",         \"object\": \"document:2021-budget\"       },       \"timestamp\": \"2021-10-06T15:32:11.128Z\"     }   ],   \"continuation_token\": \"eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==\" } ``` This means that `user:bob` has a `reader` relationship with 1 document `document:2021-budget`. Note that this API, unlike the List Objects API, does not evaluate the tuples in the store. The continuation token will be empty if there are no more tuples to query. ### Query for all stored relationship tuples that have a particular relation and object To query for all users that have `reader` relationship with `document:2021-budget`, call read API with body of  ```json {   \"tuple_key\": {      \"object\": \"document:2021-budget\",      \"relation\": \"reader\"    } } ``` The API will return something like  ```json {   \"tuples\": [     {       \"key\": {         \"user\": \"user:bob\",         \"relation\": \"reader\",         \"object\": \"document:2021-budget\"       },       \"timestamp\": \"2021-10-06T15:32:11.128Z\"     }   ],   \"continuation_token\": \"eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==\" } ``` This means that `document:2021-budget` has 1 `reader` (`user:bob`).  Note that, even if the model said that all `writers` are also `readers`, the API will not return writers such as `user:anne` because it only returns tuples and does not evaluate them. ### Query for all users with all relationships for a particular document To query for all users that have any relationship with `document:2021-budget`, call read API with body of  ```json {   \"tuple_key\": {       \"object\": \"document:2021-budget\"    } } ``` The API will return something like  ```json {   \"tuples\": [     {       \"key\": {         \"user\": \"user:anne\",         \"relation\": \"writer\",         \"object\": \"document:2021-budget\"       },       \"timestamp\": \"2021-10-05T13:42:12.356Z\"     },     {       \"key\": {         \"user\": \"user:bob\",         \"relation\": \"reader\",         \"object\": \"document:2021-budget\"       },       \"timestamp\": \"2021-10-06T15:32:11.128Z\"     }   ],   \"continuation_token\": \"eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==\" } ``` This means that `document:2021-budget` has 1 `reader` (`user:bob`) and 1 `writer` (`user:anne`). 

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_assertions**
> ReadAssertionsResponse read_assertions(authorization_model_id)

Read assertions for an authorization model ID

The ReadAssertions API will return, for a given authorization model id, all the assertions stored for it. 

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_authorization_models**
> ReadAuthorizationModelsResponse read_authorization_models()

Return all the authorization models for a particular store

The ReadAuthorizationModels API will return all the authorization models for a certain store. OpenFGA's response will contain an array of all authorization models, sorted in descending order of creation.  ## Example Assume that a store's authorization model has been configured twice. To get all the authorization models that have been created in this store, call GET authorization-models. The API will return a response that looks like: ```json {   \"authorization_models\": [     {       \"id\": \"01G50QVV17PECNVAHX1GG4Y5NC\",       \"type_definitions\": [...]     },     {       \"id\": \"01G4ZW8F4A07AKQ8RHSVG9RW04\",       \"type_definitions\": [...]     },   ],   \"continuation_token\": \"eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==\" } ``` If there are no more authorization models available, the `continuation_token` field will be empty ```json {   \"authorization_models\": [     {       \"id\": \"01G50QVV17PECNVAHX1GG4Y5NC\",       \"type_definitions\": [...]     },     {       \"id\": \"01G4ZW8F4A07AKQ8RHSVG9RW04\",       \"type_definitions\": [...]     },   ],   \"continuation_token\": \"\" } ``` 

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_changes**
> ReadChangesResponse read_changes()

Return a list of all the tuple changes

The ReadChanges API will return a paginated list of tuple changes (additions and deletions) that occurred in a given store, sorted by ascending time. The response will include a continuation token that is used to get the next set of changes. If there are no changes after the provided continuation token, the same token will be returned in order for it to be used when new changes are recorded. If the store never had any tuples added or removed, this token will be empty. You can use the `type` parameter to only get the list of tuple changes that affect objects of that type. When reading a write tuple change, if it was conditioned, the condition will be returned. When reading a delete tuple change, the condition will NOT be returned regardless of whether it was originally conditioned or not. 

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
    start_time = '2013-10-20T19:20:30+01:00' # datetime | Start date and time of changes to read. Format: ISO 8601 timestamp (e.g., 2022-01-01T00:00:00Z) If a continuation_token is provided along side start_time, the continuation_token will take precedence over start_time. (optional)

    try:
        # Return a list of all the tuple changes
        api_response = await api_instance.api_instance.read_changes(type=type, page_size=page_size, continuation_token=continuation_token, start_time=start_time)
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
 **start_time** | **datetime**| Start date and time of changes to read. Format: ISO 8601 timestamp (e.g., 2022-01-01T00:00:00Z) If a continuation_token is provided along side start_time, the continuation_token will take precedence over start_time. | [optional]

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **streamed_list_objects**
> StreamResultOfStreamedListObjectsResponse streamed_list_objects(body)

Stream all objects of the given type that the user has a relation with

The Streamed ListObjects API is very similar to the the ListObjects API, with two differences:  1. Instead of collecting all objects before returning a response, it streams them to the client as they are collected.  2. The number of results returned is only limited by the execution timeout specified in the flag OPENFGA_LIST_OBJECTS_DEADLINE.  

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
        # Stream all objects of the given type that the user has a relation with
        api_response = await api_instance.api_instance.streamed_list_objects(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling OpenFgaApi->streamed_list_objects: %s\n" % e)
    await api_client.close()
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ListObjectsRequest**](ListObjectsRequest.md)|  |

### Return type

[**StreamResultOfStreamedListObjectsResponse**](StreamResultOfStreamedListObjectsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response.(streaming responses) |  -  |
**400** | Request failed due to invalid input. |  -  |
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **write**
> object write(body)

Add or delete tuples from the store

The Write API will transactionally update the tuples for a certain store. Tuples and type definitions allow OpenFGA to determine whether a relationship exists between an object and an user. In the body, `writes` adds new tuples and `deletes` removes existing tuples. When deleting a tuple, any `condition` specified with it is ignored. The API is not idempotent by default: if, later on, you try to add the same tuple key (even if the `condition` is different), or if you try to delete a non-existing tuple, it will throw an error. To allow writes when an identical tuple already exists in the database, set `\"on_duplicate\": \"ignore\"` on the `writes` object. To allow deletes when a tuple was already removed from the database, set `\"on_missing\": \"ignore\"` on the `deletes` object. If a Write request contains both idempotent (ignore) and non-idempotent (error) operations, the most restrictive action (error) will take precedence. If a condition fails for a sub-request with an error flag, the entire transaction will be rolled back. This gives developers explicit control over the atomicity of the requests. The API will not allow you to write tuples such as `document:2021-budget#viewer@document:2021-budget#viewer`, because they are implicit. An `authorization_model_id` may be specified in the body. If it is, it will be used to assert that each written tuple (not deleted) is valid for the model specified. If it is not specified, the latest authorization model ID will be used. ## Example ### Adding relationships To add `user:anne` as a `writer` for `document:2021-budget`, call write API with the following  ```json {   \"writes\": {     \"tuple_keys\": [       {         \"user\": \"user:anne\",         \"relation\": \"writer\",         \"object\": \"document:2021-budget\"       }     ],     \"on_duplicate\": \"ignore\"   },   \"authorization_model_id\": \"01G50QVV17PECNVAHX1GG4Y5NC\" } ``` ### Removing relationships To remove `user:bob` as a `reader` for `document:2021-budget`, call write API with the following  ```json {   \"deletes\": {     \"tuple_keys\": [       {         \"user\": \"user:bob\",         \"relation\": \"reader\",         \"object\": \"document:2021-budget\"       }     ],     \"on_missing\": \"ignore\"   } } ``` 

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **write_assertions**
> write_assertions(authorization_model_id, body)

Upsert assertions for an authorization model ID

The WriteAssertions API will upsert new assertions for an authorization model id, or overwrite the existing ones. An assertion is an object that contains a tuple key, the expectation of whether a call to the Check API of that tuple key will return true or false, and optionally a list of contextual tuples.

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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
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
**401** | Not authenticated. |  -  |
**403** | Forbidden. |  -  |
**404** | Request failed due to incorrect path. |  -  |
**409** | Request was aborted due a transaction conflict. |  -  |
**422** | Request timed out due to excessive request throttling. |  -  |
**500** | Request failed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

