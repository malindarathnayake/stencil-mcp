# Kubernetes and container platforms

> Use this guide when the diagram shows traffic into or between Kubernetes workloads, the cluster's own architecture, workload types and namespaces, storage, security controls, delivery, autoscaling, observability, failure, or an approximation of a service mesh.

## Questions to ask first

Ask only the questions whose answers the brief leaves open, in one round, each with its default. Pick the ones relevant to the brief.

1. Which platform is it (a managed service such as EKS, AKS or GKE, OpenShift, or self-managed), how many clusters, across which regions or zones, and what routes traffic between clusters? (default: one generic cluster, zones not drawn, no cross-cluster edges)
2. Should the control plane be shown, and is it provider-managed or self-hosted? (default: one `kubernetes/control-plane` card outside the request path, no etcd detail)
3. How many worker nodes appear, and does pod placement on specific nodes matter? (default: nodes not drawn; pods sit directly in the namespace group)
4. Which namespaces exist, and which workloads belong to each? (default: one application namespace)
5. What workload type runs each component, and how many replicas? (default: Deployment with two pods for stateless services, StatefulSet for anything holding its own data, drawn as "Pod 1" and "Pod 2")
6. How does external traffic enter, where is TLS terminated, and how are certificates issued? (default: Gateway API, TLS ends at the gateway, noted in the footer, no certificate card)
7. Which service-to-service calls, external dependencies and egress paths (NAT, egress gateway, fixed egress IPs) belong in the story? (default: only calls the brief names; egress not drawn)
8. Do any workloads need persistent storage, and with which access mode, CSI driver and backend? (default: no persistent volumes)
9. Are security controls in scope: NetworkPolicy, RBAC, workload identity to cloud APIs, admission policy, or secrets from an external store? (default: none drawn)
10. How are changes delivered: CI pushing to the cluster, a GitOps controller pulling from Git, Helm or an operator? Which registry is used, and are there signature or SBOM checks? (default: delivery out of scope)
11. Is autoscaling, a service mesh (sidecar or sidecarless) or telemetry collection part of the story? (default: none shown)
12. Is a failure being explained, such as a node or pod going down? (default: no failure markers)

## Push back when

- **Namespaces are drawn as isolation.** A namespace scopes names, quotas and access control; it does not block pod-to-pod traffic. Network isolation needs NetworkPolicy and a CNI plugin that enforces it. Ask whether to show those policies.
- **A Secret is labelled "encrypted".** Secret values are base64-encoded in the API and readable by anyone with get or list on Secrets, or create on pods, in that namespace. Encryption at rest depends on the provider and its configuration; several managed services enable it by default. External Secrets Operator still materialises a Kubernetes Secret, while the Secrets Store CSI driver can mount values without one. Ask which applies before labelling.
- **Several replicas across nodes share one ReadWriteOnce volume.** ReadWriteOnce allows mounting by one node at a time, and ReadWriteOncePod by one pod. Ask whether each replica has its own claim (the StatefulSet pattern) or whether the storage really supports ReadWriteMany.
- **A Deployment with a ReadWriteOnce volume rolls out with RollingUpdate.** If the new pod lands on another node, it can hang on a Multi-Attach error until the old pod releases the volume. Say so, and ask whether the strategy is Recreate or whether the workload should be a StatefulSet.
- **The horizontal pod autoscaler is said to add nodes.** It changes the replica count of a Deployment, StatefulSet or ReplicaSet. Nodes come from a cluster autoscaler or node provisioner. It cannot scale a DaemonSet.
- **The Service is drawn as a proxy box that traffic passes through.** A ClusterIP Service is a virtual address and an endpoint list; the node data plane (kube-proxy or an eBPF-based CNI) forwards traffic straight to pod endpoints. A headless Service (`clusterIP: None`, as a StatefulSet uses) has no virtual IP; clients resolve and connect to individual pods. An ExternalName Service is only a DNS alias to an outside host and has no pods.
- **Non-HTTP traffic is drawn through an Ingress.** Ingress routes HTTP and HTTPS only. Ask whether a LoadBalancer or NodePort Service, or a Gateway with TCPRoute or UDPRoute (experimental in Gateway API), is in use, and draw that entry point.
- **Controllers or the scheduler are drawn talking to pods directly.** Controllers and the scheduler act only through the API server, and only the API server talks to etcd. The kubelet takes its pod specs from the API server and then runs containers locally through the container runtime, so a kubelet-to-pod `control` edge inside a node is correct.
- **Helm is drawn with an in-cluster Tiller.** Helm 3 has no Tiller; the client renders the chart and applies it through the API server. Ask whether Helm 2 is meant.
- **"GitOps" is drawn as CI running `kubectl apply`.** That is push-based deployment. GitOps normally means an in-cluster controller pulling desired state from Git. Ask which one the user runs.
- **A Pod is described as moving to another node.** Pods are not migrated; the controller creates a replacement pod, usually on another node. A Deployment replacement gets a new name and IP. A StatefulSet replacement keeps its ordinal name, stable DNS name and PersistentVolumeClaim, and only its IP changes.

## How we draw it here

**Direction and grouping.** Traffic flows left to right: client, entry point, Service, pods, data stores. Draw the cluster as a `group` with `style: "boundary"`. Groups do not nest in the scene format; nesting is visual only. Draw each namespace group's rectangle fully inside the cluster group's rectangle, and set each node's `group` to the innermost group. The validator does not check that the namespace sits inside the cluster, so check it in the render. Use a `panel` group for anything outside the cluster, such as CI or an external database. Draw several clusters as separate boundary groups, or as `kubernetes/cluster` cards when internal detail is out of scope. Connect clusters only through what the user named (a global load balancer, DNS failover, a mesh), with `resilience/failover` where failover is the point.

**Zones and regions.** Draw each zone or region as a `boundary` group titled after it (for example "Zone a"). Use `cloud/availability-zone` or `cloud/cloud-region` cards only in overviews. Spread replicas as the user described.

**Control plane.** Place `kubernetes/control-plane` above or below the request row, never between the client and the pods. Its edges, and controller or operator actions (create pods, update endpoints, provision volumes), are `control` edges to the API server or control plane, not to individual pods.

**Nodes and pods.** When nodes matter, draw each worker node as a `boundary` or `panel` group titled with the node name (for example "worker-1"), and set the pod cards' `group` to it. Use `kubernetes/worker-node` cards only when pods are not drawn inside them; cards cannot contain cards. Keep the number of pods per node consistent with the replica count. A DaemonSet shows one pod in every node group. A CronJob is `kubernetes/cronjob` to `kubernetes/job` to a pod, with no Service.

**Asset roles.**

| Role | Asset ID |
| --- | --- |
| Client, external load balancer | `software/browser`, `compute/mobile` or `identity/user`; `network/load-balancer` |
| Entry point | `kubernetes/ingress` or `kubernetes/gateway-api` (match the user's API) |
| Service, pod, container | `kubernetes/service`, `kubernetes/pod`, `kubernetes/container` |
| Workload controllers | `kubernetes/deployment`, `kubernetes/statefulset`, `kubernetes/daemonset`, `kubernetes/job`, `kubernetes/cronjob` |
| Namespace or cluster as a card (overview only) | `kubernetes/namespace`, `kubernetes/cluster` |
| Configuration | `kubernetes/configmap`, `kubernetes/secret`; an external store is `identity/secrets-vault` |
| Storage | `kubernetes/persistent-volume` (also used for a PVC), `kubernetes/csi`, then `storage/block-volume`, `storage/file-share` or `storage/storage-array` |
| Stateful replicas | `data/database-replica` with `replication` edges |
| Pod networking, NetworkPolicy, egress | `kubernetes/cni`; `security/microsegmentation` or `security/acl`; `routing/nat`, `security/firewall` |
| Identity, RBAC, certificates | `identity/service-account`, `identity/group`, `identity/admin`; `identity/certificate`, `identity/certificate-authority` |
| Admission and policy | `security/policy-engine`, `devops/policy-as-code` |
| Managed platform | `cloud/public-cloud` |
| Operator, Helm | `kubernetes/operator`, `kubernetes/helm-chart` |
| Delivery and supply chain | `devops/git-repository`, `devops/ci-build`, `devops/container-image`, `devops/artifact-registry`, `devops/cd-release` (label it "GitOps controller" when it is one), `devops/sbom`, `devops/sca` |
| Autoscaling, observability | `resilience/autoscaler` fed by `observability/metrics`; `observability/collector`, `observability/logs`, `observability/traces` |
| Mesh approximation | `network/reverse-proxy` labelled "Sidecar proxy", `kubernetes/control-plane` labelled "Mesh control plane" |

**Edge meanings.** Request traffic from the client to pods, and from pods to data stores, is `data`. The Service selecting its pods is a `dependency` edge labelled "selects"; show either it or the traffic edge, never both on one segment. For a headless Service, label the card "Headless Service" and draw client edges to specific pods when ordinal identity matters, for example a primary and replica database. ConfigMap and Secret attachments are `dependency` edges from the pod or workload. Storage runs from the pod to its PersistentVolumeClaim (a `kubernetes/persistent-volume` card labelled "PVC <name>"), then to the PersistentVolume, then to the backend, all as `dependency` edges. StorageClass and CSI provisioning is `control`. A StatefulSet gets one PVC per replica through volumeClaimTemplates. Image pulls are `data`; reconciliation and controller actions are `control`. A NetworkPolicy is a `control` edge from a `security/microsegmentation` card to the namespace or pod it governs, labelled with the rule (for example "allow app->db").

**Palettes.** Keep one meaning per palette: blue for application traffic, slate for the control plane and control edges, teal for storage and data stores, purple for delivery tooling. Use red only for failure states.

**Failure.** Place a `marker` node with `state: "down"` beside the failed node or pod, not on top of it, which raises `node_overlap`. Draw the replacement pod where the controller recreates it.

**Service mesh.** Draw each meshed pod as a `panel` group titled "Pod 1" that holds the application `kubernetes/container` card and the "Sidecar proxy" card, with each card's `group` set to that pod group. Do not also draw a `kubernetes/pod` card. Pod-to-pod traffic between proxies is `data` labelled "mTLS", with `identity/certificate` attached as a `dependency`. The mesh control plane has `control` edges to the proxies. For sidecarless modes, ask what the node-level or waypoint proxies are and draw those instead. State in the footer that the mesh is an approximation, not a configuration of a particular product.

**Legend, footer and density.** Add a `legend` whenever more than one edge kind appears, with one entry per kind (`dashed: true` for control and dependency). Use `footer` for unconfirmed assumptions and approximations, such as "Service-to-pod edges are logical; the node data plane forwards traffic". A panel with more than 28 elements raises a `density` warning; split nodes, namespaces and mesh detail into separate panels as the `style` guide describes.

## Common mistakes

- Adding a mesh, operator, external load balancer, monitoring stack, NetworkPolicy or CNI card the user did not mention because "clusters usually have one". Ask instead.
- Drawing the control plane in the request path, or routing user traffic through the API server.
- Using `kubernetes/ingress` when the user said Gateway API, or the reverse.
- Using `kubernetes/cluster`, `kubernetes/namespace`, `kubernetes/worker-node` or `kubernetes/pod` cards as containers, or stacking cards on them. Containment is a group.
- Setting a node's `group` to the cluster when it sits in a namespace group, or looking for a parent field on groups.
- Drawing one pod for a replicated workload, two pods for a singleton, or a DaemonSet with a replica count.
- Showing a Job or CronJob as a long-running service behind a Service.
- Pointing the pod straight at a PersistentVolume and skipping the claim.
- Making Secret or ConfigMap edges `data` arrows that look like request traffic.
- Labelling a namespace boundary as a security control.
- Picking `compute/virtual-machine` or `compute/rack-server` for a worker node, unless the underlying machine is the point.

## Start from

- `kubernetes-ingress` for client traffic through a gateway and Service to pods, with the control plane off the data path.
- `secure-ci-cd` for build, verify and deploy into a cluster; extend it with a GitOps controller or Helm release.
- `observability-pipeline` when telemetry from the cluster is the story; `zero-trust-access` when identity-aware access to workloads is.
- No template yet for cluster architecture with nodes, zones, storage, autoscaling, operators, a mesh or multi-cluster failover; use `layout_diagram`, then place the groups by hand.

Read alongside: `brief` first, then `style`. Read `network` for the routed network under the cluster, and the CI/CD, storage, security or observability guides when the drawing covers those areas in depth.
