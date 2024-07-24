# CheckRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tuple_key** | [**CheckRequestTupleKey**](CheckRequestTupleKey.md) |  | 
**contextual_tuples** | [**ContextualTupleKeys**](ContextualTupleKeys.md) |  | [optional] 
**authorization_model_id** | **str** |  | [optional] 
**trace** | **bool** | Defaults to false. Making it true has performance implications. | [optional] [readonly] 
**context** | **object** | Additional request context that will be used to evaluate any ABAC conditions encountered in the query evaluation. | [optional] 
**consistency** | [**ConsistencyPreference**](ConsistencyPreference.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


