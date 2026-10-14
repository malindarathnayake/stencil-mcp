#!/usr/bin/env python3
"""Build readable example scenes with explicit connection semantics."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from diagramkit.renderer import render
from diagramkit.scene import validate
OUT=ROOT/'diagramkit/library/templates'

class Diagram:
    def __init__(self,slug,title,subtitle,w=1480,h=740):
        self.slug=slug;self.s={'version':'1.0','title':title,'subtitle':subtitle,'description':subtitle,'width':w,'height':h,'groups':[],'nodes':[],'edges':[],'footer':'Illustrative architecture. Labels describe roles; generic symbols do not assert product compatibility.'}
    def group(self,id,x,y,w,h,title,caption='',palette='blue',style='panel'):
        self.s['groups'].append(dict(id=id,x=x,y=y,w=w,h=h,title=title,caption=caption,palette=palette,style=style));return id
    def node(self,id,asset,x,y,label,detail='',w=190,h=144,palette='blue',group=None,kind='component'):
        n=dict(id=id,kind=kind,asset=asset,x=x,y=y,w=w,h=h,label=label,palette=palette)
        if detail:n['detail']=detail
        if group:n['group']=group
        self.s['nodes'].append(n);return id
    def txt(self,id,x,y,w,h,label,size=16,weight=400,align='left'):
        self.s['nodes'].append(dict(id=id,kind='text',x=x,y=y,w=w,h=h,label=label,font_size=size,weight=weight,align=align));return id
    def packet(self,id,x,y,label,palette,detail='',w=92,h=58,state='normal'):
        self.s['nodes'].append(dict(id=id,kind='packet',x=x,y=y,w=w,h=h,label=str(label),detail=detail,palette=palette,state=state));return id
    def memory(self,id,x,y,w,h,values,label):
        colors=['orange','blue','green','purple','yellow']
        self.s['nodes'].append(dict(id=id,kind='memory',x=x,y=y,w=w,h=h,label=label,cells=[{'value':str(v),'palette':colors[i%5],**({'state':'missing'} if v=='—' else {})} for i,v in enumerate(values)]));return id
    def edge(self,a,b,label='',palette='blue',kind='data',points=None,sp=None,tp=None,**kw):
        e=dict(id=f'e{len(self.s["edges"])+1}',source=a,target=b,kind=kind,palette=palette)
        if label:e['label']=label
        if points is not None:e['points']=[{'x':x,'y':y} for x,y in points]
        if sp:e['source_port']=sp
        if tp:e['target_port']=tp
        e.update(kw);self.s['edges'].append(e)
    def save(self):
        OUT.mkdir(parents=True,exist_ok=True)
        report=validate(self.s)
        if not report['valid']:raise RuntimeError(self.slug+': '+json.dumps(report))
        # Byte writes keep LF line endings on every OS, so rebuilt files are repeatable.
        (OUT/(self.slug+'.json')).write_bytes((json.dumps(self.s,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
        (ROOT/'examples'/(self.slug+'.svg')).write_bytes(render(self.s).encode('utf-8'))
        return report

# Packet-level teaching example: one original packet is really lost.
d=Diagram('mrc-loss-recovery','How MRC uses multiple paths',"MRC sprays one connection’s packets across ECMP paths, handles loss at the endpoints, and only resends what’s missing.",1800,1030)
d.s['footer']='Illustrative packet numbers and UDP ports. SACK text summarizes receive state; it is not a literal wire-format field.'
d.group('fabric',605,136,590,449,'ECMP forwarding','Changing the hash input allows one connection to use several paths.')
d.node('sender','hardware/rdma-nic',42,310,'Sender NIC','One MRC connection',w=214,h=158,palette='teal')
d.node('receiver','hardware/rdma-nic',1542,310,'Receiver NIC','Received: 1, 2, 3, 5',w=216,h=158,palette='teal')
cols=['orange','blue','green','purple','yellow']
for i in range(5):
    d.packet(f'p{i+1}',326,175+76*i,f'Packet {i+1}',cols[i],f'UDP source port: {50001+i}',w=185,h=60)
    d.edge('sender',f'p{i+1}',palette=cols[i],route='straight')
for i,letter in enumerate('ABCD'):
    d.node('path'+letter,'network/switch-l3',806,194+i*98,'',w=160,h=70,kind='symbol')
    d.txt('label'+letter,987,199+i*98,183,26,'ECMP path '+letter,16,600)
for i,path in enumerate(['A','B','C','D','D']):d.edge(f'p{i+1}','path'+path,palette=cols[i],sp='e',tp='w')
for letter,col,yy in [('A','orange',250),('B','blue',294),('C','green',340)]:
    # Deliberate waypoints leave space for path labels.
    origin_y=229+'ABCD'.index(letter)*98
    d.edge('path'+letter,'receiver',palette=col,sp='e',tp='w',points=[(1218,origin_y),(1430,yy),(1498,yy),(1498,389)])
d.s['nodes'].append(dict(id='loss',kind='marker',x=1304,y=435,w=44,h=44,state='dropped'))
d.edge('pathD','loss',palette='purple',sp='e',tp='w',points=[(1230,523),(1230,457)])
d.edge('pathD','receiver',palette='yellow',sp='e',tp='w',points=[(1208,523),(1208,565),(1504,565),(1504,389)])
d.txt('lost-note',1263,491,236,44,'Packet 4 is dropped.\nThe original never arrives.',15)
d.group('arrival',36,622,850,352,'1  Arrivals and receiver memory','Packet 2 is delayed. Packet 4 is lost.',palette='blue')
d.txt('arrival-label',70,699,325,28,'Arrival order at the receiver',15,600)
for i,(v,col) in enumerate([(1,'orange'),(3,'green'),(5,'yellow'),(2,'blue')]):d.packet('a'+str(v),70+i*82,742,v,col,w=63,h=46)
d.memory('rx-before',70,820,445,85,[1,2,3,'—',5],'Direct placement into receiver memory')
d.txt('sack-note',570,738,274,110,'Receiver state:\nHave 1, 2, 3, 5 — missing 4',18,600)
d.txt('slot-note',570,872,274,59,'Slot 4 stays empty until the retransmitted packet arrives.',15)
d.group('recovery',910,622,854,352,'2  Recover only the missing packet','Feedback and loss-recovery timing guide the retransmission.',palette='teal')
d.node('retry-sender','hardware/rdma-nic',946,734,'Sender NIC',w=173,h=126,palette='teal')
d.node('retry-receiver','hardware/rdma-nic',1553,734,'Receiver NIC',w=173,h=126,palette='teal')
d.packet('retry4',1249,782,'4','purple',w=150,h=56,detail='Retransmitted packet')
d.edge('retry-receiver','retry-sender','SACK: have 1, 2, 3, 5 — missing 4',palette='slate',kind='feedback',sp='n',tp='n',points=[(1639.5,706),(1032.5,706)],label_x=1335,label_y=708)
d.edge('retry-sender','retry4',palette='purple',sp='e',tp='w')
d.edge('retry4','retry-receiver',palette='purple',sp='e',tp='w')
d.txt('retry-note',1162,740,334,29,'Only packet 4 is resent',16,600,'center')
d.memory('rx-after',1024,885,618,69,[1,2,3,4,5],'Receiver memory after recovery')
d.save()

# ECMP example: two independent flows collide; all four physical paths still exist.
d=Diagram('ecmp-flow-hashing','ECMP hashes flows onto paths','Two large flows can select the same path while other equal-cost paths remain available.',1480,720)
d.group('paths',566,141,384,492,'Four equal-cost next hops','The diagram separates physical reachability from traffic.',palette='blue')
d.node('s','compute/rack-server',45,330,'Sending host','Two independent flows')
d.node('r','compute/rack-server',1224,330,'Receiving host')
for i,L in enumerate('ABCD'):
    d.node('p'+L,'network/switch-l3',650,218+i*100,'',w=140,h=67,kind='symbol')
    d.txt('t'+L,805,(576 if i==3 else 206+i*100),125,29,'Path '+L,16,600)
    d.edge('s','p'+L,palette='slate',kind='physical',sp='e',tp='w',width=1.2,route='straight')
    d.edge('p'+L,'r',palette='slate',kind='physical',sp='e',tp='w',width=1.2,route='straight')
d.edge('s','pA','Flow A + Flow B',palette='orange',sp='n',tp='w',points=[(140,264),(431,264),(431,251.5)],label_x=401,label_y=252,width=4)
d.edge('pA','r',palette='orange',sp='e',tp='n',points=[(1120,251.5),(1319,251.5)],width=4)
d.s['legend']=[{'label':'Available physical path','palette':'slate'},{'label':'Two flows share path A','palette':'orange'}];d.save()

# Leaf-spine physical topology, no invented traffic arrows.
d=Diagram('leaf-spine','Leaf–spine topology','Each leaf connects to both spines. Server attachments and fabric links are shown without traffic arrows.',1480,810)
d.group('fabric',260,135,960,454,'Routed fabric','Physical connectivity only; routing and traffic overlays can be added separately.')
for i,x in enumerate((473,833)):d.node('sp'+str(i),'network/spine-switch',x,220,'Spine '+str(i+1),w=180,h=126)
for i,x in enumerate((310,646,980)):
    d.node('leaf'+str(i),'network/leaf-switch',x,436,'Leaf '+str(i+1),w=180,h=126)
    for j in range(2):d.edge('sp'+str(j),'leaf'+str(i),kind='physical',palette='slate',sp='s',tp='n',route='straight')
    d.node('host'+str(i),'compute/compute-cluster',x,635,'Host group '+str(i+1),'Dual-homing not depicted',w=180,h=142)
    d.edge('leaf'+str(i),'host'+str(i),kind='physical',palette='teal',sp='s',tp='n')
d.save()

# Hybrid site connectivity.
d=Diagram('hybrid-cloud','Hybrid-cloud connectivity','On-premises and cloud networks connected through private circuits, with a separate Internet edge.',1540,750)
d.group('onprem',35,140,432,550,'On-premises datacenter',style='boundary')
d.group('wan',517,140,489,550,'Provider networks',palette='slate')
d.group('cloud',1056,140,449,550,'Cloud environment',style='boundary')
d.node('hosts','compute/compute-cluster',61,251,'Application hosts',w=170,h=140)
d.node('edge','network/border-router',267,251,'Border router','BGP adjacency',w=175,h=140)
d.node('circuit','cloud/dedicated-circuit',666,250,'Private circuits','Provider-managed transport',w=190,h=144)
d.node('cgw','network/router',1080,251,'Cloud gateway',w=175,h=140)
d.node('apps','cloud/vpc',1291,251,'Application VPC',w=175,h=140)
d.node('fw','security/firewall',264,481,'Internet edge',w=175,h=140,palette='red')
d.node('inet','network/internet',666,481,'Internet',w=190,h=140)
d.edge('hosts','edge',label='LAN',kind='physical');d.edge('edge','circuit',label='Circuit',kind='physical');d.edge('circuit','cgw',label='Circuit',kind='physical');d.edge('cgw','apps',kind='physical')
d.edge('edge','fw',kind='physical',sp='s',tp='n');d.edge('fw','inet',kind='physical',palette='slate');d.save()

# Firewall enforced zones, small controls at zone boundaries.
d=Diagram('segmented-network','Network segmentation','Show the enforcement points between trust zones and label the permitted application flows.',1720,680)
for gid,x,w,title,pal in [('external',36,252,'Untrusted','slate'),('dmz',358,308,'DMZ','orange'),('appzone',754,389,'Application zone','blue'),('datazone',1232,451,'Data zone','teal')]:d.group(gid,x,156,w,414,title,palette=pal,style='boundary')
d.node('client','network/internet',69,286,'External client',w=182,h=140)
d.node('waf','security/waf',413,286,'WAF / ingress',w=198,h=140,palette='red')
d.node('api','software/backend',850,286,'Application API',w=196,h=140)
d.node('db','data/relational-db',1374,286,'Database',w=204,h=140,palette='teal')
d.edge('client','waf','HTTPS',palette='blue');d.edge('waf','api','Approved requests',palette='blue');d.edge('api','db','DB policy',palette='teal')
d.txt('z-note',399,479,1220,44,'Dashed boxes show trust scope. Actual access is enforced by the named controls and workload/network policies.',16)
d.save()

# Identity, policy and enforcement are distinct components.
d=Diagram('zero-trust-access','Identity-aware access','Identity and policy decisions are separate from the component that enforces access.',1530,790)
d.group('userzone',35,145,273,518,'User / device',style='boundary',palette='slate')
d.group('control',355,145,1138,253,'Identity and policy',palette='purple')
d.group('protected',355,438,1138,285,'Protected application path',style='boundary',palette='teal')
d.node('u','identity/user',71,336,'User + device',w=196,h=145)
d.node('idp','identity/identity-provider',427,220,'Identity provider','Authentication / MFA',w=219,h=145,palette='purple')
d.node('pol','security/policy-engine',764,220,'Policy engine','Identity + device + context',w=219,h=145,palette='purple')
d.node('audit','observability/audit-log',1165,220,'Audit events',w=219,h=145,palette='orange')
d.node('pep','security/security-gateway',427,524,'Access proxy','Policy enforcement',w=219,h=145,palette='red')
d.node('svc','software/backend',990,524,'Internal application',w=248,h=145,palette='teal')
d.edge('u','idp','Sign in',palette='purple',sp='n',tp='w',points=[(169,292)])
d.edge('idp','pol','Identity',palette='purple',kind='control')
d.edge('u','pep','Request',sp='s',tp='w',points=[(169,596.5)],label_x=327,label_y=582)
d.edge('pep','pol','Decision request',palette='purple',kind='control',sp='n',tp='s',points=[(536.5,416),(873.5,416)],label_x=731,label_y=416)
d.edge('pep','svc','Allow only when authorized',palette='teal')
d.edge('svc','audit','Record',palette='orange',kind='control',sp='e',tp='s',points=[(1274.5,596.5)],label_x=1335,label_y=481)
d.save()

# K8s north-south access and separate storage connection.
d=Diagram('kubernetes-ingress','Kubernetes application traffic','A logical request path through a gateway, service and application pods; storage and control are distinct.',1600,800)
d.group('k8s',350,136,1209,591,'Kubernetes cluster','Namespace boundaries are logical scope, not automatic security enforcement.',style='boundary')
d.node('client','software/browser',50,292,'Client',w=191,h=140)
d.node('gw','kubernetes/gateway-api',411,292,'Gateway / ingress',w=199,h=140)
d.node('svc','kubernetes/service',724,292,'Service',w=184,h=140)
d.node('pod1','kubernetes/pod',1044,236,'Pod 1',w=166,h=127)
d.node('pod2','kubernetes/pod',1044,460,'Pod 2',w=166,h=127)
d.node('db','data/relational-db',1327,341,'Database',w=182,h=144,palette='teal')
d.node('ctrl','kubernetes/control-plane',496,529,'Control plane',w=244,h=143,palette='slate')
d.edge('client','gw','HTTPS');d.edge('gw','svc','Route');d.edge('svc','pod1',sp='e',tp='w');d.edge('svc','pod2',sp='s',tp='w',points=[(816,523.5)])
d.edge('pod1','db',palette='teal',sp='e',tp='n',points=[(1418,299.5)])
d.edge('pod2','db',palette='teal',sp='e',tp='s',points=[(1418,523.5)])
d.edge('ctrl','svc','Control',palette='slate',kind='control',sp='n',tp='s',points=[(618,487),(816,487)],label_x=738,label_y=486)
d.save()

# CI/CD flow with explicit human approval and rollback path.
d=Diagram('secure-ci-cd','Build, verify and deploy','Separate build and verification from the human approval gate and production deployment.',1670,775)
d.group('delivery',35,142,1600,547,'Software delivery pipeline',palette='purple')
xs=[63,381,699,1017,1335]
for i,(aid,lab,det) in enumerate([('devops/git-repository','Source repository','Reviewable changes'),('devops/ci-build','Build + tests','Repeatable CI job'),('devops/sca','Security checks','SAST / SCA / policy'),('devops/release-approval','Release approval','Explicit human gate'),('devops/cd-release','Deploy','Versioned release')]):d.node('n'+str(i),aid,xs[i],253,lab,det,w=239,h=150,palette='purple')
for i,lab in enumerate(['Commit','Artifact','Pass','Approve']):d.edge('n'+str(i),'n'+str(i+1),lab,palette='purple')
d.node('registry','devops/artifact-registry',381,508,'Artifact registry','Immutable version / digest',w=239,h=145,palette='teal')
d.node('rollback','devops/rollback',1017,508,'Rollback','Known-good version',w=239,h=145,palette='orange')
d.edge('n1','registry','Store',palette='teal',sp='s',tp='n',label_x=542,label_y=459)
d.edge('n4','rollback','Restore',palette='orange',sp='s',tp='e',points=[(1454.5,580.5)])
d.save()

# Application overview: synchronous requests, async work, data.
d=Diagram('software-overview','Application overview','Keep the main request path separate from asynchronous work and persistent data.',1600,780)
d.group('app',341,142,922,573,'Application boundary',style='boundary')
d.node('user','software/browser',43,284,'Web client',w=199,h=144)
d.node('web','software/frontend',402,284,'Frontend',w=203,h=144)
d.node('api','software/rest-api',747,284,'Application API',w=204,h=144)
d.node('db','data/relational-db',1340,284,'Database',w=210,h=144,palette='orange')
d.node('queue','software/message-queue',747,535,'Job queue',w=204,h=144,palette='teal')
d.node('worker','software/background-worker',1020,535,'Worker',w=204,h=144,palette='teal')
d.edge('user','web','HTTPS');d.edge('web','api','Request');d.edge('api','db','SQL',palette='orange')
d.edge('api','queue','Enqueue',palette='teal',sp='s',tp='n',label_x=897,label_y=490)
d.edge('queue','worker','Consume',palette='teal')
d.edge('worker','db','Write result',palette='orange',sp='e',tp='s',points=[(1445,607)],label_x=1326,label_y=595)
d.save()

# Event-driven flow.
d=Diagram('event-driven','Event-driven processing','One published event can feed independent consumers. Delivery guarantees are application-specific.',1520,760)
d.group('domain',37,144,337,496,'Producer domain',style='boundary',palette='blue')
d.group('buszone',427,144,314,496,'Messaging',palette='teal')
d.group('consumers',795,144,687,496,'Independent consumers',palette='purple')
d.node('producer','software/backend',111,336,'Producer',w=187,h=146)
d.node('topic','software/topic',485,336,'Event topic',w=192,h=146,palette='teal')
d.node('c1','software/background-worker',843,220,'Consumer A',w=195,h=145,palette='purple')
d.node('c2','software/background-worker',843,440,'Consumer B',w=195,h=145,palette='purple')
d.node('db1','data/relational-db',1240,220,'Store A',w=185,h=145,palette='orange')
d.node('db2','data/document-db',1240,440,'Store B',w=185,h=145,palette='orange')
d.edge('producer','topic','Publish',palette='teal');d.edge('topic','c1',palette='purple',sp='e',tp='w');d.edge('topic','c2',palette='purple',sp='e',tp='w')
d.edge('c1','db1','Persist',palette='orange');d.edge('c2','db2','Persist',palette='orange');d.save()

# Generic agent tools, no internal project name.
d=Diagram('agent-mcp-tools','An agent with controlled tool access','Read-only data access and privileged actions have different tools, policies and approval paths.',1750,845)
d.group('agentzone',35,145,639,622,'Agent runtime',style='boundary',palette='teal')
d.group('tools',720,145,986,622,'Tool and data boundary','Tool access is explicit; the model does not get unrestricted database credentials.',style='boundary',palette='purple')
d.node('user','identity/user',65,316,'User',w=164,h=136)
d.node('agent','ai/ai-agent',376,316,'Agent loop',w=223,h=145,palette='teal')
d.node('model','ai/llm',376,568,'Reasoning model',w=223,h=145,palette='teal')
d.node('mcp','ai/mcp-server',776,316,'MCP server','Registered tool contracts',w=215,h=145,palette='purple')
d.node('db','data/relational-db',1413,225,'Database','Read-only queries',w=244,h=145,palette='orange')
d.node('logs','observability/logs',1413,429,'Log system','Bounded search',w=244,h=145,palette='orange')
d.node('approval','ai/human-approval',1013,593,'Human approval','Required for mutation',w=238,h=145,palette='red')
d.node('action','ai/tool',1413,633,'Action tool',w=244,h=113,palette='red')
d.edge('user','agent','Task');d.edge('agent','model','Inference',palette='teal',sp='s',tp='n',label_x=546,label_y=522)
d.edge('agent','mcp','Tool call',palette='purple')
d.edge('mcp','db','Read',palette='orange',sp='e',tp='w',points=[(1216,388.5),(1216,297.5)])
d.edge('mcp','logs','Search',palette='orange',sp='e',tp='w',points=[(1190,388.5),(1190,501.5)])
d.edge('mcp','approval','Request approval',palette='red',kind='control',sp='s',tp='n',points=[(883.5,541),(1132,541)],label_x=1062,label_y=541)
d.edge('approval','action','Approved action',palette='red',label_x=1332,label_y=658);d.save()

# Disaggregated inference illustrative.
d=Diagram('disaggregated-inference','Prefill and decode workers','Move the prepared KV cache between workers, then continue token generation at the decode worker.',1660,704)
d.group('serving',331,142,1286,479,'Inference serving boundary',style='boundary',palette='teal')
d.node('request','software/browser',45,303,'Client request',w=209,h=148)
d.node('router','ai/router',399,303,'Request router',w=212,h=148,palette='teal')
d.node('prefill','ai/prefill-worker',719,303,'Prefill worker','Process the prompt',w=212,h=148,palette='teal')
d.node('kv','ai/kv-cache',1039,303,'KV-cache transfer','Transport depends on setup',w=212,h=148,palette='purple')
d.node('decode','ai/decode-worker',1359,303,'Decode worker','Generate tokens',w=212,h=148,palette='teal')
for a,b,lab,pal in [('request','router','Prompt','blue'),('router','prefill','Assign','teal'),('prefill','kv','Cache','purple'),('kv','decode','Place','purple')]:d.edge(a,b,lab,palette=pal)
d.txt('kv-note',401,517,1168,48,'A transport example can expand the KV-cache transfer into sender NIC, multiple paths, receiver memory and recovery panels.',17)
d.save()

# Recovery mechanisms without promising RPO/RTO.
d=Diagram('backup-dr','Replication and recoverable backups','Replication, backup retention and restore testing answer different recovery needs.',1500,779)
d.group('primaryzone',36,144,417,515,'Primary site',style='boundary')
d.group('secondary',523,144,418,515,'Recovery site',style='boundary',palette='teal')
d.group('backupzone',1011,144,452,515,'Backup boundary',style='boundary',palette='purple')
d.node('primary','data/relational-db',119,267,'Primary database',w=246,h=145,palette='orange')
d.node('replica','data/database-replica',611,267,'Replica',w=242,h=145,palette='teal')
d.node('immutable','storage/immutable-backup',1108,267,'Immutable backup',w=251,h=145,palette='purple')
d.node('test','storage/backup',1108,472,'Restore test','Verify recovery procedure',w=251,h=145,palette='green')
d.edge('primary','replica','Replicate',palette='teal',kind='replication')
d.edge('primary','immutable','Scheduled backup',palette='purple',sp='n',tp='n',points=[(242,223),(1233.5,223)],label_x=737,label_y=222)
d.edge('immutable','test',palette='green',sp='s',tp='n')
d.txt('rpo',91,508,785,69,'Define RPO and RTO per workload. A successful replication link or backup job is not proof that a restore will work.',18)
d.save()

# Telemetry parallel streams.
d=Diagram('observability-pipeline','From telemetry to an actionable alert','Logs, metrics and traces are separate signals that can be correlated during investigation.',1550,820)
d.group('signals',449,145,1057,592,'Observability pipeline',palette='orange')
d.node('apps','software/backend',49,354,'Applications',w=220,h=145)
for aid,asset,lab,y in [('logs','observability/logs','Logs',230),('metrics','observability/metrics','Metrics',416),('traces','observability/traces','Traces',602)]:
    d.node(aid,asset,509,y,lab,w=168,h=116,palette='orange')
    d.edge('apps',aid,palette='orange',sp='e',tp='w',route='straight')
d.node('collector','observability/collector',856,416,'Collector / stores',w=230,h=145,palette='orange')
d.node('dash','observability/dashboard',1231,237,'Dashboard',w=220,h=145,palette='orange')
d.node('alert','observability/alert',1231,504,'Alert + response',w=220,h=145,palette='red')
for aid in ('logs','metrics','traces'):d.edge(aid,'collector',palette='orange',sp='e',tp='w')
d.edge('collector','dash',palette='orange',sp='e',tp='w');d.edge('collector','alert',palette='red',sp='e',tp='w');d.save()

# Threat model data-flow notation, no attack procedure.
d=Diagram('threat-model-dfd','Threat-model data flows','Track which data crosses each trust boundary and which component is responsible for checking it.',1580,718)
d.group('browser-zone',36,150,311,455,'User-controlled context',style='boundary',palette='slate')
d.group('app-zone',423,150,1116,455,'Application trust boundary',style='boundary',palette='blue')
d.node('actor','identity/user',96,292,'External actor',w=192,h=148)
d.node('api','presentation/process',492,292,'Request handler','Process: validate / authorize',w=237,h=148)
d.node('policy','security/policy-engine',880,292,'Policy decision','Context and authorization',w=237,h=148,palette='red')
d.node('store','presentation/data-store',1255,292,'Sensitive store','Data classification applies',w=237,h=148,palette='orange')
d.edge('actor','api','Untrusted input');d.edge('api','policy','Request context',palette='red');d.edge('policy','store','Authorized access',palette='orange')
d.txt('dfd-note',482,509,991,62,'For every crossing: identify the data, caller identity, validation, authorization, logging and failure behavior. Boundaries do not enforce policy by themselves.',16)
d.save()

# Sequence-style workflow uses lifelines and time-ordered labels, not physical topology.
d=Diagram('sequence-request','Request, work and response','A sequence view: horizontal arrows are messages and time progresses downward.',1380,820)
xs=[82,423,764,1105]
for i,(asset,lab) in enumerate([('software/browser','Client'),('network/api-gateway','Gateway'),('software/backend','Service'),('data/relational-db','Database')]):
    d.node('head'+str(i),asset,xs[i],148,lab,w=186,h=126)
    d.s['nodes'].append(dict(id='end'+str(i),kind='text',x=xs[i]+91,y=725,w=4,h=4,label=''))
    d.edge('head'+str(i),'end'+str(i),palette='slate',kind='control',arrow='none',sp='s',tp='n',width=1)
# Invisible message anchor nodes mark ordered events without claiming extra servers.
for i,(s,t_,y,label,pal,kind) in enumerate([(0,1,337,'1. HTTPS request','blue','data'),(1,2,420,'2. Validated request','blue','data'),(2,3,503,'3. Query','orange','data'),(3,2,589,'4. Results','orange','feedback'),(2,0,679,'5. Response','teal','feedback')]):
    for ident,col in ((f'm{i}a',s),(f'm{i}b',t_)):
        d.s['nodes'].append(dict(id=ident,kind='text',x=xs[col]+93,y=y,w=1,h=1,label=''))
    d.edge(f'm{i}a',f'm{i}b',label,palette=pal,kind=kind,route='straight',sp='e' if s<t_ else 'w',tp='w' if s<t_ else 'e',label_x=(xs[s]+xs[t_])/2+93,label_y=y-14)
d.s['description']='Logical message sequence with example steps only; no protocol handshake or timing guarantee is implied.'
d.save()
# ---------------------------------------------------------------------------------------------
# Department process templates: cross-functional swimlanes on a fixed column grid.
# Lanes are roles, columns are steps in time. Tasks are component cards; decisions, parallel
# gateways, timers and start/end points are captioned symbols. Solid blue = process flow,
# dashed orange = hand-off to or from an external party, dashed red = rework or exception.
X0,COLW,NW,NH,LANE_H,LGAP=64,240,170,142,246,10
PROCESS_FOOTER='Illustrative process. Lanes are roles; steps, thresholds and timings are examples, not policy.'

class Lanes(Diagram):
    def __init__(self,slug,title,subtitle,lanes,cols,top=124,description=''):
        w=X0+(cols-1)*COLW+NW+64;h=top+len(lanes)*(LANE_H+LGAP)+66
        super().__init__(slug,title,subtitle,w,h)
        self.top=top;self.lane_index={}
        self.s['footer']=PROCESS_FOOTER
        if description:self.s['description']=description
        for i,(lid,ltitle,pal) in enumerate(lanes):
            self.lane_index[lid]=i
            self.group(lid,30,self.ly(lid),w-60,LANE_H,ltitle,palette=pal,style='lane')
    def ly(self,lane):return self.top+self.lane_index[lane]*(LANE_H+LGAP)
    def cx(self,col):return X0+col*COLW
    def mid(self,lane):return self.ly(lane)+52+NH/2
    def task(self,id,lane,col,asset,label,detail='',palette='blue'):
        return self.node(id,asset,self.cx(col),self.ly(lane)+52,label,detail,NW,NH,palette,lane)
    def sym(self,id,lane,col,asset,caption,w=124,h=108,palette='blue'):
        self.s['nodes'].append(dict(id=id,kind='symbol',asset=asset,x=self.cx(col)+(NW-w)/2,y=self.mid(lane)-h/2,w=w,h=h,label=caption,caption=caption,palette=palette,group=lane));return id
    def gate(self,id,lane,col,caption):return self.sym(id,lane,col,'presentation/decision',caption)
    def fork(self,id,lane,col,caption):return self.sym(id,lane,col,'business/gateway-parallel',caption)
    def event(self,id,lane,col,caption):return self.sym(id,lane,col,'presentation/start-end',caption,104,100,'slate')
    def flow(self,a,b,label='',**kw):self.edge(a,b,label,'blue','data',**kw)
    def handoff(self,a,b,label='',**kw):self.edge(a,b,label,'orange','control',**kw)
    def rework(self,a,b,label='',**kw):self.edge(a,b,label,'red','feedback',**kw)
    def legend(self,external=True,rework=True):
        items=[{'label':'Process flow','palette':'blue'}]
        if external:items.append({'label':'Hand-off with an external party','palette':'orange','dashed':True})
        if rework:items.append({'label':'Rework or exception','palette':'red','dashed':True})
        self.s['legend']=items

# 1. Engineering: change delivery with review loop and rollback.
d=Lanes('eng-platform-delivery','Engineering: from pull request to production','A change moves through peer review, automated checks and a release gate; an unhealthy deploy rolls back.',
  [('dev','Developer','blue'),('rev','Reviewer','purple'),('ci','CI/CD pipeline','teal'),('ops','Platform team','slate')],10,
  description='Developer opens a pull request. Reviewer approves or requests changes, which return to the developer. Approved changes are built, tested and scanned by CI/CD. The platform team approves the release and deploys it; a failed health check rolls back to the previous release.')
d.event('start','dev',0,'Change ready')
d.task('pr','dev',1,'devops/pull-request','Open pull request','Branch + description')
d.task('review','rev',2,'devops/code-review','Review changes','Code owners')
d.gate('approved','rev',3,'Approved?')
d.task('build','ci',4,'devops/ci-build','Build and test','Unit + integration')
d.task('scan','ci',5,'devops/sast','Security scan','SAST / SCA / SBOM')
d.task('release','ops',6,'devops/release-approval','Release approval','Change window')
d.task('deploy','ops',7,'devops/cd-release','Deploy','Progressive rollout')
d.task('rollback','ci',8,'devops/rollback','Roll back','Previous release')
d.event('done','ops',9,'Released')
d.flow('start','pr');d.flow('pr','review','Ready');d.flow('review','approved')
d.flow('approved','build','Yes')
d.rework('approved','pr','Changes requested',sp='n',tp='e')
d.flow('build','scan');d.flow('scan','release','Pass');d.flow('release','deploy','Go')
d.flow('deploy','done','Healthy')
d.rework('deploy','rollback','Unhealthy',sp='n',tp='w')
d.legend(external=False);d.save()

# 2. Security operations: incident response with parallel containment.
d=Lanes('sec-incident-response','Security: incident response','An alert is triaged, declared, contained in parallel with evidence preservation and communications, then reviewed.',
  [('det','Detection','orange'),('soc','SOC analyst','red'),('eng','On-call engineer','blue'),('ic','Incident commander','slate')],10,
  description='Detection raises a correlated alert. The SOC analyst triages it; false positives are tuned and closed. A true positive is declared by the incident commander, who starts three parallel tracks: the engineer contains the host, the analyst preserves evidence, and the commander notifies stakeholders on a fixed update cadence. After eradication and recovery, a post-incident review closes the incident.')
d.task('alert','det',0,'observability/alert','SIEM alert','Correlated detection',palette='orange')
d.task('triage','soc',1,'observability/incident','Triage alert','Enrich and scope',palette='red')
d.gate('tp','soc',2,'True positive?')
d.task('tune','det',3,'security/siem','Tune detection','Suppress false positive',palette='orange')
d.event('fp','det',4,'Closed: false positive')
d.task('declare','ic',3,'business/ticket','Declare incident','Severity + owner',palette='slate')
d.fork('par','ic',4,'Respond in parallel')
d.task('contain','eng',5,'security/quarantine','Contain host','Isolate endpoint')
d.task('evidence','soc',5,'observability/audit-log','Preserve evidence','Chain of custody',palette='red')
d.task('notify','ic',5,'business/email','Notify stakeholders','Legal, leadership',palette='slate')
d.sym('cadence','ic',6,'business/timer','Update every 4 h',palette='slate')
d.task('recover','eng',6,'security/edr','Eradicate and recover','Patch, rotate secrets')
d.task('pir','ic',8,'presentation/note','Post-incident review','Lessons + actions',palette='slate')
d.event('closed','ic',9,'Closed')
d.flow('alert','triage');d.flow('triage','tp')
d.flow('tp','tune','No');d.flow('tune','fp')
d.flow('tp','declare','Yes',sp='s',tp='w')
d.flow('declare','par')
d.flow('par','contain');d.flow('par','evidence',sp='n',tp='w');d.flow('par','notify')
d.flow('notify','cadence');d.flow('contain','recover')
d.flow('recover','pir')
d.flow('evidence','pir','Evidence',sp='e',tp='n')
d.flow('pir','closed')
d.legend(external=False,rework=False);d.save()

# 3. IT: new-hire access provisioning.
d=Lanes('it-onboarding-access','IT: new-hire access provisioning','From an HR-system ticket to a verified first login, with an extra approval for privileged roles.',
  [('hr','HR system','slate'),('desk','Service desk','blue'),('idm','Identity admin','purple'),('sec','Security','red')],10,
  description='The HR system opens an onboarding ticket. The service desk validates it and returns incomplete requests. The identity admin creates the account and assigns role groups while the service desk provisions a laptop. Privileged roles need a time-bound approval from Security. The new hire enrols MFA and the service desk verifies the first login.')
d.event('start','hr',0,'New hire confirmed')
d.task('ticket','hr',1,'business/ticket','Create onboarding ticket','From HRIS record',palette='slate')
d.task('validate','desk',2,'business/form','Validate request','Role, start date')
d.gate('complete','desk',3,'Complete?')
d.task('account','idm',4,'identity/user','Create account','Directory + mailbox',palette='purple')
d.task('laptop','desk',4,'compute/laptop','Provision laptop','Imaged + encrypted')
d.task('groups','idm',5,'identity/group','Assign role groups','Least privilege',palette='purple')
d.gate('priv','idm',6,'Privileged role?')
d.task('approve','sec',6,'identity/privileged-access','Approve privileged access','Time-bound',palette='red')
d.task('mfa','desk',7,'identity/mfa','Enrol MFA','Day-1 session')
d.task('verify','desk',8,'status/approved','Verify first login','Close ticket')
d.event('live','desk',9,'Access live')
d.flow('start','ticket');d.flow('ticket','validate');d.flow('validate','complete')
d.rework('complete','ticket','Missing info',sp='n',tp='e')
d.flow('complete','account','Yes',sp='s',tp='w')
d.flow('account','laptop');d.flow('account','groups');d.flow('groups','priv')
d.flow('priv','mfa','No');d.flow('priv','approve','Yes')
d.flow('approve','mfa',sp='e',tp='s');d.flow('laptop','mfa')
d.flow('mfa','verify');d.flow('verify','live')
d.legend(external=False);d.save()

# 4. Finance: procure-to-pay with a spend threshold and three-way match.
d=Lanes('fin-procurement-approval','Finance: procure to pay','A requisition is approved by the budget owner, escalated to the CFO above a threshold, ordered, matched and paid.',
  [('req','Requester','blue'),('mgr','Manager','purple'),('fin','Finance','teal'),('cfo','CFO','slate'),('ven','Vendor (external)','orange')],11,
  description='The requester submits a requisition. The manager approves or rejects it. Finance routes requests above the threshold to the CFO, then issues a purchase order to the vendor. The vendor delivers and invoices. Finance performs a three-way match of order, receipt and invoice; a mismatch is disputed with the vendor, and a match is paid.')
d.event('start','req',0,'Need identified')
d.task('submit','req',1,'business/form','Submit requisition','Item, cost, budget')
d.task('mreview','mgr',2,'business/approval','Manager review','Budget owner',palette='purple')
d.gate('mok','mgr',3,'Approved?')
d.event('rejected','req',3,'Rejected')
d.gate('threshold','fin',4,'Over $5k?')
d.task('cfoapprove','cfo',5,'business/approval','CFO approval','Spend policy',palette='slate')
d.task('po','fin',6,'business/purchase-order','Issue purchase order','ERP',palette='teal')
d.task('deliver','ven',7,'business/vendor','Deliver goods','Fulfil order',palette='orange')
d.task('invoice','ven',8,'business/invoice','Send invoice','References PO',palette='orange')
d.task('match','fin',8,'observability/audit-log','Three-way match','PO, receipt, invoice',palette='teal')
d.gate('matched','fin',9,'Match?')
d.task('pay','fin',10,'business/payment','Pay vendor','Payment run',palette='teal')
d.event('paid','ven',10,'Paid')
d.flow('start','submit');d.flow('submit','mreview');d.flow('mreview','mok')
d.flow('mok','rejected','No');d.flow('mok','threshold','Yes')
d.flow('threshold','cfoapprove','Yes');d.flow('threshold','po','No');d.flow('cfoapprove','po',sp='e',tp='s')
d.handoff('po','deliver','Purchase order',sp='e',tp='n')
d.flow('deliver','invoice')
d.handoff('invoice','match','Invoice')
d.flow('match','matched')
d.rework('matched','invoice','Dispute',sp='s',tp='e')
d.flow('matched','pay','Yes')
d.handoff('pay','paid','Remittance')
d.legend();d.save()

# 5. HR: employee onboarding with parallel preparation.
d=Lanes('hr-employee-onboarding','HR: employee onboarding','From an accepted offer to a 30-day check-in, with HR, the hiring manager and IT preparing in parallel.',
  [('hire','New hire','blue'),('hr','HR','purple'),('mgr','Hiring manager','teal'),('it','IT','slate')],11,
  description='The new hire accepts the offer. HR sends the contract, the new hire signs it, and HR creates the personnel record. HR, the hiring manager and IT then prepare in parallel: orientation, a buddy, and accounts with a laptop. When all three are ready the new hire starts. After 30 days the manager holds a check-in and onboarding is complete.')
d.event('start','hire',0,'Offer accepted')
d.task('contract','hr',1,'business/contract','Send contract','E-signature',palette='purple')
d.task('sign','hire',2,'identity/user','Sign contract','Returns documents')
d.task('record','hr',3,'data/document-db','Create HR record','Personnel file',palette='purple')
d.fork('split','hr',4,'Prepare in parallel')
d.task('orient','hr',5,'business/calendar','Schedule orientation','Day-1 agenda',palette='purple')
d.task('buddy','mgr',5,'identity/group','Assign a buddy','Team introductions',palette='teal')
d.task('itprep','it',5,'business/ticket','IT onboarding','Account + laptop',palette='slate')
d.fork('join','hr',6,'All ready')
d.task('day1','hire',7,'compute/workstation','First day','Desk, laptop, access')
d.sym('wait','mgr',8,'business/timer','After 30 days',palette='teal')
d.task('checkin','mgr',9,'business/chat','30-day check-in','Goals + feedback',palette='teal')
d.event('done','hr',10,'Onboarded')
d.flow('start','contract',sp='s',tp='w');d.flow('contract','sign',sp='n',tp='w');d.flow('sign','record',sp='s',tp='w')
d.flow('record','split')
d.flow('split','orient');d.flow('split','buddy',sp='s',tp='w');d.flow('split','itprep',sp='s',tp='w')
d.flow('orient','join');d.flow('buddy','join',sp='e',tp='s');d.flow('itprep','join',sp='e',tp='s')
d.flow('join','day1',sp='n',tp='w');d.flow('day1','wait',sp='e',tp='n');d.flow('wait','checkin');d.flow('checkin','done',sp='e',tp='s')
d.legend(external=False,rework=False);d.save()

# 6. Sales: lead to cash.
d=Lanes('sales-lead-to-cash','Sales: lead to cash','An inbound enquiry is qualified, quoted and negotiated; a won deal becomes an order, an invoice and recognised revenue.',
  [('cust','Customer (external)','orange'),('sales','Sales','blue'),('ops','Sales operations','purple'),('fin','Finance','teal')],11,
  description='A customer enquiry reaches Sales, who qualify it; unqualified leads are closed. Sales sends a quote and negotiates with the customer. A lost deal is closed; a won deal becomes an order in sales operations. Finance invoices the customer, receives payment and reports the revenue.')
d.event('start','cust',0,'Enquiry')
d.task('qualify','sales',1,'identity/user','Qualify lead','Need, budget, timing')
d.gate('qualified','sales',2,'Qualified?')
d.event('dq','ops',2,'Disqualified')
d.task('quote','sales',3,'business/contract','Build quote','Pricing + terms')
d.task('negotiate','cust',4,'business/chat','Review and negotiate','Customer decision',palette='orange')
d.gate('won','sales',5,'Won?')
d.event('lost','ops',5,'Closed-lost')
d.task('order','ops',6,'software/workflow','Create order','CRM to ERP',palette='purple')
d.task('invoice','fin',7,'business/invoice','Invoice customer','Billing terms',palette='teal')
d.task('pay','cust',8,'business/payment','Pay invoice','Customer AP',palette='orange')
d.task('report','fin',9,'business/report','Recognise revenue','Bookings to cash',palette='teal')
d.event('cash','fin',10,'Cash collected')
d.handoff('start','qualify','Enquiry')
d.flow('qualify','qualified');d.flow('qualified','dq','No');d.flow('qualified','quote','Yes')
d.handoff('quote','negotiate','Quote',sp='n',tp='w');d.handoff('negotiate','won','Decision',sp='e',tp='n')
d.flow('won','lost','No');d.flow('won','order','Yes',sp='e',tp='n')
d.flow('order','invoice',sp='s',tp='w')
d.handoff('invoice','pay','Invoice',sp='n',tp='w')
d.handoff('pay','report','Payment',sp='e',tp='n')
d.flow('report','cash')
d.legend(rework=False);d.save()

# 7. IT change management: change request through CAB approval to a verified change.
d=Lanes('it-change-approval','IT: change approval','A change request is risk-assessed; standard changes are pre-approved, normal changes go to the change advisory board, and a failed verification is backed out.',
  [('req','Change owner','blue'),('mgr','Change manager','purple'),('cab','Change advisory board','slate'),('ops','Implementer','teal')],11,
  description='The change owner raises a request with scope, risk and a backout plan. The change manager assesses it. Standard changes are pre-approved and go straight to scheduling; normal changes go to the change advisory board, which approves them or sends them back for revision. The change manager schedules an approved change outside freeze periods. The implementer makes the change in its window and verifies it; a failed verification is backed out. The change manager reviews the result and closes the change.')
d.event('start','req',0,'Change needed')
d.task('rfc','req',1,'business/form','Raise change request','Scope, risk, backout')
d.task('assess','mgr',2,'security/security-review','Assess risk','Impact + category',palette='purple')
d.gate('standard','mgr',3,'Standard change?')
d.task('cabreview','cab',4,'business/approval','CAB review','Weekly meeting',palette='slate')
d.gate('approved','cab',5,'Approved?')
d.task('schedule','mgr',6,'business/calendar','Schedule window','Check freeze calendar',palette='purple')
d.task('implement','ops',7,'devops/cd-release','Implement change','In change window',palette='teal')
d.gate('verified','ops',8,'Verified?')
d.task('backout','ops',9,'devops/rollback','Back out','Run backout plan',palette='teal')
d.task('review','mgr',9,'business/report','Review and close','Post-implementation',palette='purple')
d.event('closed','mgr',10,'Closed')
d.flow('start','rfc');d.flow('rfc','assess',sp='s',tp='w');d.flow('assess','standard')
d.flow('standard','schedule','Yes: pre-approved')
d.flow('standard','cabreview','No',sp='s',tp='w')
d.flow('cabreview','approved')
d.rework('approved','rfc','Revise',sp='n',tp='e')
d.flow('approved','schedule','Yes',sp='e',tp='s')
d.flow('schedule','implement',sp='e',tp='n')
d.flow('implement','verified')
d.flow('verified','review','Yes',sp='n',tp='w')
d.rework('verified','backout','No')
d.flow('backout','review','Backed out',sp='n',tp='s')
d.flow('review','closed')
d.legend(external=False);d.save()

# 8. Customer support: tiered escalation to engineering.
d=Lanes('support-escalation','Customer support: tiered escalation','A customer issue is handled at L1, escalated to L2 when unresolved, and to engineering for product defects.',
  [('cust','Customer (external)','orange'),('l1','L1 support','blue'),('l2','L2 support','purple'),('eng','Engineering','slate')],10,
  description='The customer reports an issue and L1 creates a ticket and troubleshoots it with a runbook. Issues resolved at L1 are confirmed with the customer. Unresolved issues escalate to L2 under a response SLA. L2 investigates; product defects go to engineering for a fix and release, other issues get a workaround. The customer confirms the resolution and the ticket closes.')
d.event('start','cust',0,'Issue noticed')
d.task('ticket','l1',1,'business/ticket','Create ticket','Email, chat or portal')
d.task('trouble','l1',2,'identity/user','Troubleshoot','Known-issue runbook')
d.gate('res1','l1',3,'Resolved?')
d.sym('sla','l2',3,'business/timer','Respond within 8 h',palette='purple')
d.task('investigate','l2',4,'observability/logs','Investigate','Logs + reproduce',palette='purple')
d.gate('defect','l2',5,'Product defect?')
d.task('workaround','l2',6,'presentation/note','Apply workaround','Document in KB',palette='purple')
d.task('fix','eng',6,'devops/pull-request','Fix defect','Linked to ticket',palette='slate')
d.task('ship','eng',7,'devops/cd-release','Ship fix','Hotfix release',palette='slate')
d.task('confirm','cust',8,'business/email','Confirm resolution','Customer reply',palette='orange')
d.event('closed','cust',9,'Ticket closed')
d.handoff('start','ticket','Report issue')
d.flow('ticket','trouble');d.flow('trouble','res1')
d.handoff('res1','confirm','Yes: solution sent',sp='n',tp='w',points=[(d.cx(3)+NW/2,d.ly('cust')+40),(d.cx(8)-40,d.ly('cust')+40),(d.cx(8)-40,d.mid('cust'))])
d.flow('res1','investigate','No')
d.flow('sla','investigate')
d.flow('investigate','defect');d.flow('defect','workaround','No');d.flow('defect','fix','Yes')
d.flow('fix','ship')
d.handoff('workaround','confirm','Workaround',sp='n',tp='s')
d.handoff('ship','confirm','Fix released',sp='e',tp='s')
d.flow('confirm','closed')
d.legend(rework=False);d.save()

print(f'Built {len(list(OUT.glob("*.json")))} templates.')
