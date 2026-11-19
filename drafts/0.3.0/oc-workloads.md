# Deploy and repair a workload

Estimated time: 12 minutes, including four practice exercises.
Prerequisite: Explain a workload symptom.

A Deployment describes a desired set of application pods. Its controller uses
ReplicaSets to reconcile actual state with that desired state. Deleting a pod
does not delete that intent: the controller normally creates a replacement.
If the template contains a mistake, the replacement inherits it.

In the practical checkpoint, apply the supplied `web.yaml` inside the assigned
project. It declares an application image pinned by digest, one replica, bounded
CPU and memory, and the workload security settings required by the lab. Run
`oc apply -f web.yaml`, then inspect the resulting Deployment and pods. The lab
supplies the actual file and project; the text exercise does not create resources.
Do not strip security settings to work around an admission rejection.

A changed pod template starts a new rollout. Observe it with
`oc rollout status deployment/web --timeout=60s`. A timeout means it did not finish
within that window; inspect events and conditions before choosing a repair.
If the supplied broken update uses an invalid image, restore the approved digest
in the manifest and apply it again. An imperative `oc set image` change is also
valid when it produces the required safe final state. It can differ from the
saved file, so reconcile that file before future applies.

An older replica may keep serving while the new rollout is stuck. Therefore,
"one pod is Ready" is weaker evidence than "the latest Deployment generation has
been observed, the intended updated replicas are Ready, and the rollout finished."
Verify the new state, then verify the application's response.

The checkpoint first records a working deployment, then introduces a controlled
image mistake and records that failure before repair. This sequence gives trusted
evidence of recovery. A final healthy screenshot alone cannot prove the failure
was encountered and repaired. Reset starts a new lab generation and repeats the
sequence; it cannot reuse evidence from the old attempt.
