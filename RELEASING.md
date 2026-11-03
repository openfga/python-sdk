# Release guide

This project uses [release-please](https://github.com/googleapis/release-please) via a
`workflow_dispatch`-triggered GitHub Actions workflow. This document explains how to cut
a release and what to watch out for.

---

## Versioning rules for this project

We are pre-1.0.0. Semver conventions are relaxed:

| Change type      | Bump                  | Example              |
|---               |---                    |---                   |
| Breaking change  | **Minor** (`0.x.0`)   | `0.10.0` → `0.11.0` |
| Everything else  | **Patch** (`0.0.x`)   | `0.10.0` → `0.10.1` |

Major bumps (`1.0.0`) are reserved for a deliberate stable-API graduation decision — not for
routine breaking changes.

---

## Cutting a release

1. Go to **Actions → release-please** and click **Run workflow**.
2. Choose a bump type:
   - `auto` — bump determined from the conventional commits since the last release (default)
   - `patch` — bugfixes, docs, small changes
   - `minor` — breaking changes (see above)
   - `explicit` — uses the exact version entered in `release-version` (e.g. `0.11.0` or
     `0.11.0-beta.1`); the other bump types ignore that field
3. The workflow creates a release PR. It is built from `main` at dispatch time and not
   refreshed — if anything else merges to `main` first, close it and re-run the workflow.
   Review it, then merge.
4. On merge, CI pushes a signed `vX.Y.Z` tag and a draft GitHub release; the tag build
   publishes to PyPI and then undrafts the release. If the release stays a draft, check
   that run.

> **Note — release-please only understands `auto` or an explicit version string.**
> The `patch`, `minor`, and `major` options in the workflow dropdown are conveniences
> implemented in the workflow. The workflow reads the current manifest version, computes
> the next version (e.g. `0.10.0` + patch = `0.10.1`), and passes that computed string
> to release-please as an explicit `Release-As:` commit — exactly the same as choosing
> `explicit` and typing it yourself. There is no native patch/minor/major mode in
> release-please. This is why `explicit` is always the safest option when in doubt —
> you are just skipping the arithmetic step.

---

## When to use `explicit`

Use `explicit` and type the version yourself in any of these situations:

**After a beta or non-conventional tag.**
If the previous release was something like `0.10.0-beta.1`, release-please tracks the
base semver (`0.10.0`) but cannot reliably decide whether the next release should be
`0.10.0`, `0.10.1`, or `0.11.0`. It will often guess wrong.

The rule of thumb: **if the last tag had a pre-release suffix, always use `explicit` for
the next release.**

**After a manually created tag.**
Any tag created outside of the release-please workflow (e.g. hotfixes, manual git tags)
is invisible to release-please's version logic. Use `explicit` to anchor the next version
correctly.

**When you want a beta.**
Release-please does not increment pre-release suffixes automatically. Use `explicit` for
every beta, incrementing the suffix manually:
```
0.11.0-beta.1  →  explicit: 0.11.0-beta.2  →  explicit: 0.11.0
```

There is also a `release-please-develop` lane that cuts pre-releases from the `develop`
branch — sync `develop` with `main` first. A version like `0.11.0-beta.1` appears on
PyPI as `0.11.0b1`.

---

## What goes in the changelog

Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/)
for release-please to group them correctly:

```
feat: add support for batch check          → Added
fix: correct retry logic for transient errors  → Fixed
docs: update API reference                 → Documentation
perf: cache DNS lookups                    → Changed
refactor: extract auth helper               → Changed
chore: bump dependencies                   → (hidden)
```

### Overriding a changelog entry

If a commit message isn't user-facing, add this block to the PR description (before or
after merging; re-run the release workflow to pick it up). release-please uses it instead
of the commit message:

```
BEGIN_COMMIT_OVERRIDE
feat: user-facing description of the change
END_COMMIT_OVERRIDE
```

### Breaking changes

Mark the type with `!` and add a `BREAKING CHANGE:` footer. PRs are squash-merged, and a
single-commit PR's squash title defaults to the commit title, not the PR title. Put the `!`
in both, and check the squash dialog shows it and the footer before merging:

```
feat!: remove the Foo option

BREAKING CHANGE: the Foo option has been removed. Use Bar instead.
```

---

## Troubleshooting

**"Invalid previous_tag parameter" error.**
The manifest version does not have a corresponding GitHub Release object. Reset the
manifest to the last valid tag:
```bash
echo '{ ".": "0.x.y" }' > .release-please-manifest.json
git commit -am "chore: reset manifest to v0.x.y"
git push origin main
```

**Duplicate release PRs.**
Close all stale ones. The workflow auto-closes stale open PRs on each dispatch, but
merged duplicates need manual labelling with `autorelease: tagged`.

**Changelog shows everything ungrouped.**
Make sure `changelog-type` in `release-please-config.json` is set to `"default"`, not
`"github"`.
