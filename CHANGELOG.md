# Changelog

## v0.2.0

### [0.2.0](https://github.com/openfga/python-sdk/compare/v0.1.1...v0.2.0) (2023-05-25)

Changes:
- [BREAKING] feat!: `schema_version` is now required when calling `write_authorization_model`
- [BREAKING] chore!: drop support for python < 3.10
- feat(client): add OpenFgaClient wrapper see [docs](https://github.com/openfga/python-sdk/tree/main#readme), see the `v0.1.1` docs for [the OpenFgaApi docs](https://github.com/openfga/python-sdk/tree/v0.1.1#readme)
- feat(client): implement `batch_check` to check multiple tuples in parallel
- feat(client): implement `list_relations` to check in one call whether a user has multiple relations to an objects
- feat(client): add support for a non-transactional `write`
- feat(validation): ensure storeId and authorizationModelId are in valid ulid format
- chore(config): bump default max retries to `15`
- chore(deps): upgrade dependencies

## v0.1.1

### [0.1.1](https://github.com/openfga/python-sdk/compare/v0.1.0...v0.1.1) (2023-01-17)

- chore(deps): upgrade dependencies

## v0.1.0

### [0.1.0](https://github.com/openfga/python-sdk/compare/v0.0.1...v0.1.0) (2022-12-14)

Updated to include support for [OpenFGA 0.3.0](https://github.com/openfga/openfga/releases/tag/v0.3.0)

Changes:
- [BREAKING] feat(list-objects)!: response has been changed to include the object type
    e.g. response that was `{"object_ids":["roadmap"]}`, will now be `{"objects":["document:roadmap"]}`

Fixes:
- fix(models): update interfaces that had incorrectly optional fields to make them required


## v0.0.1

### [0.0.1](https://github.com/openfga/python-sdk/releases/tag/v0.0.1) (2022-08-31)

Initial OpenFGA Python SDK release
- Support for [OpenFGA](https://github.com/openfga/openfga) API
  - CRUD stores
  - Create, read & list authorization models
  - Writing and Reading Tuples
  - Checking authorization
  - Using Expand to understand why access was granted
