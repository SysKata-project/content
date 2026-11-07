# Content authoring and delivery

Status: [JSON Schema and validation](content-schema.md) and the
[bundle compiler and publication workflow](content-bundles.md) are implemented.
Curriculum and production lab evaluator integration remain separate work.

## Source structure

Use YAML for structured metadata and Markdown for explanations. Proposed directories: journeys/, units/, lessons/, exercises/, skills/, references/, schemas/ and fixtures/. Each entity has a stable ID and revision; journey releases also have a bundle version and schema version. Store course/source baseline, reviewed date, locale, supported runtime, prerequisites, objectives, estimated duration and exercise pools. Skills are independent of XP levels.

Exercise types for MVP: single_choice, command_order, command_entry and lab_task. Each declares skills, prompt, hints, criterion/misconception feedback, documentation reference IDs, assessment type/version and completion evidence. Lab tasks additionally declare environment profile, setup, reset semantics and observable checks. Accepted command forms must preserve meaningful shell semantics; do not normalize away quoting or flags indiscriminately.

Example design (not a validated schema instance yet):

```yaml
id: openshift.workloads.ready
version: 1
type: lab_task
skills: [openshift.deployments]
environment: openshift-project-v1
prompt: Make the supplied web deployment available in your assigned project.
assessment:
  evaluator: openshift.deployment_available
  evaluator_version: 1
  parameters:
    deployment: web
    minimum_available_replicas: 1
feedback:
  deployment_unavailable:
    explanation: Inspect pod events and the deployment status to find the failing dependency.
    documentation_refs: [openshift-workloads]
```

The assigned project is resolved from the authorized lab session, never selected by an untrusted submitted path. A deployment check is one criterion; compound tasks must separately check routes, connectivity or permissions when those are objectives.

## Validation and publication

Compile source into immutable JSON artifacts with a manifest containing schema/bundle versions, source commit, content hash and required evaluator capabilities. Validate schema, duplicate IDs, dangling references, prerequisite cycles, supported types, learner payload separation and evaluator fixtures. Check links and source/runtime compatibility. Keep expected outcomes and positive/negative fixtures for every assessment.

Produce a learner projection without expected answers/check parameters and an assessment projection for trusted services. Public repository material is inspectable; do not claim hidden-exam security. Package bundles with the API for MVP. Retain old releases and pin sessions to their release; do not edit a released bundle in place.

Changes pass author review and assessment validation in the target environment. Activation/rollback is an API concern; curriculum migration must explicitly preserve earned progress or explain reassessment. Do not silently replace skill meaning under a stable ID.

See [OpenShift curriculum](openshift-path.md) and [shared architecture](https://github.com/SysKata-project/docs/blob/main/architecture/learning-platform.md).
