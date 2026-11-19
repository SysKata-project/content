# Find your project

Estimated time: 8 minutes, including four practice exercises.

Before starting, you should be comfortable with shell commands, arguments and
exit status, and know how a container image differs from a running container.
If these are unfamiliar, practice those basics before entering a cluster lab.
This is a bounded OpenShift pilot, not the complete DO180 course.

An OpenShift project gives your work a namespace. Deployments, Pods, Services
and Routes belong to that scope. Nodes belong to the cluster and are shared
infrastructure; they are not yours to reconfigure. Namespace access is not
cluster administrator access.

The lab supplies an assigned project and a scoped identity. Treat that assignment
as authoritative. `oc whoami` identifies the authenticated user; `oc project -q`
prints the selected project. Those answer different questions. Before changing
anything, compare the selected project with your assignment. Use `oc project
practice-a` only when `practice-a` is the project actually assigned to you.
The names in these exercises are examples, not authority to access another project.

Most namespaced commands use the selected project unless you supply another
namespace explicitly. An empty `oc get pods` result can simply mean you selected
the wrong project. It is not evidence that all applications disappeared from the
cluster. Likewise, a Forbidden response is an access boundary, not a request to
obtain administrator credentials. Check your assignment and ask for lab support
if the supplied access is broken.

Practice identifying scope before diagnosing resources. The useful habit is:
read the assignment, confirm the current project, then inspect that project's
resources. Do not use all-namespace queries or modify shared cluster resources
for these lessons.
