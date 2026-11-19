# Administration draft 0.3.0

Work for [content #5](https://github.com/SysKata-project/content/issues/5).
Original SysKata lessons for a bounded pilot aligned to DO280, not full course
coverage, course reproduction or exam preparation. No curriculum release exists.

| New lesson | Measurable outcome | Estimate | Exercises |
| --- | --- | --- | --- |
| [oc-declarative](oc-declarative.md) | Apply manifests and verify observed state | 12 min | 4 |
| [oc-rbac](oc-rbac.md) | Grant scoped access and verify allowed/denied operations | 12 min | 4 |
| [oc-budgets](oc-budgets.md) | Configure a quota and explain admission denial | 12 min | 4 |

Estimates include reading and practice; they are not measured learner timings.
Each exercise has a hint, misconception feedback, official 4.22 references and
positive/negative fixtures. The command evaluator's literal limits are explicit.

This new draft includes unchanged foundations lesson content from 0.2.0 to keep
all lesson/skill/unit prerequisites resolvable. It adds three lessons and 12
exercises, for seven lessons and 28 exercises total. The foundations draft remains
unchanged. Preserve the 2026-11-04 curriculum source baseline, separate from the
new reference review date and any actual runtime version.

[Checkpoint B](checkpoint/README.md) specifies setup, reset, scoped identities,
manifest/RBAC/quota criteria and alternate-valid/negative scenarios. Its live
proof remains [pending](checkpoint/VALIDATION.md). `tested_versions` is empty for
this combined draft; foundations-only evidence does not validate administration.

## Validate and compile

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_sources.py
.venv/bin/python scripts/compile_bundle.py build drafts/0.3.0/catalog.yaml \
  --cases drafts/0.3.0/assessment-cases.json --output dist/administration-build
```

Choose a fresh output directory. The compiler produces separate learner and
assessment artifacts with `release_eligible: false`. CI discovers the new draft.
Do not publish, activate, or use this text-only catalog to unlock administration
or declare pilot completion. Neither checkpoint is represented by a fixture lab
adapter. Production integration must enforce trusted checkpoint A before
`oc-declarative` and checkpoint B before pilot completion.

The [owner decision](DECISIONS.md) allows review after authored-content checks
and live scoped-identity proof; it defers production integration to labs #3.
Local tests passing alone do not satisfy the live proof requirement.

## Recorded local validation

On 2026-11-19: all 40 unit tests passed, including all 28 exercise fixture sets,
answer separation, manifest evidence and quota/error classification. Schema fixture,
Python syntax, local Markdown links, whitespace and secret scans passed. All catalog
reference checks passed with TLS verification using `SSL_CERT_FILE=/etc/ssl/cert.pem`
after a transient HTTP 503 retry. Live
checkpoint execution remains blocked by test-cluster API DNS resolution.
