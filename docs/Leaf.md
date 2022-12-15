# Leaf

A leaf node contains either - a set of users (which may be individual users, or usersets   referencing other relations) - a computed node, which is the result of a computed userset   value in the authorization model - a tupleToUserset nodes, containing the result of expanding   a tupleToUserset value in a authorization model.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**users** | [**Users**](Users.md) |  | [optional] 
**computed** | [**Computed**](Computed.md) |  | [optional] 
**tuple_to_userset** | [**UsersetTreeTupleToUserset**](UsersetTreeTupleToUserset.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


