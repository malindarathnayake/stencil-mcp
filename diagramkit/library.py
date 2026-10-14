"""Catalog access. Only registered bundled assets are readable."""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
import json, re, difflib

ROOT = Path(__file__).resolve().parent / 'library'

@lru_cache(maxsize=1)
def catalog() -> dict:
    return json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))

@lru_cache(maxsize=1)
def index() -> dict:
    return {a['id']: a for a in catalog()['assets']}

def asset_info(asset_id: str, include_svg: bool = False) -> dict:
    if asset_id not in index():
        near = difflib.get_close_matches(asset_id, index(), n=5)
        raise ValueError(f'Unknown asset {asset_id!r}. Possible IDs: {near}. Use search_assets first.')
    item = dict(index()[asset_id])
    if include_svg:
        item['svg'] = (ROOT / item['file']).read_text(encoding='utf-8')
    return item

def search_assets(query: str = '', category: str = '', limit: int = 12, offset: int = 0) -> dict:
    if category and category not in {c['id'] for c in catalog()['categories']}:
        raise ValueError('Unknown category. Call library_info for category IDs.')
    terms = re.findall(r'[a-z0-9]+', query.lower())
    # Expand only well-defined search aliases; this is lexical search, not an embedding index.
    aliases = {'proxmox':'hypervisor', 'vmware':'hypervisor', 'rancher':'kubernetes',
               'rke2':'kubernetes', 'mrc':'rdma sack ecmp packet', 'roce':'rdma',
               'oracle':'relational database', 'infisical':'secrets vault',
               'nvidia':'gpu', 'alveo':'video accelerator', 'k8s':'kubernetes'}
    extras = ' '.join(aliases.get(term,'') for term in terms).split()
    ranked=[]
    for a in catalog()['assets']:
        if category and a['category'] != category: continue
        head=(a['id']+' '+a['name']).lower()
        body=(head+' '+a['search_text']+' '+a['description']).lower()
        score=sum(10 if term in head else 4 if term in body else 0 for term in terms)
        score+=sum(2 for term in extras if term in body)
        if not terms or score:
            ranked.append((score,a))
    ranked.sort(key=lambda pair:(-pair[0],pair[1]['id']))
    results=[]
    for score,a in ranked[offset:offset+limit]:
        results.append({k:a[k] for k in ('id','name','category','description','role_badge','glyph_family')})
    return {'total':len(ranked),'offset':offset,'next_offset':offset+limit if offset+limit<len(ranked) else None,'assets':results}

@lru_cache(maxsize=1)
def template_index() -> dict:
    return {p.stem:json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'templates').glob('*.json'))}

def list_templates(query: str = '') -> dict:
    terms=query.lower().split()
    items=[]
    for tid,scene in template_index().items():
        text=(tid+' '+scene.get('title','')+' '+scene.get('description','')).lower()
        if not terms or any(term in text for term in terms):
            items.append({'id':tid,'title':scene['title'],'description':scene.get('description',''),'nodes':len(scene['nodes']),'size':[scene['width'],scene['height']]})
    return {'templates':items}

def get_template(template_id: str) -> dict:
    if template_id not in template_index(): raise ValueError('Unknown template ID. Use list_templates.')
    return json.loads(json.dumps(template_index()[template_id]))
