# Explain a workload symptom

Estimated time: 10 minutes, including four practice exercises.
Prerequisite: Find your project.

A useful diagnosis joins a symptom to evidence. Start with `oc get pods` in the
assigned project. Read readiness, status and restart information separately.
A Running pod can still be unready; a process having started does not establish
that it can serve requests.

For a named pod, `oc describe pod web-example` shows conditions and events.
Replace the example with the actual pod name in a live lab. Events can explain
why a container did not start: an unavailable image, admission restriction or
scheduling problem calls for a different response than a crashing process.
For a started container, `oc logs deployment/web` can supply application evidence.
Do not expect useful application logs from a container that has never started.

Suppose a new pod shows ImagePullBackOff. That status means pulling its image is
failing with retries; it does not identify the cause by itself. If the events
say a tag does not exist, compare the Deployment image reference with the approved
image supplied by the lab. If instead the registry or network is unavailable,
report an infrastructure problem. Do not mark the learner wrong for an outage.

Record the observation before changing the workload. Repeated deletion or
restarts can remove useful context and will not repair a bad pod template.
After a repair, repeat the relevant observations and check the current rollout.

The text exercises accept only the command forms they request. They do not
execute a shell or recognize every equivalent spelling. The practical checkpoint
will be assessed by resource state and behavior rather than command history.
