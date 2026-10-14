"""Bounded scene validation and layout helpers. No arbitrary XML or CSS is accepted."""
from __future__ import annotations
import json, math, re
from functools import lru_cache
from .library import ROOT, index

# C0 controls (except tab/newline/CR), DEL, lone surrogates, XML non-characters, zero-width space,
# word joiner, BOM, bidi overrides/isolates and the Unicode tag block. These break XML output,
# spoof label direction or hide text from a human reviewer; ZWJ/ZWNJ/LRM/RLM stay legal for scripts.
ILLEGAL_TEXT=re.compile('[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\ud800-\udfff￾￿​⁠-⁤﻿‪-‮⁦-⁩\U000e0000-\U000e007f]')
MAX_ISSUES=200

@lru_cache(maxsize=1)
def schema() -> dict:
    return json.loads((ROOT/'scene.schema.json').read_text(encoding='utf-8'))

def structural_errors(value, spec: dict, path: str='$') -> list[dict]:
    """Evaluate the deliberately small JSON Schema subset used by this package.

    This is not a general-purpose JSON Schema engine. The bundled schema uses only
    type, properties, required, additionalProperties, items, bounds, enum, const,
    pattern, and string/array lengths. Tests also check it with jsonschema when available.
    """
    problems=[]
    def err(message):problems.append({'severity':'error','code':'schema','path':path,'message':message})
    typ=spec.get('type')
    valid={'object':lambda:type(value) is dict,'array':lambda:type(value) is list,
           'string':lambda:type(value) is str,'number':lambda:type(value) in (int,float) and math.isfinite(value),
           'integer':lambda:type(value) is int,'boolean':lambda:type(value) is bool}
    if typ and not valid[typ]():err(f'Expected {typ}.');return problems
    if 'const' in spec and value!=spec['const']:err(f'Expected {spec["const"]!r}.')
    if 'enum' in spec and value not in spec['enum']:err(f'Expected one of {spec["enum"]}.')
    if typ=='object':
        for key in spec.get('required',[]):
            if key not in value:err(f'Missing field {key!r}.')
        props=spec.get('properties',{})
        if spec.get('additionalProperties') is False:
            for key in value:
                if key not in props:err(f'Unexpected field {key!r}.')
        for key,sub in props.items():
            if key in value:problems+=structural_errors(value[key],sub,path+'.'+key)
    elif typ=='array':
        # Stop at an oversized array: walking every item would amplify one bad request into a huge report.
        if len(value)>spec.get('maxItems',100000):err('Too many array items.');return problems
        if len(value)<spec.get('minItems',0):err('Too few array items.')
        for i,item in enumerate(value):problems+=structural_errors(item,spec.get('items',{}),f'{path}[{i}]')
    elif typ=='string':
        if len(value)>spec.get('maxLength',100000):err('String is too long.')
        # fullmatch: re.search with '$' would accept a trailing newline in identifiers.
        if 'pattern' in spec and not re.fullmatch(spec['pattern'].removeprefix('^').removesuffix('$'),value):err('Invalid identifier format.')
        if ILLEGAL_TEXT.search(value):problems.append({'severity':'error','code':'illegal_character','path':path,'message':'Control, invisible, bidirectional-override or non-XML characters are not permitted.'})
    elif typ in ('number','integer'):
        if value<spec.get('minimum',-math.inf) or value>spec.get('maximum',math.inf):err('Number is outside allowed bounds.')
    return problems

DEFAULT_SIZE={'component':(200,146),'symbol':(144,112),'packet':(92,58),'memory':(400,92),'text':(300,48),'marker':(36,36)}

def box(n: dict) -> tuple[float,float,float,float]:
    dw,dh=DEFAULT_SIZE[n['kind']]
    return n['x'],n['y'],n.get('w',dw),n.get('h',dh)

def width_text(txt: str, size: float) -> float:
    # Conservative font-width estimate for Arial / Helvetica. Browser preview remains required.
    # math.fsum, not sum: Python 3.12 changed float sum() to compensated summation, so
    # sum() gives different last-bit results on 3.10/3.11 and renders are not byte-stable.
    return math.fsum(.29 if ch in 'ilI.,:;!|\' ' else .88 if ch in 'MW@%#' else .57 if ch.isupper() else .53 for ch in txt)*size

def wrap(txt: str, width: float, size: float) -> list[str]:
    lines=[]
    for para in str(txt).split('\n'):
        current=''
        for word in para.split():
            if width_text(word,size)>width:
                if current:lines.append(current);current=''
                part=''
                for char in word:
                    if width_text(part+char,size)>width and part:lines.append(part);part=''
                    part+=char
                current=part
            elif not current or width_text(current+' '+word,size)<=width:current=(current+' '+word).strip()
            else:lines.append(current);current=word
        lines.append(current)
    return lines or ['']

def overlaps(a,b,pad:float=0) -> bool:
    ax,ay,aw,ah=a;bx,by,bw,bh=b
    return min(ax+aw,bx+bw)-max(ax,bx)>pad and min(ay+ah,by+bh)-max(ay,by)>pad

def anchor(n:dict,port:str) -> tuple[float,float]:
    x,y,w,h=box(n)
    return {'n':(x+w/2,y),'s':(x+w/2,y+h),'e':(x+w,y+h/2),'w':(x,y+h/2)}[port]

def edge_points(edge:dict,nodes:dict) -> list[tuple[float,float]]:
    a,b=nodes[edge['source']],nodes[edge['target']]
    ax,ay,aw,ah=box(a);bx,by,bw,bh=box(b)
    dx=bx+bw/2-ax-aw/2;dy=by+bh/2-ay-ah/2
    horizontal=abs(dx)>=abs(dy)
    sp=edge.get('source_port',('e' if dx>=0 else 'w') if horizontal else ('s' if dy>=0 else 'n'))
    tp=edge.get('target_port',('w' if dx>=0 else 'e') if horizontal else ('n' if dy>=0 else 's'))
    start=anchor(a,sp);end=anchor(b,tp)
    if edge.get('points') is not None:pts=[start]+[(p['x'],p['y']) for p in edge['points']]+[end]
    elif edge.get('route')=='straight':pts=[start,end]
    elif sp in ('e','w') and tp in ('e','w'):
        mx=(start[0]+end[0])/2;pts=[start,(mx,start[1]),(mx,end[1]),end]
    elif sp in ('n','s') and tp in ('n','s'):
        my=(start[1]+end[1])/2;pts=[start,(start[0],my),(end[0],my),end]
    elif sp in ('e','w'):pts=[start,(end[0],start[1]),end]
    else:pts=[start,(start[0],end[1]),end]
    out=[]
    for pt in pts:
        if not out or pt!=out[-1]:out.append(pt)
    # Merge collinear segments so a label uses the full straight run, not half of it.
    compact=[]
    for pt in out:
        while len(compact)>=2:
            a,b=compact[-2],compact[-1]
            cross=(b[0]-a[0])*(pt[1]-b[1])-(b[1]-a[1])*(pt[0]-b[0])
            dot=(b[0]-a[0])*(pt[0]-b[0])+(b[1]-a[1])*(pt[1]-b[1])
            if abs(cross)<1e-8 and dot>=0:compact.pop()
            else:break
        compact.append(pt)
    return compact

def edge_label(edge:dict,nodes:dict) -> tuple[float,float,float,float]:
    pts=edge_points(edge,nodes)
    seg=max(zip(pts,pts[1:]),key=lambda pair:math.dist(*pair),default=(pts[0],pts[0]))
    x=edge.get('label_x',(seg[0][0]+seg[1][0])/2)
    y=edge.get('label_y',(seg[0][1]+seg[1][1])/2-13)
    w=width_text(edge.get('label',''),13)+16
    return x-w/2,y-14,w,23

def segment_crosses_box(a,b,rect) -> bool:
    # Liang-Barsky clipping against an inset box; endpoint tangencies do not count.
    x,y,w,h=rect;x+=4;y+=4;w-=8;h-=8
    if w<=0 or h<=0:return False
    dx=b[0]-a[0];dy=b[1]-a[1];lo,hi=0.0,1.0
    for pp,qq in ((-dx,a[0]-x),(dx,x+w-a[0]),(-dy,a[1]-y),(dy,y+h-a[1])):
        if abs(pp)<1e-9:
            if qq<0:return False
        else:
            t=qq/pp
            if pp<0:lo=max(lo,t)
            else:hi=min(hi,t)
    return lo<=hi and hi>0 and lo<1

def validate(scene:dict) -> dict:
    issues=structural_errors(scene,schema())
    if issues:return _report(issues)
    def add(code,message,path='',severity='error'):
        issues.append({'severity':severity,'code':code,'path':path,'message':message})
    seen=set();nodes={};groups={}
    for g in scene.get('groups',[]):
        if g['id'] in seen:add('duplicate_id',g['id'])
        seen.add(g['id']);groups[g['id']]=g
        if g['x']+g['w']>scene['width'] or g['y']+g['h']>scene['height']:add('group_bounds',g['id'])
        if width_text(g['title'],20)>g['w']-38:add('group_title_width',f'{g["id"]}: shorten the group title or widen the group.',severity='warning')
    for i,n in enumerate(scene['nodes']):
        ident=n['id'];path=f'$.nodes[{i}]'
        if ident in seen:add('duplicate_id',ident,path)
        seen.add(ident);nodes[ident]=n
        x,y,w,h=box(n)
        if x+w>scene['width'] or y+h>scene['height']:add('node_bounds',f'{ident}: outside canvas.',path)
        if n['kind'] in ('component','symbol') and n.get('asset') not in index():add('asset_id',f'{ident}: unknown or missing asset.',path)
        if n['kind']=='memory' and not n.get('cells'):add('memory_cells',f'{ident}: memory nodes need cells.',path)
        if n.get('group'):
            if n['group'] not in groups:add('group_id',f'{ident}: unknown group.',path)
            else:
                g=groups[n['group']]
                if x<g['x'] or y<g['y'] or x+w>g['x']+g['w'] or y+h>g['y']+g['h']:add('group_containment',f'{ident}: extends beyond its group.',path)
        if n['kind']=='component':
            labels=wrap(n.get('label',''),w-20,17);details=wrap(n.get('detail',''),w-20,12)
            needed=92+max(0,len(labels)-1)*20+(16*len(details) if n.get('detail') else 0)+14
            if needed>h:add('text_height',f'{ident}: needs approximately {needed}px height, has {h}px.',path,'warning')
        if n['kind']=='symbol' and n.get('caption') and len(wrap(n['caption'],w,13))>2:
            add('text_height',f'{ident}: caption wraps beyond two lines; shorten it or widen the node.',path,'warning')
        if n['kind']=='text' and n.get('label'):
            fs=n.get('font_size',16)
            if len(wrap(n.get('label',''),w,fs))*fs*1.32>h+1:add('text_height',f'{ident}: text may not fit in its box.',path,'warning')
    for i,a in enumerate(scene['nodes']):
        for b in scene['nodes'][i+1:]:
            if overlaps(box(a),box(b),2):add('node_overlap',f'{a["id"]} overlaps {b["id"]}.',severity='warning')
    for e in scene['edges']:
        if e['id'] in seen:add('duplicate_id',e['id'])
        seen.add(e['id'])
        if e['source'] not in nodes or e['target'] not in nodes:add('edge_endpoint',f'{e["id"]}: unknown source or target.');continue
        if e['source']==e['target'] and not e.get('points'):add('self_edge',f'{e["id"]}: self-links need explicit waypoints.');continue
        pts=edge_points(e,nodes)
        for pt in pts:
            if pt[0]<0 or pt[0]>scene['width'] or pt[1]<0 or pt[1]>scene['height']:add('edge_bounds',f'{e["id"]}: waypoint outside canvas.')
        for n in scene['nodes']:
            if n['id'] not in (e['source'],e['target']) and any(segment_crosses_box(a,b,box(n)) for a,b in zip(pts,pts[1:])):
                add('edge_node_crossing',f'{e["id"]} crosses {n["id"]}; adjust waypoints.',severity='warning')
        if e.get('label'):
            lb=edge_label(e,nodes)
            if lb[0]<0 or lb[0]+lb[2]>scene['width'] or lb[1]<0 or lb[1]+lb[3]>scene['height']:add('edge_label_bounds',f'{e["id"]}: label extends beyond canvas.',severity='warning')
            for n in scene['nodes']:
                if overlaps(lb,box(n),2):add('edge_label_overlap',f'{e["id"]}: label overlaps {n["id"]}.',severity='warning')
    if len(scene['nodes'])>28:
        panel_counts=[];covered=set()
        for g in scene.get('groups',[]):
            inside=[n for n in scene['nodes'] if box(n)[0]>=g['x'] and box(n)[1]>=g['y'] and box(n)[0]+box(n)[2]<=g['x']+g['w'] and box(n)[1]+box(n)[3]<=g['y']+g['h']]
            panel_counts.append(len(inside));covered.update(n['id'] for n in inside)
        panel_counts.append(len(scene['nodes'])-len(covered))
        if max(panel_counts)>28:add('density','A panel has more than 28 elements. Consider additional panels or a larger canvas.',severity='warning')
    return _report(issues)

def _report(issues:list[dict]) -> dict:
    # Validity is decided on the full list; only the returned list is capped to bound response size.
    report={'valid':not any(i['severity']=='error' for i in issues),'issues':issues[:MAX_ISSUES]}
    if len(issues)>MAX_ISSUES:report['truncated']=len(issues)-MAX_ISSUES
    return report

def auto_layout(title: str,nodes: list[dict],edges: list[dict],direction: str='LR') -> dict:
    """Simple deterministic DAG layering. Cycles use a grid, not a guessed dependency order."""
    if not 1<=len(nodes)<=80 or len(edges)>200:raise ValueError('Use 1–80 nodes and at most 200 edges.')
    allowed={'id','asset','label','detail','palette'}
    if any(set(n)-allowed for n in nodes):raise ValueError('Layout nodes accept id, asset, label, detail, palette only.')
    ids=[n.get('id') for n in nodes]
    if len(set(ids))!=len(ids) or any(not isinstance(i,str) for i in ids):raise ValueError('Node IDs must be unique strings.')
    if direction not in ('LR','TB'):raise ValueError('direction must be LR or TB.')
    indeg={i:0 for i in ids};adj={i:[] for i in ids};levels={i:0 for i in ids}
    for edge in edges:
        if edge.get('source') not in indeg or edge.get('target') not in indeg:raise ValueError('Unknown edge endpoint.')
        indeg[edge['target']]+=1;adj[edge['source']].append(edge['target'])
    todo=sorted(i for i in ids if indeg[i]==0);done=[]
    while todo:
        i=todo.pop(0);done.append(i)
        for j in adj[i]:
            levels[j]=max(levels[j],levels[i]+1);indeg[j]-=1
            if indeg[j]==0:todo.append(j);todo.sort()
    cyclic=len(done)!=len(ids)
    if cyclic:levels={ident:i//4 for i,ident in enumerate(ids)}
    lanes={}
    for ident in ids:lanes.setdefault(levels[ident],[]).append(ident)
    positions={}
    for level,items in sorted(lanes.items()):
        for row,ident in enumerate(items):
            positions[ident]=(54+level*300,154+row*208) if direction=='LR' else (54+row*264,154+level*230)
    result=[]
    for n in nodes:
        x,y=positions[n['id']];result.append(dict(n,kind='component',x=x,y=y,w=200,h=146))
    scene={'version':'1.0','title':title,'subtitle':'Adjust ports, spacing, and labels after the initial layout.','width':max(480,int(max(n['x']+n['w'] for n in result)+54)),'height':int(max(n['y']+n['h'] for n in result)+90),'nodes':result,'edges':edges}
    if cyclic:scene['description']='A directed cycle was found. Initial positions use a grid; this is not a topological ordering.'
    report=validate(scene)
    if not report['valid']:raise ValueError(json.dumps(report))
    return scene
