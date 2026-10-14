"""Deterministic, self-contained SVG renderer. All user text is XML-escaped."""
from __future__ import annotations
from html import escape
from functools import lru_cache
import json, hashlib, xml.etree.ElementTree as ET
from .library import ROOT, asset_info
from .scene import box, wrap, width_text, edge_points, edge_label, validate
ET.register_namespace('', 'http://www.w3.org/2000/svg')
BASE=json.loads((ROOT/'palettes.json').read_text(encoding='utf-8'))


def palette(name='blue',theme='light'):
    a,s=BASE['colors'][name]['accent'],BASE['colors'][name]['soft']
    if theme=='monochrome':return '#41546E','#EDF2F7'
    if theme=='dark':
        aa={'blue':'#77B9FA','teal':'#67D1C3','purple':'#BBA2FA','orange':'#F2B77B','red':'#F38E99','slate':'#B0C4DE','green':'#88D2A3','yellow':'#E5CF80'}
        ss={'blue':'#1C3551','teal':'#153D3E','purple':'#302747','orange':'#403121','red':'#432833','slate':'#243349','green':'#233B30','yellow':'#3D3929'}
        return aa[name],ss[name]
    return a,s

def tokens(theme):
    return {'ink':'#DFEBFC','muted':'#ABC0D9','border':'#3A506B','bg':'#0F1D30','card':'#162840'} if theme=='dark' else {'ink':BASE['ink'],'muted':BASE['muted'],'border':BASE['border'],'bg':'#FFFFFF','card':'#FFFFFF'}

def rect(x,y,w,h,fill,stroke='none',rx=8,sw=1.5,dash=''):
    extra=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"{extra}/>'

def text(x,y,content,size=16,fill='#132B50',weight=400,anchor='start'):
    return f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(content))}</text>'

def multiline(x,y,content,max_width,size=16,fill='#132B50',weight=400,anchor='start',leading=1.32):
    return ''.join(text(x,y+i*size*leading,line,size,fill,weight,anchor) for i,line in enumerate(wrap(content,max_width,size)))

@lru_cache(maxsize=400)
def asset_art(asset_id):
    meta=asset_info(asset_id,True);raw=meta['svg']
    if len(raw.encode())>100_000:raise ValueError('Asset exceeds size limit.')
    if hashlib.sha256(raw.encode()).hexdigest()!=meta['sha256']:raise ValueError(f'Asset checksum mismatch: {asset_id}. Rebuild the catalog after approved edits.')
    root=ET.fromstring(raw)
    allowed={'svg','g','title','desc','path','rect','circle','ellipse','line','polygon','polyline','text'}
    for el in root.iter():
        if el.tag.rsplit('}',1)[-1] not in allowed:raise ValueError('Unsupported SVG element in catalog asset.')
        for k,v in el.attrib.items():
            k=k.rsplit('}',1)[-1].lower()  # compare local names, so xlink:href is caught too
            if k.startswith('on') or k in ('href','style') or 'url(' in v.lower():raise ValueError('Active or externally referenced SVG content is prohibited.')
    g=next((ch for ch in root if ch.tag.endswith('}g')),None)
    if g is None:raise ValueError('Asset has no artwork group.')
    # Strip IDs from internal artwork; instance groups receive unique IDs in the scene.
    for el in g.iter():
        el.attrib.pop('id',None)
    return ET.tostring(g,encoding='unicode').replace(' xmlns="http://www.w3.org/2000/svg"','')

def symbol(asset_id,x,y,w,h,theme='light'):
    raw=asset_art(asset_id)
    if theme!='light':
        tk=tokens(theme);replacements={BASE['ink']:tk['ink'],BASE['muted']:tk['muted'],BASE['border']:tk['border'],'#FFFFFF':tk['card']}
        for name,colors in BASE['colors'].items():
            a,s=palette(name,theme);replacements[colors['accent']]=a;replacements[colors['soft']]=s
        # One-pass replacement avoids cascaded substitutions (important for monochrome).
        import re
        raw=re.sub(r'#[0-9A-Fa-f]{6}',lambda m:replacements.get(m.group(),m.group()),raw)
    scale=min(w/144,h/112);dx=x+(w-144*scale)/2;dy=y+(h-112*scale)/2
    return f'<g transform="translate({dx:g} {dy:g}) scale({scale:g})">{raw}</g>'

def draw_node(n,theme):
    tk=tokens(theme);a,s=palette(n.get('palette','blue'),theme);x,y,w,h=box(n);kind=n['kind']
    out=f'<g id="node-{n["id"]}" data-kind="{kind}"><title>{escape(n.get("label",n["id"]))}</title>'
    if kind=='component':
        out+=rect(x,y,w,h,tk['card'],tk['border'],10)+rect(x,y,4,h,a,rx=2)
        out+=symbol(n['asset'],x+(w-86)/2,y+10,86,67,theme)
        labels=wrap(n.get('label',asset_info(n['asset'])['name']),w-20,17)
        for i,lab in enumerate(labels):out+=text(x+w/2,y+94+i*20,lab,17,tk['ink'],700,'middle')
        if n.get('detail'):out+=multiline(x+w/2,y+112+(len(labels)-1)*20,n['detail'],w-20,12,tk['muted'],400,'middle')
        if n.get('state') in ('down','blocked','pending'):
            sa='status/'+{'down':'down','blocked':'blocked','pending':'pending'}[n['state']]
            out+=symbol(sa,x+w-29,y+6,23,23,theme)
    elif kind=='symbol':
        if n.get('caption'):
            # The caption sits inside the node box, so bounds and overlap checks still hold.
            lines=wrap(n['caption'],w,13)[:2];cap_h=len(lines)*17+4
            out+=symbol(n['asset'],x,y,w,h-cap_h,theme)
            for i,line in enumerate(lines):out+=text(x+w/2,y+h-cap_h+15+i*17,line,13,tk['ink'],600,'middle')
        else:out+=symbol(n['asset'],x,y,w,h,theme)
    elif kind=='packet':
        state=n.get('state','normal');failed=state in ('dropped','missing');ac,so=palette('red',theme) if failed else (a,s)
        out+=rect(x,y,w,h,tk['card'] if failed else so,ac,7,2,'5 4' if failed else '')
        out+=text(x+w/2,y+(h/2+7 if not n.get('detail') else 25),n.get('label',''),22,tk['ink'],700,'middle')
        if n.get('detail'):out+=text(x+w/2,y+h-10,n['detail'],11,tk['muted'],400,'middle')
        if state=='dropped':out+=f'<path d="M{x+9:g} {y+9:g} L{x+w-9:g} {y+h-9:g} M{x+w-9:g} {y+9:g} L{x+9:g} {y+h-9:g}" stroke="{ac}" stroke-width="3"/>'
    elif kind=='memory':
        label_height=28 if n.get('label') else 0
        if n.get('label'):out+=text(x,y+18,n['label'],14,tk['ink'],600)
        cells=n['cells'];gap=5;cw=(w-(len(cells)-1)*gap)/len(cells);ch=h-label_height
        for i,cell in enumerate(cells):
            ca,cs=palette(cell.get('palette','blue'),theme);missing=cell.get('state') in ('missing','dropped');xx=x+i*(cw+gap)
            if missing:ca,_=palette('red',theme);cs=tk['card']
            out+=rect(xx,y+label_height,cw,ch,cs,ca,5,1.6,'5 4' if missing else '')
            out+=text(xx+cw/2,y+label_height+ch/2+7,cell['value'],20,tk['ink'],700,'middle')
    elif kind=='text':
        fs=n.get('font_size',16);align=n.get('align','left');anchor={'left':'start','center':'middle','right':'end'}[align]
        xx=x if align=='left' else x+w/2 if align=='center' else x+w
        out+=multiline(xx,y+fs,n.get('label',''),w,fs,tk['ink'],n.get('weight',400),anchor)
    elif kind=='marker':
        state=n.get('state','dropped')
        sa='status/down' if state in ('dropped','down','missing') else 'status/blocked' if state=='blocked' else 'status/pending' if state=='pending' else 'status/healthy'
        out+=symbol(sa,x,y,w,h,theme)
    return out+'</g>'

def render(scene:dict,strict:bool=True) -> str:
    report=validate(scene)
    if strict and not report['valid']:raise ValueError(json.dumps(report,ensure_ascii=False))
    if not report['valid']:raise ValueError('Cannot render a structurally invalid scene.')
    theme=scene.get('theme','light');tk=tokens(theme);W,H=scene['width'],scene['height']
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="diagram-title" aria-describedby="diagram-description" font-family="Arial, Helvetica, sans-serif">',f'<title id="diagram-title">{escape(scene["title"])}</title>',f'<desc id="diagram-description">{escape(scene.get("description",scene.get("subtitle",scene["title"])))}</desc>',rect(0,0,W,H,tk['bg'],rx=0),'<defs>']
    for name in BASE['colors']:
        ac,_=palette(name,theme)
        out.append(f'<marker id="arrow-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M1 1 L9 5 L1 9 Z" fill="{ac}"/></marker>')
    out.append('</defs>')
    title_size=34 if W>=1000 else 27
    out.append(multiline(36,52,scene['title'],W-72,title_size,tk['ink'],700))
    if scene.get('subtitle'):out.append(multiline(36,85,scene['subtitle'],W-72,16,tk['muted']))
    for g in scene.get('groups',[]):
        ac,soft=palette(g.get('palette','blue'),theme);dash='7 5' if g.get('style')=='boundary' else ''
        out.append(f'<g id="group-{g["id"]}">')
        out.append(rect(g['x'],g['y'],g['w'],g['h'],soft,ac if dash else tk['border'],12,1.4,dash))
        out.append(text(g['x']+19,g['y']+31,g['title'],20,tk['ink'],700))
        if g.get('caption'):out.append(multiline(g['x']+19,g['y']+54,g['caption'],g['w']-38,13,tk['muted']))
        out.append('</g>')
    nodes={n['id']:n for n in scene['nodes']}
    for e in scene['edges']:
        pts=edge_points(e,nodes);name=e.get('palette','blue');ac,_=palette(name,theme)
        kind=e.get('kind','data');arrow=e.get('arrow','none' if kind=='physical' else 'forward')
        dash={'control':'7 5','feedback':'7 5','dependency':'3 5','tunnel':'10 4','replication':'9 3'}.get(kind,'')
        d='M'+' L'.join(f'{x:g} {y:g}' for x,y in pts)
        attrs=f' stroke-dasharray="{dash}"' if dash else ''
        if arrow in ('forward','both'):attrs+=f' marker-end="url(#arrow-{name})"'
        if arrow=='both':attrs+=f' marker-start="url(#arrow-{name})"'
        out.append(f'<path id="edge-{e["id"]}" data-kind="{kind}" d="{d}" fill="none" stroke="{ac}" stroke-width="{e.get("width",2.4):g}" stroke-linejoin="round" stroke-linecap="round"{attrs}/>')
    for n in scene['nodes']:out.append(draw_node(n,theme))
    for e in scene['edges']:
        if e.get('label'):
            x,y,w,h=edge_label(e,nodes)
            out.append(f'<g id="label-{e["id"]}">'+rect(x,y,w,h,tk['card'],tk['border'],5,0.7)+text(x+w/2,y+16,e['label'],13,tk['ink'],500,'middle')+'</g>')
    if scene.get('legend'):
        xx=36;yy=H-48 if scene.get('footer') else H-28
        for item in scene['legend']:
            ac,_=palette(item['palette'],theme);dash=' stroke-dasharray="6 4"' if item.get('dashed') else ''
            out.append(f'<path d="M{xx:g} {yy-5:g} H{xx+28:g}" fill="none" stroke="{ac}" stroke-width="2.5"{dash}/>'+text(xx+38,yy,item['label'],12,tk['muted']))
            xx+=width_text(item['label'],12)+70
    if scene.get('footer'):out.append(multiline(36,H-17,scene['footer'],W-72,11,tk['muted']))
    out.append('</svg>')
    return '\n'.join(out)+'\n'
