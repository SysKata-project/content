# Connect a Service and Route

Estimated time: 10 minutes, including four practice exercises.
Prerequisite: Deploy and repair a workload.

Pods can be replaced, so their addresses are not a stable application interface.
A Service supplies a stable in-cluster endpoint and selects backend pods by labels.
Its selector must match the intended pods. A similar resource name alone creates
no association. The Service port maps to a target port where the application
actually listens; declaring a container port does not start a listener.

For this lab, the web container listens on 8080. After deploying it, create a
ClusterIP Service with `oc expose deployment web --port=8080 --target-port=8080`.
Inspect it with `oc describe service web`. Confirm its selector and backend
readiness before blaming external routing. The platform maintains EndpointSlices
for Services; an empty ready backend set points you toward selection or readiness.

An OpenShift Route connects an external host at the ingress router to a Service.
Create the lab's edge-terminated Route with `oc create route edge web
--service=web --port=8080 --insecure-policy=Redirect`. This uses the router's
configured certificate; learners do not need to read or upload private keys.
TLS ends at the router, and this example forwards HTTP to the application.
Edge termination is not a claim of encryption on every internal hop.

Inspect the assigned Route host and its admission status. Then use an HTTPS
client with the trusted cluster certificate chain to request that host and check
the expected application response. A Route object or router error page is not
proof of success. Diagnose in order: current rollout, Service selector and target
port, Route target/admission, then the external response. Infrastructure DNS,
certificate or router failures require lab support rather than a learner penalty.

Your checkpoint outcome is a healthy current rollout and a reachable application,
including recovery from the controlled failure. It does not grant access to
cluster-wide network policy or complete the full DO180/DO280 curriculum.
