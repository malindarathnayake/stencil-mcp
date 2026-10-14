#!/usr/bin/env python3
"""Build Stencil's SVG brand pack; optionally export PNGs with CairoSVG.

Uses saved vector outlines, not bundled font files. SVG generation is stdlib-only.
Existing diagram assets and their catalog IDs are not modified.
"""
from __future__ import annotations
from pathlib import Path
from html import escape
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
BRAND=ROOT/'branding'
C=json.loads((BRAND/'tokens.json').read_text(encoding='utf-8'))['colors']
O=json.loads((BRAND/'source/wordmark-outline.json').read_text(encoding='utf-8'))
try:
    import cairosvg
except ImportError:
    cairosvg=None

TOP='M 128 26 Q 133 26 138 29 L 221 73 Q 234 80 221 88 L 138 132 Q 128 137 118 132 L 35 88 Q 22 80 35 73 L 118 29 Q 123 26 128 26 Z'
MID='M 46 107 L 118 145 Q 128 150 138 145 L 210 107 L 224 114 Q 236 121 224 128 L 138 173 Q 128 178 118 173 L 32 128 Q 20 121 32 114 Z'
BOTTOM='M 46 153 L 118 191 Q 128 196 138 191 L 210 153 L 224 160 Q 236 167 224 174 L 138 219 Q 128 224 118 219 L 32 174 Q 20 167 32 160 Z'

def mark(x=0,y=0,size=256,variant='primary'):
    palette={'primary':(C['navy'],C['sky'],C['sky']),
             'mint':(C['teal'],C['blue'],C['blue']),
             'dark':(C['blue'],C['sky'],C['sky']),
             'navy':(C['navy'],)*3,'white':(C['white'],)*3}[variant]
    # Paint each layer independently; the open gaps are truly transparent.
    parts=[f'<g transform="translate({x} {y}) scale({size/256:.8f})">']
    for name,d,color in zip(('lower-layer','middle-layer','top-layer'),(BOTTOM,MID,TOP),reversed(palette)):
        parts.append(f'<path data-part="{name}" d="{d}" fill="{color}"/>')
    return ''.join(parts)+'</g>'

def word(x,y,em,color):
    scale=em/O['units_per_em']
    return f'<g aria-label="Stencil" fill="{color}" transform="translate({x} {y}) scale({scale:.8f} {-scale:.8f})">'+''.join(
        f'<path transform="translate({g["x"]} 0)" d="{g["path"]}"/>' for g in O['glyphs'])+'</g>'

def text(x,y,t,size=22,color=None,weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color or C["navy"]}" text-anchor="{anchor}">{escape(t)}</text>'

def rect(x,y,w,h,fill,rx=0,stroke=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>'

def svg(w,h,title,body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="Inter, Arial, Helvetica, sans-serif" role="img" aria-label="{escape(title,quote=True)}">'
            f'<title>{escape(title)}</title>{body}</svg>\n')

manifest=[]
def save(rel,w,h,title,body,usage,png_width=None):
    p=BRAND/rel;p.parent.mkdir(parents=True,exist_ok=True)
    source=svg(w,h,title,body);p.write_bytes(source.encode('utf-8'))
    entry={'id':'brand/'+p.stem,'svg':rel,'viewBox':[0,0,w,h],'usage':usage,'sha256':hashlib.sha256(source.encode()).hexdigest()}
    if cairosvg and png_width:
        target=p.with_suffix('.png')
        cairosvg.svg2png(bytestring=source.encode(),write_to=str(target),output_width=png_width)
        entry['png']=str(target.relative_to(BRAND))
    manifest.append(entry)
    return source

def main():
    for variant in ('primary','navy','white'):
        save('logos/stencil-mark-'+variant+'.svg',256,256,'Stencil layered mark',mark(variant=variant),
             'Primary standalone mark.' if variant=='primary' else 'Single-color mark for '+('dark backgrounds.' if variant=='white' else 'light backgrounds.'),512)
    for theme in ('light','dark'):
        ink=C['navy'] if theme=='light' else C['white']
        body=mark(12,24,208,'primary' if theme=='light' else 'dark')+word(245,179,126,ink)
        save('logos/stencil-lockup-'+theme+'.svg',720,256,'Stencil logo',body,'Horizontal logo; transparent background, outlined wordmark.',1440)
    save('logos/stencil-wordmark.svg',620,180,'Stencil wordmark',word(18,142,170,C['navy']),'Wordmark alone; transparent, outlined SVG.',1240)
    save('logos/stencil-lockup-editable-text.svg',720,256,'Stencil editable logo',
         mark(12,24,208)+text(245,180,'Stencil',126,C['navy'],700),
         'Editable live text variant. Appearance depends on the local font; use outlined logos for exact reproduction.')
    for theme in ('mint','dark','light'):
        bg={'mint':C['mint'],'dark':C['navy'],'light':C['white']}[theme]
        variant={'mint':'mint','dark':'dark','light':'primary'}[theme]
        source=save('avatars/stencil-avatar-'+theme+'.svg',512,512,'Stencil '+theme+' avatar',
          rect(0,0,512,512,bg,112)+mark(88,88,336,variant),'GitHub/avatar icon; safe central symbol for circular crops.',1024)
        if cairosvg:
            for size in (512,128,64,32):
                out=BRAND/'avatars'/f'stencil-avatar-{theme}-{size}.png'
                cairosvg.svg2png(bytestring=source.encode(),write_to=str(out),output_width=size,output_height=size)
    save('avatars/stencil-favicon.svg',256,256,'Stencil favicon',rect(0,0,256,256,C['mint'],56)+mark(20,20,216,'mint'),
         'Small-site icon. Prefer the standalone three-layer symbol; no wordmark.',64)

    # Reuse shipped vector icons for the repository banner, not concept-sheet crops.
    import sys
    sys.path.insert(0,str(ROOT))
    from diagramkit.renderer import symbol
    body=rect(0,0,1600,480,C['white'],24)+rect(48,44,64,5,C['blue'],2)
    body+=text(48,84,'SVG DIAGRAM LIBRARY + MCP',17,C['slate'],600)
    body+=mark(36,119,220)+word(259,277,128,C['navy'])
    body+=text(54,365,'Reusable assets for technical diagrams.',28,C['navy'],500)
    body+=text(54,411,'Infrastructure  /  Networking  /  Security  /  Software',18,C['slate'])
    body+=rect(947,64,607,352,C['panel'],26)+rect(981,93,128,30,C['mint'],15)
    body+=text(1045,114,'EDITABLE SVG',13,C['teal'],700,'middle')
    body+='<path d="M 1130 245 H 1180 M 1314 245 H 1372" fill="none" stroke="'+C['blue']+'" stroke-width="4"/>'
    body+='<path d="M 1173 238 L 1180 245 L 1173 252 M 1365 238 L 1372 245 L 1365 252" fill="none" stroke="'+C['blue']+'" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    for aid,x,label in [('compute/rack-server',982,'Compute'),('network/switch-l3',1170,'Network'),('security/firewall',1356,'Security')]:
        body+=symbol(aid,x,182,160,124)+text(x+80,341,label,18,C['navy'],600,'middle')
    save('banners/stencil-readme-banner.svg',1600,480,'Stencil repository banner',body,'README header. Prefer PNG for a uniform display across renderers.',1600)

    body=rect(0,0,1280,640,C['navy'])+rect(60,58,90,7,C['mint'],3)
    body+=mark(56,137,260,'dark')+word(343,328,172,C['white'])
    body+=text(72,464,'Reusable SVG assets. Editable technical diagrams.',34,C['white'],500)
    body+=text(74,537,'INFRASTRUCTURE  /  NETWORKS  /  SECURITY  /  SOFTWARE',19,C['sky'],600)
    save('banners/stencil-social-preview.svg',1280,640,'Stencil social preview',body,'Repository social/open-graph artwork.',1280)

    # One-page preview of the actual export files and finalized tokens.
    body=rect(0,0,1280,940,C['white'])+text(48,66,'Stencil',44,C['navy'],700)+text(50,104,'Logo, avatars and repository colors',21,C['slate'])
    body+=rect(40,137,760,274,C['panel'],20)+mark(68,160,200)+word(294,309,112,C['navy'])
    body+=text(72,382,'Primary logo  /  outlined SVG',16,C['slate'])
    for i,theme in enumerate(('mint','dark','light')):
        x=847+i*126; bg={'mint':C['mint'],'dark':C['navy'],'light':C['ice']}[theme]
        variant={'mint':'mint','dark':'dark','light':'primary'}[theme]
        body+=rect(x,172,112,112,bg,24)+mark(x+16,188,80,variant)+text(x+56,323,theme.title(),16,C['slate'],400,'middle')
    body+=text(48,476,'Brand colors',26,C['navy'],700)
    swatches=['navy','blue','sky','mint','teal','slate','panel']
    for i,k in enumerate(swatches):
        x=48+i*171
        body+=rect(x,506,146,90,C[k],14)+text(x,626,k.title(),18,C['navy'],600)+text(x,651,C[k],15,C['slate'])
    body+=rect(40,697,1200,190,C['panel'],20)+text(65,733,'Diagram components',22,C['navy'],700)
    for i,(aid,label) in enumerate([('compute/rack-server','Server'),('network/switch-l3','Switch'),('hardware/rdma-nic','RDMA NIC'),('security/firewall','Firewall'),('software/rest-api','API'),('protocol/packet','Packet')]):
        x=65+i*197;body+=symbol(aid,x+30,754,114,88)+text(x+86,868,label,16,C['slate'],400,'middle')
    body+=text(48,920,'Option C selected. Vector redraws and export files for Stencil; concept boards retained in references/.',14,C['slate'])
    save('stencil-brand-preview.svg',1280,940,'Stencil branding preview',body,'Overview of the production brand pack.',1280)
    (BRAND/'manifest.json').write_bytes((json.dumps({'name':'Stencil','assets':manifest},indent=2)+'\n').encode('utf-8'))
    print(f'Built {len(manifest)} brand SVGs.'+(' PNG exports generated.' if cairosvg else ' Install CairoSVG for PNG exports.'))
if __name__=='__main__':main()
