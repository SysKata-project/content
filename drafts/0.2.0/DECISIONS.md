# Content #4 acceptance boundary

Accepted by the project owner on 2026-11-17: once the four lessons compile and
the checkpoint passes live runtime testing, submit content #4 for review.
Production evaluator integration and content activation remain gated on labs #3.

This corrects the earlier draft's circular blocker: labs #3 explicitly depends
on content #4 and #5. It does not waive live curriculum testing or authorize a
release. The content deliverable is authored lessons, validated text-exercise
fixtures, checkpoint setup/reset and outcome specifications, and a reproducible
scoped-identity runtime proof. The checkpoint specification is not presented as
a production compiled lab exercise. The lesson-only catalog remains a non-release
draft; moving it into `releases/` and activating it requires the full integration.

The temporary proof role can add the scoped diagnostic reads needed to test
learner commands. Production role/lifecycle integration remains with labs #2.
Authenticated grading, stale-result rejection, reward deduplication and progression
must be implemented and verified in labs/API work before learner activation.

Approval of this boundary is not approval of a final code revision or authorization
to merge. Keep the issue open through review and merge, per AGENTS.md.
