# Changelog

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
