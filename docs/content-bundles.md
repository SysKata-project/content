# Immutable content bundles

Implements [content #2](https://github.com/SysKata-project/content/issues/2).
The project owner selected GitHub Releases on 2026-11-07. Repository release
immutability was enabled and verified on that date. There are no curriculum
releases yet; examples under `fixtures/` remain test data.

## Author and review

Use Python 3.13 and `requirements-dev.txt`. A catalog is one YAML document with
the [schema 1.0.0](content-schema.md) structure. `!markdown explanation.md` loads
UTF-8 prose relative to the catalog directory. Duplicate YAML keys, unsafe tags,
missing files, absolute paths and paths/symlinks escaping that directory fail.
Dates remain ISO strings. Markdown is carried as text, never executed or rendered
by this compiler. Clients must render it safely. See the executable
[authoring example](../fixtures/authoring/catalog.yaml).

For a release, add `releases/<bundle-version>/catalog.yaml`, its Markdown files,
and `assessment-cases.json` in a reviewed PR. Commit every input, including prose.
The cases map each exercise ID to `{ "answer": ..., "expected": true/false }`
rows. Every exercise requires passing positive and negative cases. Validate:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_sources.py
.venv/bin/python scripts/compile_bundle.py build fixtures/authoring/catalog.yaml \
  --cases fixtures/authoring/assessment-cases.json --output dist
git diff --check
sh scripts/scan-secrets.sh history
```

`Content validation / validate` checks the existing schema fixtures plus all
release sources, graph/reference rules, assessment cases and live documentation
reference URLs. HTTPS requests must succeed with HTTP 200; network failures,
access denials and insecure final redirects fail the check. These checks validate
reference entities, not every URL appearing in arbitrary Markdown prose. Review
Markdown links, reference relevance, source baseline, original authorship and
public text for accidentally disclosed answers. Do not weaken validation to pass
a transient documentation outage; retry after the external cause is resolved.
On macOS Python installations lacking trusted roots, configure `SSL_CERT_FILE`
to an appropriate trusted CA bundle, such as `/etc/ssl/cert.pem`; never disable TLS.

Authors increment entity revisions for changed content and select a new bundle
version. Reviewers ensure stable skill meaning, backward compatibility and
curriculum correctness. Existing versions must remain available to historical
sessions. Real checkpoint review additionally needs labs runtime validation.

## Evaluators and release gates

| Evaluator / version | Semantics |
| --- | --- |
| `choice.exact` / 1 | Exact option ID equality |
| `order.exact` / 1 | Exact complete ordered step IDs |
| `command.literal` / 1 | `literal-command-v1` from the schema contract |

The API must explicitly implement these capabilities before activating a bundle;
a compiler capability does not prove API support. Compiler fixtures also support
`fixture.choice`, `fixture.order`, `fixture.command`, `fixture.lab` and
`fixture.pod-ready`, all version 1. The lab fixture checks supplied observations
against a validated parameter schema, never a cluster. It accepts only the
fixture environment/setup profiles. No authored command is executed.

Release mode rejects **every fixture evaluator**, unknown evaluator versions and
unsupported profiles/parameters. Production lab adapters and evidence validation
must be integrated with [labs #3](https://github.com/SysKata-project/labs/issues/3)
before releasing checkpoint content. Nonempty `tested_versions` alone cannot
bypass this gate. This compiler does not claim real OpenShift assessment.

## Artifact contract

Each bundle directory contains three canonical UTF-8 JSON files (sorted object
keys, compact separators, one final newline). Array order is preserved. Builds
from the same source commit and inputs produce identical bytes; no clock or
absolute paths are embedded.

- `learner.json`: allowlisted presentation catalog, including hint IDs but no
  hint bodies, answer keys, feedback, reveals, evaluator parameters or profiles.
- `assessment.json`: full trusted catalog for API/labs use, including assistance
  and assessment definitions. Never serve it as a mobile or web asset.
- `manifest.json`: manifest format version 1, schema/bundle versions, full source
  Git SHA, release eligibility, exact evaluator/version requirements, assessment
  fixture SHA-256, and each artifact's SHA-256, byte count and audience.

The manifest itself is pinned by SHA-256 in the release notes and API build
configuration; hashes establish integrity only when the manifest pin comes from
an approved release. The verifier checks both artifact hashes and recomputes the
learner projection, rejecting answer leakage even when artifact hashes match.
GitHub release immutability protects published bytes and tags; see
[GitHub's documentation](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes).
The repository and release assets are public: separation prevents accidental
answer delivery, not inspection of published assessment material.

## Publish and retain

After review and merge, manually run **Publish content** on `main` with the
reviewed bundle version. This is an explicit publication action, not a side effect
of opening or merging a PR. The workflow runs tests and history secret scanning,
requires clean tracked source, validates references, builds in release mode and
checks the source version against the requested version.

The publisher rebuilds the artifacts from the clean checkout before publishing,
requires source ancestry on `main`, checks immutable-release settings and reads
the complete release registry and matching tags. Any existing version, including
a draft or orphaned tag, is rejected. Network/authentication failures fail closed.
It uploads all three assets to a new draft `content-v<version>`, then publishes
and verifies GitHub's `immutable` flag. Publication runs serially and never uses
force, clobber, delete or asset-replacement operations.

If publication fails, inspect the draft/tag and workflow log. Do not overwrite
or automatically remove the partial release; use a new version after correcting
the cause. A published release is not rolled back by deletion. Retain all versions
needed by sessions and results. Administrators must keep immutability enabled
and preserve published releases; this workflow grants no deletion authority.

A local publish uses the same guards (requires `gh` authentication with repository
contents-write and access to the immutable-release setting):

```sh
.venv/bin/python scripts/compile_bundle.py build releases/1.0.0/catalog.yaml \
  --cases releases/1.0.0/assessment-cases.json --output dist --release
.venv/bin/python scripts/publish_bundle.py dist/1.0.0 \
  --manifest-sha256 <approved-manifest-sha256>
```

The versions above illustrate commands, not an existing release. The output
version directory is created exclusively; it will never overwrite an existing
local bundle either. Use a new empty output root for a reproducibility check.

## Package, activate and roll back

At API build time, download all three assets for a pinned tag:

```sh
gh release download content-v1.0.0 --repo SysKata-project/content \
  --pattern learner.json --pattern assessment.json --pattern manifest.json \
  --dir vendor/content/1.0.0
.venv/bin/python scripts/compile_bundle.py verify vendor/content/1.0.0 \
  --manifest-sha256 <approved-manifest-sha256>
```

Package the verified directory in the API image. Only expose the learner
projection through the authenticated API; keep the trusted file private within
server images. API activation must reject non-release bundles, unsupported
manifest/schema versions or missing evaluator capabilities. No GitHub call belongs
in the learning request path. Keep older bundles/readers packaged while sessions
or historical attempts reference them.

Rollback selects a previously verified bundled version for **new sessions**.
Existing sessions retain pinned schema, bundle, exercise, evaluator and policy
versions; progress and attempts are not rewritten. Breaking schema changes need
compatible readers deployed first. Stable skill meaning changes require new IDs
and an explicit progress migration decision.

## Validation boundaries

Unit tests cover deterministic builds, YAML/Markdown failures, answer separation,
assessment outcomes, capabilities, hash tampering, exclusive output creation,
HTTP failure behavior and simulated GitHub publication. Tests publish no releases.
The first real publication requires reviewed curriculum and validates GitHub
Actions token permissions and end-to-end release retrieval. No production
curriculum or lab runtime evidence is invented by this tooling issue.
