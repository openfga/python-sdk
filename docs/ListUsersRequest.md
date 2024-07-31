# ListUsersRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**authorization_model_id** | **str** |  | [optional] 
**object** | [**FgaObject**](FgaObject.md) |  | 
**relation** | **str** |  | 
**user_filters** | [**list[UserTypeFilter]**](UserTypeFilter.md) | The type of results returned. Only accepts exactly one value. | 
**contextual_tuples** | [**list[TupleKey]**](TupleKey.md) |  | [optional] 
**context** | **object** | Additional request context that will be used to evaluate any ABAC conditions encountered in the query evaluation. | [optional] 
**consistency** | [**ConsistencyPreference**](ConsistencyPreference.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


