# Changelog

## [Unreleased](https://github.com/openfga/python-sdk/compare/v0.9.8...HEAD)

### [0.9.8](https://github.com/openfga/python-sdk/compare/v0.9.7...0.9.8) (2025-11-04)
- feat: add support for conflict options for Write operations: (#235)
  The client now supports setting `ConflictOptions` on `ClientWriteOptions` to control behavior when writing duplicate tuples or deleting non-existent tuples. This feature requires OpenFGA server [v1.10.0](https://github.com/openfga/openfga/releases/tag/v1.10.0) or later.
  See [Conflict Options for Write Operations](./README.md#conflict-options-for-write-operations) for more.
  - `on_duplicate` for handling duplicate tuple writes (ERROR or IGNORE)
  - `on_missing` for handling deletes of non-existent tuples (ERROR or IGNORE)

### [0.9.7](https://github.com/openfga/python-sdk/compare/v0.9.6...0.9.7) (2025-10-06)

- feat: `headers` configuration property (#233)
- fix: per-request custom header precedence (#230)

### [v0.9.6](https://github.com/openfga/python-sdk/compare/v0.9.5...v0.9.6) (2025-09-15)

- fix: reuse ssl context in the sync client (#222) - thanks @wadells!
- feat: add OAuth2 scopes parameter support to CredentialConfiguration (#213) - thanks @SoulPancake

### [v0.9.5](https://github.com/openfga/python-sdk/compare/v0.9.4...v0.9.5) (2025-07-09)

- fix: aiohttp.ClientResponse.data should be awaited (#197) - thanks @cmbernard333

### [0.9.4](https://github.com/openfga/python-sdk/compare/v0.9.3...0.9.4) (2025-04-30)

- feat: support List Stores name filter (#181)
- feat: fix and improve retries and rate limit handling. (#176) - thanks @GMorris-professional
  The SDK now respects the rate limit headers (`Retry-After`) returned by the server and will retry the request after the specified time.
  If the header is not sent or on network errors, it will fall back to exponential backoff.
- feat: allow more user customizations for the token issuer (#186) - thanks @manuel-lang
- fix: ListRelations should not swallow errors (#183)
- fix: urllib3 compatibility < v2 (#187)

### [0.9.3](https://github.com/openfga/python-sdk/compare/v0.9.2...v0.9.3) (2025-03-26)

- fix: urllib3 compatibility < v2 (#179)

### [0.9.2](https://github.com/openfga/python-sdk/compare/v0.9.1...v0.9.2) (2025-03-25)

- fix(telemetry): fixes for telemetry attributes and metrics tracking (#177)
- fix: REST client should not close after `stream` request (#172)

## v0.9.1

### [0.9.1](https://github.com/openfga/python-sdk/compare/v0.9.0...v0.9.1) (2025-01-23)

- feat: add `/streamed-list-objects` endpoint support (#163)
- feat: add `contextual_tuples` support for `/expand` endpoint requests (#164)

## v0.9.0

### [0.9.0](https://github.com/openfga/python-sdk/compare/v0.8.1...v0.9.0) (2024-12-19)

- feat: remove client-side validation - thanks @GMorris-professional (#155)
- feat: add support for `start_time` parameter in `ReadChanges` endpoint (#156) - Note, this feature requires v1.8.0 of OpenFGA or newer
- feat!: add support for `BatchCheck` API (#154) - Note, this feature requires v1.8.2 of OpenFGA or newer
- fix: change default max retry limit to 3 from 15 - thanks @ovindu-a (#155)

BREAKING CHANGE:

Usage of the existing batch_check should now use client_batch_check instead, additionally the existing
BatchCheckResponse has been renamed to ClientBatchCheckClientResponse.

Please see (#154)(https://github.com/openfga/python-sdk/pull/154) for more details on this change.

## v0.8.1

### [0.8.1](https://github.com/openfga/python-sdk/compare/v0.8.0...v0.8.1) (2024-11-26)

- feat: allow specifying a request timeout (#151) - thanks @Oscmage!

## v0.8.0

### [0.8.0](https://github.com/openfga/python-sdk/compare/v0.7.2...v0.8.0) (2024-11-15)

- feat: allow configuring the token endpoint (#137)
- feat: add per-HTTP request counter metric (#135)
- refactor: remove SDK version for OpenTelemetry meter name (#134)
- fix: only send SDK method header from SDK wrapper methods (#142)
- fix: unable to pass `retry_params` (#144)
- fix: list users should send contextual tuples as a list (#147)
- fix: handle no models existing in `read_latest_authorization_model` (#147)

## v0.7.2

### [0.7.2](https://github.com/openfga/python-sdk/compare/v0.7.1...v0.7.2) (2024-09-22)

This release includes improvements to the OpenTelemetry configuration API introduced in the previous releases

- refactor: improve OpenTelemetry configuration (#127)

This release also includes fixes for several bugs identified in previous releases:

- fix: ensure max_parallel_requests is an int value in batch_check (#132)
- fix: inconsistency in 429 handling between sync/async client (#131)
- fix: ensure telemetry is reported when API exceptions are raised (#127)

## v0.7.1

### [0.7.1](https://github.com/openfga/python-sdk/compare/v0.7.0...v0.7.1) (2024-09-16)

This release includes fixes for several bugs identified in the previous release related to OpenTelemetry metrics reporting: (#124)

- fix: attribute values are now correctly exported as their intended types (previously, these were all sent as string values)
- fix: `http_client_request_duration` being reported in seconds rather than the intended milliseconds
- fix: sync client mistakenly passing the entire configuration (rather than just the OpenTelemetry configuration as intended) to `queryDuration()` and `requestDuration()`
- fix: some attributes may not have been exported as expected under some conditions
- fix: `queryDuration()` and `requestDuration()` may not have updated their histograms reliably when `attr_http_client_request_duration` or `attr_http_server_request_duration` (respectively) were not enabled (which is the default)

Please note that if you use third-party OpenTelemetry tooling to visualize the attributes mentioned above, you may need to update your queries to account for these changes.

## v0.7.0

### [0.7.0](https://github.com/openfga/python-sdk/compare/v0.6.1...v0.7.0) (2024-08-30)

- feat: enhancements to OpenTelemetry support (#120)

Note this introduces some breaking changes to our metrics:

1. `fga-client.request.method` is now in TitleCase to match the naming conventions in the Protos, e.g. `Check`, `ListObjects`, etc..
2. Due to possible high costs for attributes with high cardinality, we are no longer including the following attributes by default:

- `fga-client.user`
- `http.client.request.duration`
- `http.server.request.duration`
  We added configuration options to allow you to set which specific metrics and attributes you care about in case the defaults don't work for your use-case

## v0.6.1

### [0.6.1](https://github.com/openfga/python-sdk/compare/v0.6.0...v0.6.1) (2024-07-31)

- feat: add support for specifying consistency when evaluating or reading (#129)
  Note: To use this feature, you need to be running OpenFGA v1.5.7+ with the experimental flag
  `enable-consistency-params` enabled. See the [v1.5.7 release notes](https://github.com/openfga/openfga/releases/tag/v1.5.7) for details.

- feat: add OpenTelemetry metrics reporting

## v0.6.0

### [0.6.0](https://github.com/openfga/python-sdk/compare/v0.5.0...v0.6.0) (2024-06-28)

- feat: add OpenTelemetry metrics reporting

## v0.5.0

### [0.5.0](https://github.com/openfga/python-sdk/compare/v0.4.2...v0.5.0) (2024-06-17)

- fix: ClientTuple condition property type
- fix: list_users should accept FgaObject type
- fix: remove ReadAuthorizationModel calls from BatchCheck and writes
- chore!: remove excluded users from ListUsers response

## v0.4.3

### [0.4.3](https://github.com/openfga/python-sdk/compare/v0.4.2...v0.4.3) (2024-06-07)

- feat: support for list users

## v0.4.2

### [0.4.2](https://github.com/openfga/python-sdk/compare/v0.4.1...v0.4.2) (2024-04-04)

- feat: support for modular models metadata
- feat: support auto-retry of failed network requests
- refactor: remove Python 2 code
- fix: limit the number of network retries
- fix: Configuration class `api_scheme`, `min_wait_in_ms` and `disabled_client_side_validations` validation issues
- chore: update aiohttp to 3.9.2
- chore: update black to 24.3.0

## v0.4.1

### [0.4.1](https://github.com/openfga/python-sdk/compare/v0.4.0...v0.4.1) (2024-02-13)

- feat: support `api_url` configuration option and deprecate `api_scheme` and `api_host`
- fix: use correct content type for token request

## v0.4.0

### [0.4.0](https://github.com/openfga/python-sdk/compare/v0.3.4...v0.4.0) (2024-01-11)

- feat: support for [conditions](https://openfga.dev/blog/conditional-tuples-announcement)
- chore!: use latest API interfaces for type info
- chore: add [example project](./example)
- chore: dependency updates

BREAKING CHANGES:
Note: This release comes with substantial breaking changes, especially to the interfaces due to the protobuf changes in the last release.

While the http interfaces did not break (you can still use `v0.3.3` SDK with a `v1.3.8+` server),
the grpc interface did and this caused a few changes in the interfaces of the SDK.

If you are using `OpenFgaClient`, the changes required should be smaller, if you are using `OpenFgaApi` a bit more changes will be needed.

You will have to modify some parts of your code, but we hope this will be to the better as a lot of the parameters are now correctly marked as required,
and so the Pointer-to-String conversion is no longer needed.

Some of the changes to expect:

- The following request interfaces changed:
  - `CheckRequest`: the `TupleKey` field is now of interface `CheckRequestTupleKey`, you can also now pass in `Context`
  - `ExpandRequest`: the `TupleKey` field is now of interface `ExpandRequestTupleKey`
  - `ReadRequest`: the `TupleKey` field is now of interface `ReadRequestTupleKey`
  - `WriteRequest`: now takes `WriteRequestWrites` and `WriteRequestDeletes`, the latter of which accepts `TupleKeyWithoutCondition`
  - And more
- The following interfaces had fields that were optional are are now required:
  - `CreateStoreResponse`
  - `GetStoreResponse`
  - `ListStoresResponse`
  - `ListObjectsResponse`
  - `ReadChangesResponse`
  - `ReadResponse`
  - `AuthorizationModel`
  - And more

Take a look at the changes in models in https://github.com/openfga/python-sdk/commit/9ed1f70d64db71451de2eb26e330bbd511625c5c and https://github.com/openfga/python-sdk/pull/59/files for more.

## v0.3.4

### [0.3.4](https://github.com/openfga/python-sdk/compare/v0.3.3...v0.3.4) (2024-01-09)

Note: `v0.3.4` has been re-released as `v0.4.0` due to breaking changes

## v0.3.3

### [0.3.3](https://github.com/openfga/python-sdk/compare/v0.3.2...v0.3.3) (2024-01-02)

- fix: correct type hints for list_relations
- fix: handle empty TupleKey in read
- chore: add example project

## v0.3.2

### [0.3.2](https://github.com/openfga/python-sdk/compare/v0.3.1...v0.3.2) (2023-12-15)

- feat: allow passing ssl certs to client configuration
- feat: setup openfga_sdk.help for bug info

## v0.3.1

### [0.3.1](https://github.com/openfga/python-sdk/compare/v0.3.0...v0.3.1) (2023-12-01)

- chore(deps): reduce min urllib3 to 1.25.11, add dependabot & bump deps

## v0.3.0

### [0.3.0](https://github.com/openfga/python-sdk/compare/v0.2.1...v0.3.0) (2023-11-02)

- feat(client): introduce synchronous OpenFgaClient (https://github.com/openfga/python-sdk/commit/c92b436543e263f2c1af6af15f1c4fda1c9dad21)
- refactor(config): extract oauth2 from credentials, removing logic from credentials configuration (https://github.com/openfga/python-sdk/commit/f91d14b25f86dd3f2e4d48229bb53cc7d9b20f1b)
- feat(client): performance improvements to batch_check (https://github.com/openfga/python-sdk/commit/d8f2d429d2c279c0e56d5ef2a6172df8bfadd82b)

## v0.2.1

### [0.2.1](https://github.com/openfga/python-sdk/compare/v0.2.0...v0.2.1) (2023-09-05)

- fix(client): fix a crash when calling check with contextual tuples (https://github.com/openfga/python-sdk/commit/dded83f9a75dc1f01c1cfbd8385a25654129f78f)
- chore(docs): update README and fix a few typos (https://github.com/openfga/python-sdk/pull/21, https://github.com/openfga/python-sdk/pull/31, https://github.com/openfga/python-sdk/pull/32, https://github.com/openfga/python-sdk/pull/33, https://github.com/openfga/python-sdk/pull/34, https://github.com/openfga/python-sdk/pull/37)

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
  e.g. response that was `{"object_ids":["roadmap"]}`, will now be `{"objects":["document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a"]}`

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
