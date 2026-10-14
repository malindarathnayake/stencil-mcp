#!/usr/bin/env python3
"""Build original, editable SVG symbols and machine-readable catalog. No dependencies."""
from pathlib import Path
from html import escape
import json, hashlib, re
ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'diagramkit' / 'library'
INK='#132B50'; WHITE='#FFFFFF'; MUTED='#5B708B'; BORDER='#CAD8E8'
PALETTES={
 'blue':('#1875D1','#EAF3FE'), 'teal':('#13857B','#E6F5F2'),
 'purple':('#7855C5','#F0EBFC'), 'orange':('#CC7628','#FFF2E3'),
 'red':('#C44552','#FCECEF'), 'slate':('#526C8C','#EDF2F7'),
 'green':('#368454','#EAF6EF'), 'yellow':('#AD8215','#FFF8D9')}
CATEGORIES={
 'compute':('Compute & virtualization','blue'),
 'hardware':('Hardware & accelerators','teal'),
 'network':('Network devices','blue'),
 'routing':('Routing & overlays','purple'),
 'security':('Security controls','red'),
 'identity':('Identity & cryptography','purple'),
 'storage':('Storage & continuity','teal'),
 'cloud':('Cloud & locations','blue'),
 'kubernetes':('Kubernetes & containers','blue'),
 'software':('Software & integration','teal'),
 'data':('Data systems','orange'),
 'devops':('Development & delivery','purple'),
 'observability':('Observability & operations','orange'),
 'ai':('AI & agent systems','teal'),
 'resilience':('Resilience & traffic policy','green'),
 'protocol':('Packets & transport','purple'),
 'presentation':('Diagram notation','slate'),
 'status':('State markers','slate'),
 'business':('Business process','teal'),
 'fleet':('Fleet telematics','orange')}
# id | readable name | glyph | optional role badge | search aliases / intended use
DATA={
'compute':'''rack-server|Rack server|server||host baremetal linux windows alma ep yc
blade-server|Blade server|blade||chassis compute
server-rack|Server rack|rack||datacenter cabinet
baremetal|Bare-metal host|server|BM|physical server linux
hypervisor|Hypervisor|hypervisor|HV|proxmox esxi kvm virtualization
virtual-machine|Virtual machine|vm|VM|guest qemu windows linux
hci-node|HCI node|server|HCI|s2d vsan hyperconverged
compute-cluster|Compute cluster|cluster||hosts failover
workstation|Workstation|desktop||desktop client
laptop|Laptop|laptop||endpoint developer mac windows
mobile|Mobile device|mobile||phone android ios
edge-server|Edge server|server|EDGE|remote branch
bastion-host|Bastion host|server|JUMP|jumpbox management
management-controller|Management controller|chip|BMC|ipmi redfish ilo idrac
tower-server|Tower server|tower||office server''',
'hardware':'''cpu|CPU|chip|CPU|processor socket amd intel epyc
gpu|GPU|accelerator|GPU|nvidia rtx inference training
dpu|DPU|accelerator|DPU|pensando smartnic offload
nic|Network interface card|nic|NIC|ethernet adapter
rdma-nic|RDMA-capable NIC|nic|RDMA|roce mrc connectx pollara
smartnic|SmartNIC|nic|SMART|packet processing
fpga|FPGA accelerator|accelerator|FPGA|programmable logic xilinx
video-accelerator|Video accelerator|accelerator|VIDEO|alveo ma35d transcode
memory|Memory module|memory||ram dimm ddr
pcie|PCIe bus|bus|PCIe|passthrough iommu vfio
nvme-device|NVMe device|ssd|NVMe|local flash disk
hsm-device|Hardware security module|chip|HSM|cryptography key custody
tpm|Trusted platform module|chip|TPM|attestation measured boot
optical-transceiver|Optical transceiver|transceiver||sfp qsfp optics''',
'network':'''switch-l2|Layer 2 switch|switch|L2|ethernet switching vlan
switch-l3|Layer 3 switch|switch|L3|routed switching
router|Router|router||ip routing gateway
leaf-switch|Leaf switch|switch|LEAF|tor clos
spine-switch|Spine switch|switch|SPINE|fabric clos
border-router|Border router|router|EDGE|internet ebgp peering
route-reflector|Route reflector|router|RR|ibgp evpn
chassis-switch|Chassis switch|rack|SW|modular switch
load-balancer|Load balancer|balance|LB|vip adc reverse proxy
reverse-proxy|Reverse proxy|gateway|PROXY|nginx haproxy envoy
api-gateway|API gateway|gateway|API|north south edge
vpn-gateway|VPN gateway|gateway|VPN|ipsec wireguard tailscale
sdwan-edge|SD-WAN edge|router|SDWAN|velocloud overlay wan
wireless-ap|Wireless access point|wifi||wifi wlan
wireless-controller|Wireless controller|server|WLC|wlan controller
modem|Modem / CPE|modem||isp handoff
patch-panel|Patch panel|switch|PATCH|cabling fiber
network-tap|Network TAP|tap|TAP|mirror span capture
wan-provider|WAN provider|cloud|WAN|carrier isp transit
internet|Internet|globe||public network''',
'routing':'''ecmp|ECMP group|multipath|ECMP|equal cost multipath
flow-hash|Flow hash|hash|HASH|five tuple source port
bgp|BGP routing|router|BGP|ebgp ibgp asn
ospf|OSPF routing|router|OSPF|igp link state
isis|IS-IS routing|router|IS-IS|igp link state
vrf|VRF|layers|VRF|routing instance tenant
vlan|VLAN|layers|VLAN|broadcast domain 8021q
vxlan|VXLAN tunnel|tunnel|VXLAN|overlay vni
evpn|EVPN control plane|multipath|EVPN|bgp overlay
vtep|VXLAN tunnel endpoint|gateway|VTEP|encapsulation decapsulation
nat|NAT translation|translate|NAT|snat dnat address
route-table|Routing table|table|FIB|rib prefix nexthop
qos|QoS scheduler|queue|QoS|priority traffic class
lag|Link aggregation|multipath|LAG|lacp port channel
mpls|MPLS forwarding|tunnel|MPLS|label switched path
srv6|SRv6 path|tunnel|SRv6|segment routing ipv6
bfd|BFD session|pulse|BFD|failure detection liveness
rpki|RPKI validation|certificate|RPKI|roa route origin
peering|Network peering|peering||interconnect asn exchange''',
'security':'''firewall|Firewall|firewall||stateful perimeter
waf|Web application firewall|firewall|WAF|http application protection
ids|Intrusion detection|eye|IDS|suricata zeek detection
ips|Intrusion prevention|shield|IPS|inline enforcement
security-gateway|Security gateway|gateway|SEC|inspection edge
acl|Access control list|checklist|ACL|permit deny filtering
security-group|Security group|shield|SG|workload ingress egress
nac|Network access control|shield|NAC|8021x posture
microsegmentation|Microsegmentation|segments||east west policy
ddos-protection|DDoS protection|shield|DDoS|scrubbing availability
sandbox|Sandbox|box|ISO|detonation isolated runtime
honeypot|Honeypot|trap||decoy deception
siem|SIEM|dashboard|SIEM|security events graylog sentinel
soar|SOAR|workflow|SOAR|response automation
edr|Endpoint detection|desktop|EDR|endpoint security
vulnerability-scanner|Vulnerability scanner|scan|VULN|exposure scan
dlp|Data loss prevention|shield|DLP|data egress inspection
casb|Cloud access broker|cloud|CASB|saas access policy
zero-trust|Zero-trust policy|shield|ZT|verify access identity
policy-engine|Policy engine|decision|POLICY|authorization opa
secure-boot|Secure boot|chip|BOOT|firmware trust
quarantine|Quarantine zone|segments|ISO|containment isolated
threat-actor|Threat actor|person|!|attacker external actor
security-review|Security review|checklist|SEC|threat model risk''',
'identity':'''user|User|person||human actor
admin|Administrator|person|ADMIN|privileged operator
group|User group|users||team organization
service-account|Service account|person|SVC|machine identity workload
identity-provider|Identity provider|identity|IdP|okta entra sso
mfa|Multi-factor authentication|mobile|MFA|authenticator otp
passkey|Passkey|key|FIDO|webauthn authentication
certificate|Certificate|certificate|TLS|x509 pki
certificate-authority|Certificate authority|certificate|CA|issuance root intermediate
key|Cryptographic key|key||encryption signing
secrets-vault|Secrets vault|vault||infisical vault secrets
access-token|Access token|token|AUTH|jwt oauth bearer
federation|Identity federation|peering|SSO|saml oidc
privileged-access|Privileged access|vault|PAM|jit access elevation''',
'storage':'''disk|Disk drive|disk||hdd ssd block
storage-array|Storage array|array||san enclosure
nas|Network attached storage|array|NAS|nfs smb file
san|Storage area network|array|SAN|iscsi fc
object-store|Object storage|bucket||s3 bucket immutable
file-share|File share|folder||smb nfs filesystem
block-volume|Block volume|disk|VOL|lun persistent volume
distributed-storage|Distributed storage|cluster|DATA|ceph scale out
snapshot|Snapshot|layers|SNAP|point in time
backup|Backup repository|backup||recovery restore
immutable-backup|Immutable backup|vault|WORM|ransomware recovery
tape-library|Tape library|tape||archive offline
disk-raid|RAID group|array|RAID|mdadm parity mirror''',
'cloud':'''public-cloud|Public cloud|cloud||aws azure gcp oci
private-cloud|Private cloud|cloud|PRIVATE|on premises
hybrid-cloud|Hybrid cloud|peering|HYBRID|onprem cloud
cloud-region|Cloud region|globe|REGION|geography region
availability-zone|Availability zone|building|AZ|fault domain
datacenter|Datacenter|building|DC|colo facility
branch-office|Branch office|building|BRANCH|remote office
vpc|Virtual network|cloud|VPC|vnet tenancy
subnet|Subnet|segments|SUBNET|cidr network
cloud-peering|Cloud peering|peering|PEER|vpc vnet peering
dedicated-circuit|Dedicated cloud circuit|multipath|DX|fastconnect expressroute direct connect
saas|SaaS application|browser|SaaS|hosted application
edge-location|Edge location|globe|EDGE|cdn pop
cloud-function|Cloud function|function|Fn|serverless lambda''',
'kubernetes':'''cluster|Kubernetes cluster|cluster|K8s|rke2 rancher orchestrator
control-plane|Control plane|cluster|CTRL|apiserver etcd scheduler
worker-node|Worker node|server|K8s|kubelet worker
pod|Pod|hexagon|POD|workload deployment
container|Container|box|CTR|oci runtime docker
service|Service|balance|SVC|clusterip endpoints
ingress|Ingress|gateway|ING|http ingress controller
gateway-api|Gateway API|gateway|GW|httproute envoy gateway
namespace|Namespace|segments|NS|tenant logical group
deployment|Deployment|layers|DEPLOY|replicas rollout
statefulset|StatefulSet|layers|STS|stateful workload
daemonset|DaemonSet|cluster|DS|node agent
job|Job|task|JOB|batch completion
cronjob|CronJob|clock|CRON|scheduled job
configmap|ConfigMap|document|CFG|configuration
secret|Secret|vault|K8s|workload secret
persistent-volume|Persistent volume|disk|PV|storage pv pvc
helm-chart|Helm chart|package|HELM|release packaging
operator|Operator|gear|OPS|controller custom resource
cni|CNI networking|multipath|CNI|calico cilium network
csi|CSI storage|disk|CSI|storage driver''',
'software':'''browser|Browser|browser||web client
frontend|Frontend|browser|UI|react webapp
backend|Backend service|code|APP|application service
rest-api|REST API|code|REST|http json endpoint
grpc-api|gRPC API|code|gRPC|protobuf rpc
microservice|Microservice|hexagon|SVC|bounded context
function|Function|function|Fn|serverless handler
background-worker|Background worker|gear|WORK|consumer async
message-queue|Message queue|queue|MQ|rabbitmq sqs amqp
message-broker|Message broker|multipath|MQ|broker pubsub
event-bus|Event bus|bus|BUS|events integration
topic|Topic|broadcast|TOPIC|pubsub kafka
scheduler|Scheduler|clock|SCHED|task schedule
batch-job|Batch job|task|BATCH|etl background
websocket|WebSocket|peering|WS|realtime bidirectional
webhook|Webhook|hook|HOOK|callback http
external-service|External service|cloud|EXT|third party api
monolith|Application monolith|code|APP|single deployment
workflow|Workflow|workflow||orchestration state machine''',
'data':'''relational-db|Relational database|database|SQL|postgres mysql oracle sqlserver
document-db|Document database|database|DOC|mongodb json
key-value-db|Key-value database|database|KV|redis dynamodb
graph-db|Graph database|graph|GRAPH|neo4j relationships
vector-db|Vector database|database|VEC|embeddings weaviate qdrant
time-series-db|Time-series database|database|TS|influx prometheus metrics
cache|Cache|memory|CACHE|redis memcached
data-warehouse|Data warehouse|building|DWH|analytics olap
data-lake|Data lake|bucket|LAKE|object analytics
stream-processor|Stream processor|workflow|STREAM|flink realtime
etl|ETL / ELT|translate|ETL|data pipeline transformation
dataset|Dataset|table|DATA|training collection
database-replica|Database replica|database|REPL|read replica replication
search-index|Search index|search|INDEX|elasticsearch opensearch''',
'devops':'''source-code|Source code|code||development repository
git-repository|Git repository|git|GIT|github gitlab version control
branch|Branch|git|BRANCH|feature branch
pull-request|Pull request|git|PR|merge review
code-review|Code review|checklist|REVIEW|approval diff
ci-build|CI build|gear|BUILD|teamcity jenkins github actions
cd-release|CD release|package|SHIP|deploy argo flux gitops
artifact-registry|Artifact registry|array|REG|harbor docker packages
container-image|Container image|package|OCI|image digest
unit-tests|Unit tests|checklist|UNIT|test coverage
integration-tests|Integration tests|checklist|INT|test service
end-to-end-tests|End-to-end tests|checklist|E2E|browser playwright
infrastructure-as-code|Infrastructure as code|code|IaC|terraform pulumi ansible
policy-as-code|Policy as code|code|POLICY|opa conftest
sbom|Software bill of materials|document|SBOM|supply chain dependencies
sast|Static analysis|scan|SAST|source security
sca|Dependency analysis|scan|SCA|supply chain dependency
dast|Dynamic analysis|scan|DAST|running application
release-approval|Release approval|checklist|GO|manual gate
rollback|Rollback|retry|BACK|revert deployment''',
'observability':'''metrics|Metrics|chart||prometheus influxdb
logs|Logs|document|LOG|graylog loki logging
traces|Distributed traces|trace||otel spans tracing
dashboard|Dashboard|dashboard||grafana charts
alert|Alert|bell||notification paging
health-probe|Health probe|pulse||liveness readiness
collector|Telemetry collector|multipath|OTEL|opentelemetry agent
netflow|Network flow telemetry|trace|FLOW|ipfix sflow
packet-capture|Packet capture|packet|PCAP|wireshark tcpdump
audit-log|Audit log|document|AUDIT|access change records
incident|Incident|bell|INC|response ticket
service-map|Service map|graph||dependencies topology''',
'ai':'''llm|Language model|brain|LLM|text inference reasoning
vision-model|Vision model|eye|VLM|multimodal image video
embedding-model|Embedding model|matrix|EMBED|vector representation
reranker|Reranker|sort|RANK|relevance scoring
model-server|Model server|server|MODEL|triton vllm ollama
model-registry|Model registry|array|MODEL|weights versions
ai-agent|AI agent|agent||tools workflow loop
mcp-server|MCP server|gateway|MCP|tool provider protocol
mcp-client|MCP client|code|MCP|codex claude tool caller
tool|Tool function|gear|TOOL|invocation action
guardrail|Guardrail|shield|AI|validation policy
human-approval|Human approval|person|GO|review gate authorization
prompt|Prompt / instructions|document|PROMPT|system user instructions
context-window|Context window|memory|CTX|tokens context
kv-cache|KV cache|memory|KV|prefill decode migration
prefill-worker|Prefill worker|accelerator|PRE|prompt processing
decode-worker|Decode worker|accelerator|DEC|token generation
training-job|Training job|brain|TRAIN|optimization weights
rag-retriever|RAG retriever|search|RAG|retrieval documents
router|Model router|decision|MODEL|routing model selection''',
'resilience':'''replication|Replication|peering|REPL|copy primary secondary
failover|Failover|multipath|FAIL|redundancy recovery
active-active|Active-active pair|peering|A/A|load share redundancy
active-passive|Active-passive pair|peering|A/P|standby failover
disaster-recovery|Disaster recovery|backup|DR|secondary site
circuit-breaker|Circuit breaker|breaker||trip isolate failure
retry|Retry policy|retry||backoff retransmission
rate-limiter|Rate limiter|gauge|RATE|throttle quota
autoscaler|Autoscaler|balance|SCALE|hpa scale out
timeout|Timeout|clock|TIME|deadline expiry''',
'protocol':'''packet|Packet|packet||payload network
ethernet-frame|Ethernet frame|packet|ETH|layer2 mac frame
ip-packet|IP packet|packet|IP|ipv4 ipv6
tcp-segment|TCP segment|packet|TCP|reliable byte stream
udp-datagram|UDP datagram|packet|UDP|source port destination port
rdma-operation|RDMA operation|nic|RDMA|write read send
queue-pair|Queue pair|queue|QP|rdma connection
sequence-number|Sequence number|token|SEQ|packet psn
ack|Acknowledgement|packet|ACK|received cumulative
sack|Selective acknowledgement|bitmap|SACK|have missing bitmap selective retransmission
nack|Negative acknowledgement|packet|NACK|loss feedback
receive-window|Receive window|memory|WIN|in flight sequence
memory-buffer|Memory buffer|memory|BUF|direct placement registered memory
queue-buffer|Queue buffer|queue|BUF|switch buffer congestion
dropped-packet|Dropped packet|drop||packet loss never arrived
out-of-order|Out-of-order arrival|sort|OOO|reordering direct placement
congestion|Congestion|gauge|QUEUE|load backlog
ecn|ECN mark|packet|ECN|congestion feedback
pfc-pause|PFC pause|pause|PFC|priority flow control
rtt|Round-trip time|clock|RTT|latency feedback
retransmission|Retransmission|retry|RTX|resend missing data''',
'presentation':'''boundary|System boundary|boundary||trust ownership zone
panel|Panel|panel||step comparison before after
swimlane|Swimlane|lanes||sequence workflow responsibility
callout|Callout|note||annotation explanation
note|Note|document||caption assumption
step|Numbered step|token|1|ordered walkthrough
decision|Decision|decision||yes no branch
process|Process|process||dfd flowchart
external-entity|External entity|process|EXT|dfd actor
data-store|Data store notation|datastore||dfd store
start-end|Start / end|capsule||flowchart terminator
legend|Legend|legend||key symbols meaning
connector-junction|Connection junction|junction||branch merge
link-break|Broken link|breaker||failure disconnected
fan-out|Fan-out|multipath||one to many
fan-in|Fan-in|funnel||many to one
sequence-lifeline|Sequence lifeline|lifeline||time ordering
annotation-bracket|Annotation bracket|bracket||group explanatory
physical-link|Physical link|link||ethernet fiber circuit
tunnel|Logical tunnel|tunnel||overlay encrypted''',
'status':'''healthy|Healthy|check||up success complete
warning|Warning|warning||degraded attention
down|Down / failed|cross||offline failure loss
pending|Pending|clock||waiting queued
blocked|Blocked|blocked||denied forbidden
locked|Locked|lock||protected private
unlocked|Unlocked|unlock||open access
unknown|Unknown|question||unverified uncertain
approved|Approved|check||review passed
expired|Expired|clock|EXP|certificate token''',
'business':'''form|Form|form||intake request application fields
invoice|Invoice|invoice||bill billing accounts payable
purchase-order|Purchase order|form|PO|procurement requisition
contract|Contract|signature||agreement esign quote signed
email|Email|envelope||notification mail message
calendar|Calendar event|calendar||schedule meeting date deadline
ticket|Ticket|ticket||case helpdesk itsm work item request
approval|Approval|stamp||approve sign-off accepted authorised
rejection|Rejection|stamp-x||declined rework returned denied
gateway-parallel|Parallel gateway|parallel||fork join and bpmn concurrent
timer|Timer|timer||sla wait deadline escalation stopwatch
payment|Payment|card||collect cash card remittance pay
report|Report|chart|KPI|kpi dashboard metrics summary
vendor|Vendor|building|EXT|supplier partner third party
chat|Chat message|bubble||instant message conversation''',
'fleet':'''vehicle|Fleet vehicle|truck||truck van asset unit
dashcam|Dash camera|camera||video road-facing driver-facing recorder
telematics-unit|Telematics unit|chip|TCU|gateway obd can modem tracker
gps-fix|GPS position|pin||location breadcrumb geocode
geofence|Geofence|geofence||zone boundary yard depot
event-clip|Event clip|film||harsh braking collision video evidence
dispatcher|Dispatcher|headset||operations desk controller
coaching-session|Coaching session|users|COACH|review safety training driver
maintenance-bay|Maintenance bay|garage||workshop repair inspection service'''
}

def el(tag, **attrs):
    return '<'+tag+' '+ ' '.join(k.replace('_','-')+'="'+escape(str(v),quote=True)+'"' for k,v in attrs.items())+'/>'
def r(x,y,w,h,fill=WHITE,stroke=INK,rx=6,sw=2.5):return el('rect',x=x,y=y,width=w,height=h,rx=rx,fill=fill,stroke=stroke,stroke_width=sw)
def l(x1,y1,x2,y2,c=INK,sw=2.5,dash=None):
    a=dict(x1=x1,y1=y1,x2=x2,y2=y2,stroke=c,stroke_width=sw,stroke_linecap='round')
    if dash:a['stroke_dasharray']=dash
    return el('line',**a)
def c(x,y,rad,fill=WHITE,stroke=INK,sw=2.5):return el('circle',cx=x,cy=y,r=rad,fill=fill,stroke=stroke,stroke_width=sw)
def p(d,fill='none',stroke=INK,sw=2.5):return el('path',d=d,fill=fill,stroke=stroke,stroke_width=sw,stroke_linecap='round',stroke_linejoin='round')
def t(x,y,txt,size=11,fill=INK,weight=700,anchor='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{fill}">{escape(txt)}</text>'

def art(g,A,S):
    def chip(badge=''):
        out=r(44,23,56,58,S)+r(55,34,34,36,WHITE,A,4)
        for x in (52,64,76,88):out+=l(x,15,x,23)+l(x,81,x,90)
        for y in (32,44,56,68):out+=l(35,y,44,y)+l(100,y,109,y)
        return out
    def server():
        out=''
        for y in (20,46,72):
            out+=r(18,y,108,22,S)+c(29,y+11,2.6,A,A,1)
            for x in (74,85,96,107):out+=l(x,y+8,x+5,y+8,MUTED,2)+l(x,y+14,x+5,y+14,MUTED,2)
        return out
    if g=='server':return server()
    if g=='blade':return r(22,14,100,86,S)+''.join(r(x,24,18,63,WHITE)+l(x+5,32,x+12,32,A)+c(x+9,77,2,A,A) for x in (29,53,77,101))
    if g=='rack':return r(33,8,78,96,S)+''.join(r(41,y,62,17,WHITE,INK,2)+c(49,y+8,2,A,A,1)+l(64,y+8,93,y+8,A,2) for y in (17,40,63))+l(42,104,42,109)+l(101,104,101,109)
    if g=='tower':return r(44,12,56,88,S)+r(52,23,40,16,WHITE)+c(72,80,7,WHITE,A)+l(54,49,90,49)+l(54,57,90,57)
    if g=='hypervisor':return r(14,62,116,34,S)+''.join(r(x,18,32,35,WHITE,A,4)+t(x+16,40,'VM',10) for x in (16,56,96))+l(32,53,32,62)+l(72,53,72,62)+l(112,53,112,62)
    if g=='vm':return r(31,17,87,72,S)+r(21,29,87,66,WHITE)+r(30,39,69,45,S,A,4)
    if g=='cluster':return ''.join(r(x,y,43,30,S)+c(x+9,y+15,2,A,A,1)+l(x+18,y+11,x+34,y+11,A,2)+l(x+18,y+20,x+34,y+20,A,2) for x,y in ((50,11),(13,70),(89,70)))+l(71,41,71,55)+l(35,55,110,55)+l(35,55,35,70)+l(110,55,110,70)
    if g in ('desktop','browser'):
        out=r(17,17,110,69,S)+r(25,25,94,46,WHITE,A,3)
        if g=='desktop':out+=l(72,86,72,97)+l(49,98,95,98)
        else:out+=l(25,37,119,37,A,1.5)+''.join(c(x,31,1.7,A,A,1) for x in (33,41,49))+r(34,46,23,17,S,A,2)+l(66,49,107,49,A,2)+l(66,57,100,57,MUTED,2)
        return out
    if g=='laptop':return r(31,17,82,63,S)+r(39,25,66,47,WHITE,A,3)+p('M31 80 H113 L131 95 Q132 99 124 99 H20 Q12 99 13 95 Z',S)+l(55,91,89,91,A)
    if g=='mobile':return r(47,9,50,95,S,rx=9)+r(54,24,36,62,WHITE,A,3)+l(63,17,81,17)+c(72,94,2,A,A,1)
    if g=='chip':return chip()
    if g in ('accelerator','nic'):
        out=r(20,25,109,66,S,rx=4)+l(14,20,14,99,INK,4)+l(10,20,23,20,INK,4)+r(45,91,55,9,'#E1BC4A',INK,0,1.5)
        if g=='accelerator':
            out+=c(61,57,22,WHITE,A)+c(61,57,6,S,A)
            for d in ('M61 51 Q43 32 43 49 Q43 59 55 59','M67 57 Q86 39 71 39 Q60 39 59 51','M61 63 Q78 80 80 65 Q80 55 68 55','M55 57 Q38 75 53 75 Q64 75 65 63'):out+=p(d,stroke=A,sw=1.5)
            out+=r(94,39,25,32,WHITE,A,3)
        else:
            out+=r(52,37,39,40,WHITE,A,3)+r(18,39,15,33,WHITE,INK,2)+l(36,47,51,47,A)+l(36,65,51,65,A)+l(94,49,118,49,A)+l(94,65,118,65,A)
        return out
    if g=='memory':return r(14,30,116,51,S,rx=3)+''.join(r(x,40,18,28,WHITE,A,2) for x in (22,48,74,100))+''.join(r(x,81,5,9,'#E1BC4A',INK,0,1) for x in range(25,121,9))
    if g=='bus':return l(18,70,126,70,A,7)+''.join(l(x,32,x,67)+r(x-12,19,24,16,S) for x in (32,72,112))
    if g=='ssd':return r(23,36,99,40,S,rx=4)+''.join(r(x,45,24,22,WHITE,A,2) for x in (33,66))+''.join(l(121,y,133,y,'#B18A25',3) for y in (43,50,57,64,71))+c(24,57,4,WHITE,INK,1.5)
    if g=='transceiver':return p('M31 34 H91 L119 48 V74 H31 Z',S)+r(22,43,31,28,WHITE)+r(30,49,12,16,S,A,1.5)+p('M53 43 L83 25 H112 V50',stroke=A)+l(60,58,104,58,MUTED)+l(60,67,104,67,MUTED)
    if g=='switch':return r(12,31,120,51,S)+p('M28 47 L40 59 M40 47 L28 59',stroke=A,sw=3)+''.join(r(x,y,9,7,WHITE,INK,1,1.5) for y in (44,59) for x in (54,68,82,96,110))+c(22,72,2,A,A,1)
    if g=='router':return el('ellipse',cx=72,cy=57,rx=48,ry=37,fill=S,stroke=INK,stroke_width=2.5)+p('M72 50 V29 M65 37 L72 29 L79 37 M79 57 H111 M103 50 L111 57 L103 64 M72 64 V85 M65 77 L72 85 L79 77 M65 57 H33 M41 50 L33 57 L41 64',stroke=A,sw=3)
    if g in ('balance','multipath','peering','funnel'):
        out=r(11,40,32,32,S,rx=5)+''.join(r(103,y,30,23,S,rx=4) for y in (11,45,79))+p('M43 56 H71 V22 H103 M71 56 H103 M71 56 V90 H103',stroke=A,sw=3)
        if g=='peering':out=r(12,34,43,44,S)+r(89,34,43,44,S)+p('M55 47 H89 M82 41 L89 47 L82 53 M89 65 H55 M62 59 L55 65 L62 71',stroke=A)
        if g=='funnel':out=p('M19 20 H125 L86 60 V89 L58 98 V60 Z',S)+l(43,33,103,33,A)+l(56,46,91,46,A)
        return out
    if g=='gateway':return r(40,16,64,84,S)+r(56,40,33,60,WHITE,A,3)+p('M8 54 H42 M31 45 L42 54 L31 63 M105 54 H137 M126 45 L137 54 L126 63',stroke=A,sw=3)
    if g=='wifi':return r(32,73,80,22,S)+c(72,63,4,A,A)+p('M55 53 Q72 38 89 53 M42 42 Q72 14 102 42 M29 29 Q72 -4 115 29',stroke=A,sw=3)
    if g=='modem':return r(25,47,94,39,S)+l(40,47,40,16)+l(106,47,106,22)+''.join(c(x,67,3,A,A,1) for x in (43,59,75))+r(96,59,13,14,WHITE,INK,2,1.5)
    if g=='tap':return r(45,35,54,41,S)+l(10,55,45,55,A,3)+l(99,55,135,55,A,3)+l(72,76,72,94,A,3)+p('M66 87 L72 95 L78 87',stroke=A)
    if g=='cloud':return p('M34 85 C9 85 7 55 28 47 C21 18 66 7 82 29 C103 13 132 35 123 57 C145 73 124 89 107 85 Z',S)+p('M49 65 L63 51 L75 64 L94 44',stroke=A,sw=3)
    if g=='globe':return c(72,56,43,S)+el('ellipse',cx=72,cy=56,rx=20,ry=43,fill='none',stroke=A,stroke_width=2)+l(29,56,115,56,A,2)+p('M39 29 Q72 45 105 29 M39 83 Q72 67 105 83',stroke=A,sw=2)
    if g=='hash':return r(32,16,80,82,S)+p('M57 34 L50 78 M84 34 L77 78 M43 47 H94 M39 65 H90',stroke=A,sw=4)
    if g=='layers':return p('M22 75 L72 98 L124 75 M22 59 L72 82 L124 59',stroke=A,sw=3)+p('M20 40 L72 14 L124 40 L72 66 Z',S)
    if g=='tunnel':return p('M32 26 Q73 4 112 26 V85 Q72 106 32 85 Z',S)+el('ellipse',cx=32,cy=55,rx=17,ry=30,fill=WHITE,stroke=INK,stroke_width=2.5)+p('M53 55 H134 M125 47 L134 55 L125 63',stroke=A,sw=3)+l(63,27,104,27,MUTED,1.5,'5 4')
    if g=='translate':return r(14,19,49,30,S)+r(81,66,49,30,S)+p('M66 32 H103 V61 M96 54 L103 61 L110 54 M79 82 H42 V54 M35 61 L42 54 L49 61',stroke=A,sw=3)
    if g in ('table','matrix','bitmap'):
        out=r(25,15,94,82,S)
        for y in (37,56,75):out+=l(25,y,119,y,A,1.5)
        for x in (55,87):out+=l(x,37,x,97,A,1.5)
        if g=='bitmap':out+=r(28,40,24,13,A,A,1)+r(90,40,25,13,A,A,1)+r(58,59,26,13,A,A,1)
        if g=='matrix':out+=t(41,52,'1',12)+t(71,52,'0',12)+t(103,52,'1',12)+t(41,71,'0',12)+t(71,71,'1',12)+t(103,71,'0',12)
        return out
    if g=='queue':return ''.join(r(x,32,26,47,S,rx=3) for x in (14,45,76))+p('M107 55 H137 M129 47 L137 55 L129 63',stroke=A,sw=3)
    if g=='pulse':return r(15,20,114,72,S)+p('M24 59 H45 L56 35 L70 76 L85 45 L96 59 H122',stroke=A,sw=3)
    if g=='firewall':return r(21,19,102,75,S,rx=3)+l(21,44,123,44)+l(21,69,123,69)+l(55,19,55,44)+l(89,19,89,44)+l(39,44,39,69)+l(73,44,73,69)+l(106,44,106,69)+l(55,69,55,94)+l(89,69,89,94)
    if g=='shield':return p('M72 9 L116 26 V55 Q111 87 72 105 Q34 87 28 55 V26 Z',S)+p('M51 56 L65 71 L95 38',stroke=A,sw=4)
    if g=='eye':return p('M13 56 Q72 -4 131 56 Q72 116 13 56 Z',S)+c(72,56,22,WHITE,A)+c(72,56,9,A,A)
    if g=='checklist':return r(36,16,80,82,S)+r(53,9,44,15,WHITE,A,4)+''.join(p(f'M46 {y} l5 5 l9 -11',stroke=A)+l(69,y,104,y,MUTED,2) for y in (41,61,81))
    if g=='box':return p('M23 31 L73 10 L123 31 V80 L73 102 L23 80 Z',S)+p('M23 31 L73 55 L123 31 M73 55 V102 M49 20 L99 43',stroke=A)
    if g=='segments':return r(13,12,118,89,WHITE,BORDER,8,2)+''.join(r(x,y,47,31,S,A,4) for x,y in ((21,20),(77,20),(21,61),(77,61)))+l(72,17,72,95,MUTED,1.5,'4 4')
    if g=='trap':return p('M37 44 H107 L119 94 H25 Z',S)+el('ellipse',cx=72,cy=43,rx=35,ry=9,fill=WHITE,stroke=INK,stroke_width=2.5)+p('M51 14 Q36 24 59 31 M84 8 Q67 20 91 29',stroke=A)
    if g=='dashboard':return r(15,18,114,78,S)+r(24,29,44,29,WHITE,A,3)+r(77,29,42,29,WHITE,A,3)+p('M25 81 L44 69 L61 79 L82 66 L101 73 L118 63',stroke=A,sw=3)
    if g=='workflow':return r(13,14,34,26,S)+r(96,14,34,26,S)+r(54,77,36,25,S)+p('M47 27 H96 M112 40 V59 H72 V77 M30 40 V59 H72',stroke=A)
    if g=='scan':return p('M36 33 V16 H55 M89 16 H108 V33 M108 80 V96 H89 M55 96 H36 V80',stroke=A,sw=3)+r(48,28,48,58,S)+l(19,55,125,55,A,3)+l(59,40,85,40,MUTED,2)+l(59,71,85,71,MUTED,2)
    if g=='decision':return p('M72 9 L129 56 L72 103 L15 56 Z',S)+t(72,67,'?',31,A)
    if g in ('person','users','identity'):
        out=c(72,31,18,S)+p('M36 96 V81 Q37 57 72 57 Q107 57 108 81 V96 Z',S)
        if g=='users':out=c(32,37,12,S,A)+c(112,37,12,S,A)+p('M8 89 V77 Q8 57 33 57 M111 57 Q135 57 136 77 V89',stroke=A)+out
        if g=='identity':out=r(13,15,118,80,S)+c(46,42,13,WHITE,A)+p('M25 79 Q25 60 46 60 Q67 60 67 79',stroke=A)+l(80,40,118,40)+l(80,55,111,55)+l(80,70,104,70)
        return out
    if g=='key':return c(46,41,23,S)+c(46,41,8,WHITE,A)+p('M63 56 L107 100 L118 89 L111 82 L119 74 L109 64 L101 73 L89 61',S)
    if g=='certificate':return r(33,11,79,82,S)+l(47,27,96,27,A)+l(47,39,96,39,MUTED,2)+l(47,51,83,51,MUTED,2)+p('M66 79 L58 105 L77 98 L90 106 L84 78',S,A)+c(75,73,17,WHITE,A)+p('M67 73 l6 6 l12 -13',stroke=A)
    if g=='vault':return r(26,13,92,87,S)+r(35,23,74,61,WHITE)+c(72,54,20,S,A)+l(72,40,72,68,A)+l(58,54,86,54,A)+c(72,54,6,WHITE,A)+l(34,100,34,107)+l(110,100,110,107)
    if g=='token':return r(31,23,83,66,S,rx=20)+c(72,56,21,WHITE,A)
    if g=='disk':return r(31,13,82,88,S)+c(72,54,27,WHITE,A)+c(72,54,7,S,A)+p('M92 77 L75 55 L81 52 L102 69',S)+c(44,89,2,A,A,1)
    if g=='array':return ''.join(r(16,y,112,26,S)+''.join(r(x,y+6,17,14,WHITE,A,2,1.5) for x in (24,46,68,90))+c(117,y+13,2,A,A,1) for y in (13,44,75))
    if g=='bucket':return p('M32 28 L40 93 Q73 108 106 93 L114 28 Z',S)+el('ellipse',cx=73,cy=28,rx=41,ry=14,fill=WHITE,stroke=INK,stroke_width=2.5)+p('M50 54 Q73 67 98 54',stroke=A)
    if g=='folder':return p('M17 28 H54 L66 40 H128 V91 H17 Z',S)+p('M18 48 H130 L119 95 H18 Z',WHITE,A)
    if g=='backup':return r(26,18,90,68,S)+r(35,27,73,33,WHITE,A,3)+p('M102 73 A35 29 0 1 1 58 66 M59 65 L55 80 M59 65 L73 68',stroke=A,sw=3)
    if g=='tape':return r(17,24,110,66,S)+c(47,56,19,WHITE,A)+c(99,56,19,WHITE,A)+c(47,56,6,S,A)+c(99,56,6,S,A)+l(47,75,99,75,A)
    if g=='building':return r(31,14,82,87,S)+''.join(r(x,y,13,13,WHITE,A,1,1.5) for y in (26,49) for x in (42,66,90))+r(61,75,24,26,WHITE,A,1)
    if g=='function':return r(27,17,90,80,S)+p('M48 32 L38 56 L48 80 M96 32 L106 56 L96 80 M80 31 L65 81',stroke=A,sw=3)
    if g=='hexagon':return p('M72 8 L116 32 V81 L72 106 L28 81 V32 Z',S)+p('M72 32 L96 45 V70 L72 84 L48 70 V45 Z',WHITE,A)
    if g=='task':return r(29,17,85,79,S)+r(39,28,28,24,WHITE,A,3)+l(77,34,103,34,MUTED,2)+l(77,46,99,46,MUTED,2)+p('M47 76 L59 86 L86 62',stroke=A,sw=4)
    if g=='clock':return c(72,57,41,S)+l(72,57,72,31,A,3)+l(72,57,94,69,A,3)+c(72,57,3,A,A)+l(66,9,78,9)+l(72,9,72,16)
    if g in ('document','note'):return p('M35 10 H86 L113 37 V101 H35 Z',S)+p('M86 10 V37 H113',WHITE)+''.join(l(47,y,99,y,MUTED,2) for y in (52,65,78,90))
    if g=='package':return p('M25 30 L72 11 L121 30 V86 L72 105 L25 86 Z',S)+p('M25 30 L72 51 L121 30 M72 51 V105 M49 20 L98 40 V62 L86 58',stroke=A)
    if g=='gear':
        out=''
        for angle in range(0,360,45):out+=f'<g transform="rotate({angle} 72 56)">'+r(62,10,20,20,S,rx=2)+'</g>'
        return out+c(72,56,34,S)+c(72,56,14,WHITE,A)
    if g=='code':return r(18,19,108,77,S)+l(18,35,126,35)+p('M47 49 L35 64 L47 80 M96 49 L108 64 L96 80 M79 46 L65 83',stroke=A,sw=3)
    if g=='broadcast':return c(37,57,17,S)+p('M63 42 Q82 57 63 72 M77 29 Q111 57 77 85 M92 17 Q137 57 92 97',stroke=A,sw=3)
    if g=='hook':return p('M36 23 V63 Q36 95 72 95 Q108 95 108 63 V47 M100 55 L108 46 L116 55',stroke=A,sw=4)+c(36,23,10,S)+c(108,26,10,S)
    if g=='database':return p('M30 28 V87 C30 109 115 109 115 87 V28 Z',S)+el('ellipse',cx=72.5,cy=28,rx=42.5,ry=16,fill=WHITE,stroke=INK,stroke_width=2.5)+p('M30 56 C30 76 115 76 115 56 M30 80 C30 99 115 99 115 80',stroke=A,sw=2)
    if g=='graph':return p('M32 31 L75 18 L117 54 L84 94 L26 82 Z M32 31 L84 94 M75 18 L26 82 M26 82 L117 54',stroke=A)+''.join(c(x,y,10,S) for x,y in ((32,31),(75,18),(117,54),(84,94),(26,82)))
    if g=='search':return c(61,47,29,S)+l(81,68,112,99,A,9)+l(48,39,74,39,A,2)+l(48,49,69,49,A,2)+l(48,59,65,59,A,2)
    if g=='git':return l(48,23,48,92,A,3)+p('M97 24 V50 Q97 66 70 66 H48',stroke=A,sw=3)+c(48,23,10,S)+c(48,92,10,S)+c(97,24,10,S)+c(48,66,7,WHITE,A)
    if g=='retry':return p('M112 40 A43 39 0 1 0 113 73 M112 40 L91 37 M112 40 L115 19',stroke=A,sw=4)+p('M72 35 V58 L88 66',stroke=INK,sw=3)
    if g=='chart':return l(22,19,22,95)+l(22,95,126,95)+''.join(r(x,y,17,95-y,S,A,2) for x,y in ((34,63),(61,44),(88,25)))
    if g=='trace':return ''.join(r(x,y,w,16,S,A,3) for x,y,w in ((16,16,112),(31,38,80),(48,60,57),(67,82,34)))+p('M23 32 V48 H30 M39 54 V70 H47 M56 76 V91 H65',stroke=MUTED,sw=1.5)
    if g=='bell':return p('M30 80 Q43 65 43 42 Q43 16 72 16 Q101 16 101 42 Q101 65 114 80 Z',S)+p('M59 92 Q72 106 85 92',stroke=A,sw=3)+l(72,8,72,16,A)
    if g=='packet':return r(16,26,112,60,S,rx=5)+r(16,26,32,60,WHITE,INK,5)+l(25,42,39,42,A,2)+l(25,53,39,53,A,2)+l(59,44,115,44,A,2)+l(59,57,109,57,MUTED,2)+l(59,70,95,70,MUTED,2)
    if g=='brain':return p('M72 18 C52 1 31 17 33 35 C11 43 21 64 31 67 C25 86 47 105 72 94 C97 105 119 86 113 67 C126 54 129 38 110 31 C109 13 87 4 72 18 Z',S)+p('M72 18 V94 M42 36 Q62 37 59 57 M33 67 Q58 65 53 85 M101 33 Q81 39 87 58 M112 67 Q88 67 91 86',stroke=A)
    if g=='sort':return ''.join(r(x,33,29,45,S,A,3)+t(x+14.5,61,str(v),18) for x,v in ((17,1),(57,3),(97,2)))+p('M70 24 Q92 5 111 24 M104 19 L111 24 L113 16',stroke=A)
    if g=='agent':return r(29,30,86,66,S,rx=14)+l(72,30,72,17)+c(72,12,5,S,A)+r(39,43,66,26,WHITE,A,6)+c(54,56,4,A,A,1)+c(90,56,4,A,A,1)+l(57,82,87,82,A,3)+r(18,50,11,29,S)+r(115,50,11,29,S)
    if g=='breaker':return l(13,62,52,62,A,3)+l(95,62,132,62,A,3)+c(52,62,4,WHITE,A)+c(95,62,4,WHITE,A)+l(52,62,90,30,A,3)+p('M69 24 L62 35 M81 18 L77 7',stroke=MUTED,sw=2)
    if g=='gauge':return p('M26 87 A49 49 0 1 1 118 87',S)+l(72,65,103,35,A,4)+c(72,65,7,WHITE,A)+l(30,62,38,62,A)+l(43,30,48,37,A)+l(72,17,72,25,A)
    if g=='drop':return r(24,23,95,67,S,'#C44552',6)+p('M49 37 L96 79 M96 37 L49 79',stroke='#C44552',sw=5)
    if g=='pause':return c(72,56,42,S)+r(54,33,12,47,A,A,2)+r(79,33,12,47,A,A,2)
    if g=='boundary':return el('rect',x=17,y=18,width=110,height=76,rx=8,fill=S,stroke=A,stroke_width=2.5,stroke_dasharray='7 5')
    if g=='panel':return r(13,15,118,83,S)+l(13,40,131,40,A,2)+r(24,51,45,32,WHITE,A,3)+l(82,56,119,56,MUTED,2)+l(82,66,113,66,MUTED,2)
    if g=='lanes':return r(12,18,120,78,S)+l(12,44,132,44,A,2)+l(12,70,132,70,A,2)+l(42,18,42,96,A,2)
    if g=='process':return r(23,23,98,66,S,rx=8)
    if g=='datastore':return l(25,27,119,27,A,3)+l(25,85,119,85,A,3)+l(25,27,25,85,A,3)
    if g=='capsule':return r(14,31,116,52,S,rx=26)
    if g=='legend':return r(22,16,99,80,S)+''.join(c(39,y,5,A,A,1)+l(54,y,107,y,MUTED,2) for y in (36,56,77))
    if g=='junction':return l(16,56,128,56,A,3)+l(72,15,72,97,A,3)+c(72,56,8,A,A)
    if g=='lifeline':return r(45,11,55,25,S)+l(72,38,72,104,A,2,'5 5')+r(65,57,14,24,WHITE,A,2)
    if g=='bracket':return p('M39 19 H27 V93 H39 M104 19 H116 V93 H104',stroke=A,sw=3)
    if g=='link':return p('M59 71 L47 83 A19 19 0 0 1 20 56 L48 28 A19 19 0 0 1 75 55 M86 40 L98 28 A19 19 0 0 1 125 55 L97 83 A19 19 0 0 1 70 56 M52 68 L92 44',stroke=A,sw=5)
    if g=='check':return c(72,56,39,'#EAF6EF','#368454')+p('M49 56 L65 73 L98 36',stroke='#368454',sw=5)
    if g=='warning':return p('M72 13 L125 96 H19 Z','#FFF2E3','#CC7628')+l(72,39,72,65,'#CC7628',5)+c(72,80,2.5,'#CC7628','#CC7628')
    if g=='cross':return c(72,56,39,'#FCECEF','#C44552')+p('M54 38 L90 74 M90 38 L54 74',stroke='#C44552',sw=5)
    if g=='blocked':return c(72,56,39,'#FCECEF','#C44552')+l(43,83,101,29,'#C44552',5)
    if g in ('lock','unlock'):
        return (p('M49 49 V34 A23 23 0 0 1 46 34',stroke=A,sw=5) if g=='unlock' else p('M49 49 V34 A23 23 0 0 1 95 34 V49',stroke=A,sw=5))+r(37,48,70,52,S)+c(72,68,6,WHITE,A)+l(72,73,72,84,A,3)
    if g=='question':return c(72,56,39,S)+t(72,69,'?',40,A)
    if g=='form':return r(36,10,72,92,S)+r(46,24,52,12,WHITE,A,2)+r(46,44,52,12,WHITE,A,2)+r(46,64,30,12,WHITE,A,2)
    if g=='invoice':return p('M36 10 H108 V98 L99 92 L90 98 L81 92 L72 98 L63 92 L54 98 L45 92 L36 98 Z',S)+l(46,26,80,26,A,3)+l(46,42,98,42,MUTED,2)+l(46,54,98,54,MUTED,2)+l(46,66,72,66,MUTED,2)+t(92,82,'$',20,A)
    if g=='signature':return r(28,10,72,90,S)+l(38,26,88,26,A,3)+l(38,40,90,40,MUTED,2)+l(38,52,84,52,MUTED,2)+p('M38 82 Q46 64 54 80 T70 76 T84 74',stroke=A,sw=3)+p('M98 90 L122 46 L131 51 L107 95 L96 99 Z',WHITE,INK,2)
    if g=='envelope':return r(20,24,104,66,S)+p('M20 30 L72 64 L124 30',stroke=A,sw=3)+p('M22 88 L58 58 M122 88 L86 58',stroke=A,sw=2)
    if g=='calendar':return r(24,20,96,82,S)+r(24,20,96,22,A,INK,6)+l(48,12,48,28,INK,4)+l(96,12,96,28,INK,4)+''.join(r(x,y,18,14,WHITE,A,2,1.5) for y in (52,76) for x in (36,63,90))+r(90,76,18,14,A,A,2,1.5)
    if g=='ticket':return p('M18 30 H126 V48 A9 9 0 0 0 126 66 V84 H18 V66 A9 9 0 0 0 18 48 Z',S)+l(98,32,98,82,A,2,'4 4')+l(32,46,82,46,A,3)+l(32,58,74,58,MUTED,2)+l(32,70,66,70,MUTED,2)
    if g in ('stamp','stamp-x'):
        out=c(72,22,12,S)+r(64,32,16,20,S,INK,3)+r(34,52,76,18,S,INK,4)+r(30,76,84,26,WHITE,A,4,2)
        return out+(p('M56 89 L67 98 L90 80',stroke=A,sw=4) if g=='stamp' else p('M60 81 L84 99 M84 81 L60 99',stroke='#C44552',sw=4))
    if g=='parallel':return p('M72 9 L129 56 L72 103 L15 56 Z',S)+p('M72 34 V78 M50 56 H94',stroke=A,sw=6)
    if g=='timer':return c(72,62,38,S)+r(63,10,18,10,S,INK,3)+l(72,20,72,24)+l(104,32,111,25)+l(72,62,72,36,A,4)+l(72,62,90,70,A,3)+c(72,62,4,A,A)+''.join(l(x1,y1,x2,y2,MUTED,2) for x1,y1,x2,y2 in ((72,30,72,34),(104,62,100,62),(72,94,72,90),(40,62,44,62)))
    if g=='card':return r(18,24,108,68,S,rx=8)+el('rect',x=18,y=38,width=108,height=14,fill=A)+r(30,62,22,16,WHITE,INK,3,2)+l(64,72,110,72,MUTED,2)+l(64,82,96,82,MUTED,2)
    if g=='bubble':return p('M32 20 H112 Q124 20 124 32 V68 Q124 80 112 80 H62 L38 98 L44 80 H32 Q20 80 20 68 V32 Q20 20 32 20 Z',S)+c(50,50,5,A,A,1)+c(72,50,5,A,A,1)+c(94,50,5,A,A,1)
    if g=='truck':return r(10,24,84,54,S,INK,4)+p('M94 40 H116 L132 58 V78 H94 Z',S)+p('M101 47 H113 L123 58 H101 Z',WHITE,A,2)+l(22,40,80,40,A,2)+''.join(c(x,84,11,WHITE)+c(x,84,4,A,A,1) for x in (32,112))
    if g=='camera':return r(46,10,40,8,S,INK,3)+l(66,18,66,32,INK,4)+r(22,32,92,52,S,INK,8)+c(64,58,18,WHITE,A)+c(64,58,7,A,A)+c(100,44,3.5,'#C44552','#C44552',1)+r(92,62,14,12,WHITE,A,2,1.5)
    if g=='pin':return p('M72 104 C72 104 36 66 36 44 A36 36 0 0 1 108 44 C108 66 72 104 72 104 Z',S)+c(72,44,13,WHITE,A)
    if g=='geofence':return el('path',d='M22 36 L60 14 L118 28 L126 78 L74 100 L24 84 Z',fill=S,stroke=A,stroke_width=2.5,stroke_dasharray='7 5',stroke_linejoin='round')+p('M72 76 C72 76 56 60 56 50 A16 16 0 0 1 88 50 C88 60 72 76 72 76 Z',WHITE,INK)+c(72,50,5,A,A,1)
    if g=='film':return r(18,22,108,70,S,INK,4)+''.join(r(x,27,8,7,WHITE,INK,1,1.5)+r(x,80,8,7,WHITE,INK,1,1.5) for x in range(26,120,16))+p('M62 43 L88 57 L62 71 Z',A,A)
    if g=='headset':return p('M34 64 V54 A38 38 0 0 1 110 54 V64',sw=4)+r(22,58,22,32,S,INK,6)+r(100,58,22,32,S,INK,6)+p('M111 90 Q111 102 86 102',stroke=A,sw=3)+c(82,102,4,A,A,1)
    if g=='garage':return p('M16 50 L72 14 L128 50 V102 H16 Z',S)+r(38,58,68,44,WHITE,INK,2)+''.join(l(38,y,106,y,MUTED,2) for y in (70,82,94))+c(72,38,9,WHITE,A)+l(72,33,72,43,A,2)
    raise ValueError('Unknown glyph: '+g)

USAGE={
 'protocol/dropped-packet':'The original transmission does not reach the receiver. Stop its arrow at a visible loss marker. Show any successful retransmission separately.',
 'protocol/sack':'Use human-readable received / missing state. A gap is not proof of loss; distinguish a delayed packet from a confirmed illustrative drop. Feedback travels receiver to sender.',
 'routing/ecmp':'Show the underlying paths separately from traffic overlays. Hashing can map different inputs to the same next hop; do not imply perfect balancing.',
 'hardware/rdma-nic':'Generic RDMA NIC icon. Label MRC-capable only when the depicted endpoint actually supports MRC; the icon does not assert product compatibility.',
 'presentation/boundary':'Label ownership or trust scope. A boundary is not itself a firewall or an enforcement control.',
 'security/zero-trust':'Use with explicit policy decision, identity, and enforcement components; do not imply a perimeter icon alone implements zero trust.',
 'ai/mcp-server':'A tool/data provider boundary. Distinguish read-only tools, mutation tools, and approval paths.',
}

def main():
    assets=[]
    for cat, rows in DATA.items():
        accent, soft=PALETTES[CATEGORIES[cat][1]]
        for line in rows.strip().splitlines():
            slug,name,glyph,badge,tags=line.split('|')
            aid=f'{cat}/{slug}'
            body=art(glyph,accent,soft)
            if badge:
                bw=max(31,len(badge)*6.7+12)
                body+=r(72-bw/2,84,bw,20,WHITE,accent,5,1.6)+t(72,98,badge,9.5,accent)
            desc=USAGE.get(aid,f'Generic {name.lower()} symbol for architecture and technical explanation diagrams. Add explicit labels and relationships for the intended system.')
            svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 144 112" width="144" height="112" role="img" aria-labelledby="title desc" font-family="Arial, Helvetica, sans-serif">
  <title id="title">{escape(name)}</title>
  <desc id="desc">{escape(desc)}</desc>
  <g id="artwork" stroke-linecap="round" stroke-linejoin="round">{body}</g>
</svg>\n'''
            dest=LIB/'assets'/cat/(slug+'.svg');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(svg.encode('utf-8'))
            assets.append({'id':aid,'name':name,'category':cat,'description':desc,'tags':tags.split(),'search_text':tags,
              'file':f'assets/{aid}.svg','viewBox':[0,0,144,112],
              'anchors':{'n':[0.5,0],'e':[1,0.5],'s':[0.5,1],'w':[0,0.5]},
              'anchor_note':'Normalized connection points on the enclosing symbol or node card, not enumerated hardware sockets.',
              'recommended_node_size':[200,128],'style':'filled-outline','glyph_family':glyph,'role_badge':badge,
              'palette':CATEGORIES[cat][1],'license':'Apache-2.0','provenance':'Original generic vector geometry generated for this kit; not an official vendor logo.',
              'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    catalog={'version':'0.2.0','asset_count':len(assets),'categories':[{'id':k,'name':v[0],'palette':v[1],'count':sum(a['category']==k for a in assets)} for k,v in CATEGORIES.items()], 'assets':assets}
    # Byte writes keep LF line endings on every OS, so recorded checksums match the files.
    (LIB/'catalog.json').write_bytes((json.dumps(catalog,indent=2)+'\n').encode('utf-8'))
    (LIB/'palettes.json').write_bytes((json.dumps({'ink':INK,'muted':MUTED,'border':BORDER,'background':WHITE,'colors':{k:{'accent':a,'soft':s} for k,(a,s) in PALETTES.items()}},indent=2)+'\n').encode('utf-8'))
    print(f'Built {len(assets)} assets across {len(CATEGORIES)} categories, {len(set(a["glyph_family"] for a in assets))} glyph families.')
if __name__=='__main__':main()
