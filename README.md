# SysKata content

Original learning material for SysKata's daily practice experience, primarily focused on Red Hat certification paths and practical Linux administration and automation skills.

## Intended scope

- Learning paths mapped to published certification objectives.
- Short lessons with clear prerequisites and measurable outcomes.
- Hands-on challenges that grow from individual commands to realistic tasks.
- Hints, explanatory feedback, and targeted review activities.
- Challenge setup requirements and outcome-based assessment criteria.

## Proposed lesson structure

A lesson should identify its stable ID, version, target skills, prerequisites, expected duration, explanation, practice instructions, hints, assessment criteria, and review prompts. Challenges should also identify the required environment and reset behavior. The machine-readable content schema remains to be designed.

## Authoring principles

- Write original material and realistic administrative scenarios.
- Explain why an approach works and how learners can correct mistakes.
- Assess resulting system behavior or state when multiple solutions are valid.
- Record the certification version and source objectives used for alignment.
- Keep examples reproducible and free of secrets or personal data.
- Do not include recalled, leaked, or copied certification exam questions.

## Component boundaries

This repository owns curriculum and challenge definitions. [Labs](https://github.com/SysKata-project/labs) owns environment execution and assessment tooling. The [API](https://github.com/SysKata-project/api) owns learner state, and [app](https://github.com/SysKata-project/app) owns presentation. Content delivery and versioning contracts will be documented in [docs](https://github.com/SysKata-project/docs).

## Proposed first milestone

Use OpenShift as the initial path, aligned to public DO180 and DO280 objectives. Define a minimal content schema and deliver the bounded pilot sequence with two assessable hands-on challenges. Validate the exercise in its target lab environment before marking it ready.

## Implementation design

- [Authoring and delivery](docs/authoring-and-delivery.md)
- [OpenShift DO180/DO280 journey](docs/openshift-path.md)

## Status and contribution

Planning scaffold only; the OpenShift DO180/DO280 curriculum plan is documented, but lessons and supported lab runtime versions are not yet validated. Open an issue with the target skill and intended learner outcome before proposing a learning path.

SysKata is independent and is not affiliated with or endorsed by Red Hat. Red Hat is a trademark of Red Hat, Inc.

## MVP implementation tracking

See the [OpenShift MVP tracker](https://github.com/SysKata-project/docs/issues/1) and [cross-repository backlog](https://github.com/SysKata-project/docs/blob/main/plans/mvp-backlog.md).

## License

Copyright 2026 SysKata contributors.

This repository, including its code, documentation, and learning content, is licensed under the [Apache License 2.0](LICENSE).
