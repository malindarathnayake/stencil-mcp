#!/usr/bin/env python3
"""Generate an offline catalog, vector contact sheets and optional raster previews."""
from pathlib import Path
from html import escape
import sys,json,math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from diagramkit.library import catalog,asset_info,list_templates,get_template
from diagramkit.renderer import symbol,text,rect,wrap,render
try:import cairosvg
except (ImportError,OSError):cairosvg=None  # OSError: package present, native libcairo missing

def sheet(ids,title,subtitle,cols=6,cardw=216,cardh=165):
    margin=30;gap=15;top=147;rows=math.ceil(len(ids)/cols);W=margin*2+cols*cardw+(cols-1)*gap;H=top+rows*(cardh+gap)+42
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif" role="img"><title>{escape(title)}</title>',rect(0,0,W,H,'#FFFFFF',rx=0),text(margin,58,title,38,'#132B50',700),text(margin,95,subtitle,16,'#5B708B')]
    for i,aid in enumerate(ids):
        a=asset_info(aid);x=margin+(i%cols)*(cardw+gap);y=top+(i//cols)*(cardh+gap)
        parts.append(rect(x,y,cardw,cardh,'#F8FAFD','#D4E0ED',10))
        parts.append(symbol(aid,x+(cardw-98)/2,y+9,98,76))
        name=wrap(a['name'],cardw-18,14)
        for j,line in enumerate(name):parts.append(text(x+cardw/2,y+107+17*j,line,14,'#132B50',600,'middle'))
        parts.append(text(x+cardw/2,y+cardh-12,a['id'],9.2,'#5B708B',400,'middle'))
    parts.append(text(margin,H-20,'Original generic symbols · editable geometry · system fonts · no vendor logos',12,'#5B708B'))
    parts.append('</svg>');return '\n'.join(parts)

SELECTION={
 'compute':['rack-server','hypervisor','virtual-machine'],
 'hardware':['gpu','rdma-nic','video-accelerator'],
 'network':['router','switch-l3','wireless-ap'],
 'routing':['ecmp','flow-hash','vxlan'],
 'security':['firewall','ids','microsegmentation'],
 'identity':['identity-provider','certificate','secrets-vault'],
 'storage':['nas','object-store','immutable-backup'],
 'cloud':['public-cloud','datacenter','dedicated-circuit'],
 'kubernetes':['cluster','pod','gateway-api'],
 'software':['rest-api','message-queue','background-worker'],
 'data':['relational-db','vector-db','cache'],
 'devops':['git-repository','ci-build','release-approval'],
 'observability':['dashboard','traces','alert'],
 'ai':['ai-agent','mcp-server','kv-cache'],
 'resilience':['replication','circuit-breaker','retry'],
 'protocol':['packet','sack','dropped-packet'],
 'presentation':['boundary','swimlane','decision'],
 'status':['healthy','warning','down'],
 'business':['form','approval','invoice'],
 'fleet':['vehicle','dashcam','event-clip']}

def main():
    preview=ROOT/'previews';preview.mkdir(exist_ok=True)
    all_assets=catalog()['assets'];cats=catalog()['categories'];n_tpl=len(list_templates()['templates'])
    counts=f'{len(all_assets)} editable SVG assets · {len(cats)} categories · {n_tpl} templates · 12 MCP tools'
    for cat in catalog()['categories']:
        ids=[a['id'] for a in all_assets if a['category']==cat['id']]
        raw=sheet(ids,cat['name'],f'{len(ids)} editable SVG assets · {cat["id"]} collection')
        (preview/(cat['id']+'.svg')).write_bytes(raw.encode('utf-8'))
        if cairosvg:cairosvg.svg2png(bytestring=raw.encode(),write_to=str(preview/(cat['id']+'.png')),output_width=1400)
    ids=[cat+'/'+slug for cat,slugs in SELECTION.items() for slug in slugs]
    raw=sheet(ids,'Stencil',counts,cols=10,cardw=186,cardh=157)
    (preview/'catalog-overview.svg').write_bytes(raw.encode('utf-8'))
    if cairosvg:cairosvg.svg2png(bytestring=raw.encode(),write_to=str(preview/'catalog-overview.png'))
    for tmp in list_templates()['templates']:
        raw=render(get_template(tmp['id']));(ROOT/'examples'/(tmp['id']+'.svg')).write_bytes(raw.encode('utf-8'))
        if cairosvg:cairosvg.svg2png(bytestring=raw.encode(),write_to=str(ROOT/'examples'/(tmp['id']+'.png')),output_width=1500)
    # Offline HTML contains the full filter text and uses only local asset paths.
    cards=[]
    for a in all_assets:
        find=' '.join([a['id'],a['name'],a['search_text']]).lower()
        cards.append(f'''<article class="asset" data-category="{escape(a['category'])}" data-search="{escape(find,quote=True)}"><a href="diagramkit/library/{a['file']}" target="_blank" rel="noopener"><img src="diagramkit/library/{a['file']}" alt="{escape(a['name'])}" width="144" height="112" loading="lazy"></a><h3>{escape(a['name'])}</h3><code>{escape(a['id'])}</code><p>{escape(a['category'])} · {escape(a['glyph_family'])}</p><button class="copy" data-id="{escape(a['id'])}">Copy asset ID</button></article>''')
    options=''.join(f'<option value="{c["id"]}">{escape(c["name"])} ({c["count"]})</option>' for c in catalog()['categories'])
    samples=''.join(f'''<article class="example"><a href="examples/{t['id']}.svg" target="_blank" rel="noopener"><img src="examples/{t['id']}.png" alt="{escape(t['title'])}" loading="lazy"></a><h3>{escape(t['title'])}</h3><a href="diagramkit/library/templates/{t['id']}.json">Scene JSON</a> · <a href="examples/{t['id']}.svg">Editable SVG</a></article>''' for t in list_templates()['templates'])
    html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stencil — Asset Library</title><style>
:root{font-family:Arial,Helvetica,sans-serif;color:#132b50;background:#f6f8fc}*{box-sizing:border-box}body{margin:0}header{padding:40px max(24px,5vw);background:white;border-bottom:1px solid #d6e0ee}h1{font-size:40px;margin:0 0 12px}header p{color:#5b708b;line-height:1.6;max-width:900px}nav a{color:#1875d1;margin-right:22px}main{padding:28px max(24px,5vw)}.filters{display:flex;gap:12px;align-items:center;flex-wrap:wrap;position:sticky;top:0;background:#f6f8fc;padding:12px 0;z-index:2}input,select,button{font:inherit;border:1px solid #bfcfe0;border-radius:7px;padding:10px;background:white;color:#132b50}input{width:min(520px,100%)}button{cursor:pointer;font-size:12px;padding:7px 12px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}.asset{background:white;border:1px solid #d6e0ee;border-radius:12px;padding:18px;text-align:center}.asset h3{font-size:15px;min-height:36px;line-height:1.4;margin:8px 0}.asset code{font-size:11px;word-break:break-word}.asset p{font-size:11px;color:#5b708b}.asset img{max-width:100%}.asset[hidden]{display:none}.examples{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:20px}.example{background:white;border:1px solid #d6e0ee;border-radius:12px;padding:18px}.example img{width:100%;height:240px;object-fit:contain}.example h3{font-size:18px}.example a{color:#1875d1;font-size:14px}section{margin-bottom:50px}.note{padding:18px;background:#eaf3fe;border-radius:9px;line-height:1.6}#count{font-size:14px;color:#5b708b}footer{padding:30px;color:#5b708b;font-size:13px}
</style></head><body><header><img src="branding/logos/stencil-lockup-light.svg" width="300" height="107" alt="Stencil"><h1>SVG asset library</h1><p>'''+f'{len(all_assets)} editable SVG assets in {len(cats)} categories. Original generic symbols with stable IDs, searchable roles, normalized connection anchors and {n_tpl} source-controlled diagram templates.'+'''</p><nav><a href="START_HERE.html">Package home</a><a href="branding/index.html">Brand pack</a><a href="#assets">Asset library</a><a href="#templates">Diagram templates</a><a href="previews/catalog-overview.svg">Vector overview</a><a href="README.md">Setup guide</a></nav></header><main><section id="assets"><div class="filters"><input id="query" aria-label="Search assets" placeholder="Search: firewall, ECMP, GPU, Proxmox, packet, MCP…"><select id="category" aria-label="Asset category"><option value="">All categories</option>'''+options+'''</select><span id="count">'''+f'{len(all_assets)} assets'+'''</span></div><div class="grid">'''+''.join(cards)+'''</div></section><section id="templates"><h2>Reusable diagram templates</h2><p class="note">Edit the scene JSON, validate it, then render the SVG. Click a preview for the vector output. Examples are illustrative and do not assert real product compatibility or an operational deployment.</p><div class="examples">'''+samples+'''</div></section></main><footer>Apache-2.0 licensed kit. Vendor terms are search aliases, not official logos. Everything on this page is local; no CDN, tracking, fonts or network requests are required.</footer><script>
const q=document.getElementById('query'),c=document.getElementById('category'),cards=[...document.querySelectorAll('.asset')];
function filter(){const terms=q.value.toLowerCase().trim().split(/\\s+/).filter(Boolean);let n=0;for(const el of cards){const show=(!c.value||el.dataset.category===c.value)&&terms.every(t=>el.dataset.search.includes(t));el.hidden=!show;if(show)n++;}document.getElementById('count').textContent=n+' assets';}q.addEventListener('input',filter);c.addEventListener('change',filter);
for(const b of document.querySelectorAll('.copy'))b.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(b.dataset.id);b.textContent='Copied';setTimeout(()=>b.textContent='Copy asset ID',1000);}catch{const range=document.createRange();range.selectNodeContents(b.parentElement.querySelector('code'));const s=window.getSelection();s.removeAllRanges();s.addRange(range);b.textContent='ID selected — copy manually';}});
</script></body></html>'''
    (ROOT/'gallery.html').write_bytes(html.encode('utf-8'))
    print(f'Generated offline gallery, {len(cats)+1} vector contact sheets and example previews.')
if __name__=='__main__':main()
