# Content schema 1.0.0

Implements [content #1](https://github.com/SysKata-project/content/issues/1).
This is a schema and validation contract, not released curriculum or a bundle
compiler. Publication, manifests, hashes and evaluator capability negotiation
remain in [content #2](https://github.com/SysKata-project/content/issues/2).

## Validate locally

Use Python 3.13 and the pinned validation dependencies:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_content.py fixtures/valid/catalog.json
git diff --check
sh scripts/scan-secrets.sh history
```

The `Content validation / validate` CI job runs the same tests and catalog
validation. Existing secret-scanning CI remains separate. No coverage threshold
or additional merge rule is established by this content issue.

## Source and schema

[JSON Schema](../schemas/1.0.0/catalog.schema.json) uses
[Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core).
The validator enables date/URI format checking explicitly using
[python-jsonschema](https://python-jsonschema.readthedocs.io/en/stable/validate/).
Each definition under `$defs` can validate an individual entity. The root
validates a catalog containing `schema_version`, `bundle_version`, and `entities`.
Unknown fields and exercise variants fail validation.

YAML metadata and Markdown prose remain the authoring baseline. JSON fixtures
represent the data model after YAML parsing; the YAML loader and Markdown file
resolution belong to the compiler issue. Markdown fields here hold text, not
filesystem paths. Never execute authored command strings during validation.

| Definition | Relationships and required metadata |
| --- | --- |
| journey | Ordered units, locale, prerequisites, source, runtime |
| unit | Ordered lessons, prerequisites, source |
| lesson | Exercise pool, objectives with skills, prerequisites, duration, explanation, review prompt, source |
| skill | Stable meaning, prerequisites, source |
| reference | HTTPS URL, title, source baseline, reviewed date |
| single_choice | Options with local IDs and one correct option ID |
| command_order | Steps with local IDs and a complete answer permutation |
| command_entry | Explicit accepted command forms and normalization version |
| lab_task | Environment/setup profiles, reset generation semantics, runtime, observable evaluator checks |

Every entity has a globally unique stable `id` and positive integer `revision`.
Objective IDs are globally unique and cannot overlap entity IDs. Option, step
and hint IDs are unique within their exercise. Prerequisites point to the same
entity kind (lesson to lesson, skill to skill, and so on) and are acyclic;
empty arrays explicitly mean none. Cross-level prerequisite policies must be
modeled at the relevant level rather than by mixing entity types. Ordered unit
and lesson arrays express presentation order; exercise arrays are pools.

Exercises require skills, objective IDs, prompts, nonempty hints, source
metadata, versioned evaluators, completion evidence, misconception feedback,
reference IDs and reveal text. Each lesson objective must have an exercise;
linked exercises must target that lesson's objectives and include their skills.
This supports objective-based completion without encoding XP or review timing
in content. Those policies remain owned by the API and
[ADR 0002](https://github.com/SysKata-project/docs/blob/main/decisions/0002-learning-policy.md).

Lab checks require distinct criterion IDs, evaluator/version and parameters,
with feedback covering every criterion. Parameter objects are evaluator-specific;
the compiler must validate supported evaluator capabilities and their parameter
schemas before release. Profile IDs are external labs registry references, not
catalog entity IDs. Their existence and compatibility require labs integration.
The assigned project and identity come from the authorized session, never an
authored or learner-supplied override. `new-generation` reset invalidates prior
lab result generations; enforcement belongs to API/labs.

Runtime metadata separates the OpenShift 4.22 curriculum baseline from actual
`tested_versions`. Empty tested versions are allowed in drafts and fixtures;
they are never evidence of runtime compatibility. Release validation must reject
unverified lab content. All supplied examples use fixture evaluators/profiles
and do not claim to implement or validate a real OpenShift checkpoint.

## Command semantics: literal-command-v1

Command-entry exercises compare text against explicit accepted forms. The only
normalization is removing leading/trailing ASCII spaces. Reject empty input,
ASCII control characters (including tabs/newlines) and DEL. Preserve internal
spaces, case, quoting, escaping, flags and their order, pipes, redirects,
substitutions and operators exactly. No shell execution, token reordering,
quote removal, alias inference, Unicode normalization or flag equivalence occurs.

For example, ` oc get pods ` matches `oc get pods`; `oc get pod` matches only
when separately authored. `oc get pods --all-namespaces`, `oc get "pods"` and
`oc get pods; whoami` do not match `oc get pods`. This intentionally conservative
policy may require several explicit alternatives; outcome-based tasks belong
in labs. Any broader semantic normalization requires a new evaluator/version
and positive/negative fixtures proving which transformations preserve meaning.

## Learner and assessment projections

`scripts/validate_content.py:projections` is an executable reference for the
compiler contract. It first validates the catalog and returns independent
copies of an allowlisted learner catalog and the complete trusted catalog.
The learner copy includes presentation fields, options/steps, source/runtime
metadata and hint IDs. It excludes all assessment definitions, correct answers,
feedback, evaluator parameters, setup/environment profile IDs, reveal text and
hint bodies. Unknown source fields fail validation instead of leaking through.

Hints and reveals must be served by the authenticated API with assistance
recorded on the current attempt, not downloaded in question payloads. Feedback
is delivered after assessment. The trusted catalog retains the originals for
that purpose. Do not serve trusted artifacts as learner assets. Public source
is inspectable; this separation prevents accidental answer delivery and does
not promise exam secrecy. Author review must also catch answers accidentally
written into prompts, option labels, source titles or other public prose.

## Versions and immutability

- Schema versions use semantic versioning. Breaking structure, required fields
  or semantics require a major version; additive compatible contracts require
  a minor version; clarifications without acceptance changes use a patch.
  Since this schema rejects unknown fields, adding a field is not automatically
  compatible with old readers: publish a new schema and deploy compatible
  readers before activation. This validator accepts exactly 1.0.0.
- Increment entity revision for any authored change, including feedback or
  answer changes. Never recycle a stable ID or change the meaning of a skill
  under its existing ID. A changed skill meaning needs a new ID and an explicit
  progress migration decision. Cosmetic edits retain the stable ID.
- Bundle versions identify immutable snapshots, including schema and every
  entity/evaluator revision. Once released, never replace bytes under that
  version or remove a snapshot needed by active sessions or historical results.
  Corrections create a new bundle version. Compiler release checks must enforce
  this against the release registry; a standalone catalog cannot prove history.
- Sessions and attempts pin schema, bundle, exercise, evaluator and policy
  versions. Rollback selects a prior bundle for new sessions; it does not mutate
  prior attempts or earned progress. Retain old schema readers as needed.

## Evidence and limitations

`fixtures/valid` includes a connected catalog and individual examples of all
nine definitions. `fixtures/invalid` includes one rejected example per
definition. Tests also reject duplicate IDs, broken/wrong-kind references,
cycles, impossible dates, unsupported fields, bad choice/order answers,
uncovered objectives, and incomplete lab feedback. Projection tests check
answer exclusion and copy isolation; command tests cover quoting, flags,
operators, whitespace and controls.

Real evaluator execution, curriculum link freshness, YAML loading, artifact
publication and OpenShift runtime testing are outside this issue. Before
release, the compiler and labs issues must supply those checks and evidence.

Local validation on 2026-11-05: all 16 tests passed with Python 3.13.0;
the connected catalog validated; local documentation links, whitespace and
full-history secret scanning passed. GitHub reported no classic protection
on `main`; this change adds CI but does not change repository merge settings.
