"""MCP-independent service functions; safe, bounded file export."""
from __future__ import annotations
import base64, json, os, re, tempfile, time
from pathlib import Path
from . import __version__
from .library import catalog, ROOT, search_assets, asset_info, list_templates, get_template
from .scene import schema, validate, auto_layout
from .renderer import render
from .guides import stencil_guide


def library_info() -> dict:
    c=catalog()
    return {'name':'Stencil','version':__version__,'asset_count':len(c['assets']),
      'glyph_families':len({a['glyph_family'] for a in c['assets']}),'categories':c['categories'],
      'templates':len(list_templates()['templates']),'themes':['light','dark','monochrome'],
      'scene_version':'1.0','workflow':['stencil_guide (no topic): the confirm-the-brief rule and the guide index','ask the user about open facts before composing','stencil_guide(topic) for brief, your diagram type and style','search_assets','get_asset','get_template or layout_diagram','validate_diagram','render_diagram or export_diagram'],
      'notes':['All symbols are generic, original editable SVGs; no official vendor logos.','Variants may share a glyph family with different role badges.','Anchors refer to node bounds, not numbered physical NIC or switch ports.','Layout checks do not verify the technical truth of an architecture or that it matches the brief.','SVG and MCP work with Python standard library only; PNG preview needs optional CairoSVG.']}


def get_guidelines() -> dict:
    return {'guidelines':(ROOT/'guidelines.md').read_text(encoding='utf-8')}


def render_diagram(scene:dict) -> dict:
    report=validate(scene)
    if not report['valid']:raise ValueError(json.dumps(report,ensure_ascii=False))
    return {'mime_type':'image/svg+xml','svg':render(scene),'validation':report}


PREVIEW_NOT_INSTALLED=('PNG previews need the optional preview extra; SVG rendering, validation and export work without it. '
    'Reinstall with it: uv tool install --force "stencil-mcp[preview]" (or pipx install --force "stencil-mcp[preview]"; '
    'from a clone: python -m pip install -e ".[preview]").')
PREVIEW_NO_LIBCAIRO=('PNG previews need the native Cairo library, which is not installed. SVG rendering, validation and export work without it. '
    'Install Cairo (Debian/Ubuntu: apt install libcairo2; macOS: brew install cairo; Windows: the GTK3 runtime), then restart the MCP server.')

def preview_diagram(scene:dict,width:int=1400) -> dict:
    if not 400<=width<=1800:raise ValueError('Preview width must be 400–1800 pixels.')
    source=render(scene)
    height=max(1,round(width*scene['height']/scene['width']))
    if width*height>6_000_000:raise ValueError('Preview is too tall; reduce width or split the scene.')
    # Optional extra. ImportError: the package is absent. OSError: cairocffi is installed but
    # the native libcairo library is not, which is the usual case on Windows and macOS.
    try:import cairosvg
    except ImportError as e:raise ValueError(PREVIEW_NOT_INSTALLED) from e
    except OSError as e:raise ValueError(PREVIEW_NO_LIBCAIRO) from e
    png=cairosvg.svg2png(bytestring=source.encode('utf-8'),output_width=width,output_height=height)
    return {'width':width,'height':height,'validation':validate(scene),'_image':base64.b64encode(png).decode('ascii')}


WINDOWS_RESERVED=re.compile(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])',re.IGNORECASE)
STALE_LOCK_SECONDS=300


def _acquire_lock(lock:Path,name:str):
    for attempt in (1,2):
        try:os.close(os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY));return
        except FileExistsError:
            try:stale=time.time()-lock.stat().st_mtime>STALE_LOCK_SECONDS
            except FileNotFoundError:stale=True
            # A lock left behind by a crashed writer is cleared once; a live one is reported.
            if attempt==2 or not stale:raise ValueError(f'Another export of {name!r} is in progress; retry shortly.')
            lock.unlink(missing_ok=True)


def export_diagram(scene:dict,name:str,overwrite:bool=False,output_dir:Path|None=None) -> dict:
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',name):
        raise ValueError('name must be a plain stem: 1–80 letters, digits, underscores or hyphens; no path or extension.')
    if WINDOWS_RESERVED.fullmatch(name):raise ValueError(f'{name!r} is a reserved Windows device name; choose another name.')
    report=validate(scene)
    if not report['valid']:raise ValueError(json.dumps(report,ensure_ascii=False))
    root=output_dir or Path(os.environ.get('INFRA_DIAGRAM_OUTPUT_DIR',str(Path.home()/'infra-diagram-exports')))
    root=root.expanduser().resolve();root.mkdir(parents=True,exist_ok=True)
    contents={name+'.svg':render(scene),name+'.scene.json':json.dumps(scene,indent=2,ensure_ascii=False)+'\n'}
    # One writer per stem: the lock stops a concurrent export from interleaving or being rolled back.
    lock=root/f'.{name}.lock';_acquire_lock(lock,name)
    staged={};published=[]
    try:
        for fname in contents:
            dest=root/fname
            if dest.is_symlink():raise ValueError('Refusing to replace an export symlink.')
            if dest.exists() and not overwrite:raise ValueError(f'{fname} exists. Use a new name or explicitly set overwrite=true.')
            if dest.exists() and not dest.is_file():raise ValueError('Export target is not a regular file.')
        # Stage both complete files before publishing, so a failed write never leaves a partial file.
        for fname,content in contents.items():
            fd,tmp=tempfile.mkstemp(prefix='.diagram-',suffix='.tmp',dir=str(root));staged[fname]=tmp
            with os.fdopen(fd,'wb') as fh:fh.write(content.encode('utf-8'))
        try:
            for fname,tmp in staged.items():
                os.replace(tmp,root/fname);published.append(root/fname)
        except Exception:
            # New exports are rolled back; files published here were created by this call under the lock.
            if not overwrite:
                for dest in published:dest.unlink(missing_ok=True)
            raise
    finally:
        for tmp in staged.values():
            if os.path.exists(tmp):os.unlink(tmp)
        lock.unlink(missing_ok=True)
    return {'svg_path':str(root/(name+'.svg')),'scene_path':str(root/(name+'.scene.json')),'validation':report}


def object_schema(properties:dict,required:list|None=None):
    return {'type':'object','properties':properties,'required':required or [],'additionalProperties':False}
S=lambda n=240:{'type':'string','maxLength':n}
B={'type':'boolean'}
I=lambda lo,hi:{'type':'integer','minimum':lo,'maximum':hi}
SCENE_ARG={'type':'object','description':'Scene JSON v1. Start with get_template or get_scene_schema; validate_diagram returns detailed scene checks.'}
LAYOUT_NODE=object_schema({'id':S(64),'asset':S(100),'label':S(120),'detail':S(240),'palette':schema()['properties']['nodes']['items']['properties']['palette']},['id','asset','label'])
TOOLS=[
 ('library_info','Get available categories, counts, styles and the recommended composition workflow.',object_schema({}),True),
 ('search_assets','Search names, roles and aliases; returns metadata, not SVG bodies. Search before inventing IDs.',object_schema({'query':S(),'category':S(40),'limit':I(1,40),'offset':I(0,10000)}),True),
 ('get_asset','Get one registered asset with bounds and normalized cardinal anchors. Request include_svg only when needed.',object_schema({'asset_id':S(100),'include_svg':B},['asset_id']),True),
 ('list_templates','List reusable architecture and packet-story templates.',object_schema({'query':S()}),True),
 ('get_template','Get an editable scene JSON template. Change the scene rather than editing the rendered SVG blindly.',object_schema({'template_id':S(100)},['template_id']),True),
 ('stencil_guide','Start here. No topic: the confirm-the-brief rule and an index of guides. With a topic (e.g. brief, network, business-process, style): how to draw that diagram type, the questions to ask the user first, and common mistakes.',object_schema({'topic':{'type':'string','maxLength':40,'pattern':'^[a-z0-9][a-z0-9-]{0,39}$'}}),True),
 ('get_guidelines','Full composition rules in one document. Prefer stencil_guide for topic-specific guidance.',object_schema({}),True),
 ('get_scene_schema','Get the complete scene JSON Schema, including node, group and edge options.',object_schema({}),True),
 ('layout_diagram','Read stencil_guide and confirm open facts with the user first. Build initial positions for a small graph. DAG layering or grid fallback; not an obstacle-avoiding layout engine. Validate and inspect afterwards.',object_schema({'title':S(160),'nodes':{'type':'array','minItems':1,'maxItems':80,'items':LAYOUT_NODE},'edges':dict(schema()['properties']['edges'],maxItems=200),'direction':{'type':'string','enum':['LR','TB']}},['title','nodes','edges']),True),
 ('validate_diagram','Check structure, asset IDs, endpoints, bounds, overlaps, label estimates and edge-node crossings. Does not certify protocol or architecture correctness.',object_schema({'scene':SCENE_ARG},['scene']),True),
 ('render_diagram','Render scene JSON into self-contained editable SVG text. No filesystem writes. Validation warnings are returned.',object_schema({'scene':SCENE_ARG},['scene']),True),
 ('preview_diagram','Return a PNG image for visual inspection. Optional CairoSVG dependency; no filesystem writes.',object_schema({'scene':SCENE_ARG,'width':I(400,1800)},['scene']),True),
 ('export_diagram','Write SVG and its source scene JSON only into the configured export directory. No arbitrary paths; no overwrite by default.',object_schema({'scene':SCENE_ARG,'name':S(80),'overwrite':B},['scene','name']),False)
]

def tool_definitions():
    return [{'name':n,'description':d,'inputSchema':s,'annotations':{'readOnlyHint':ro,'destructiveHint':not ro,'idempotentHint':ro,'openWorldHint':False}} for n,d,s,ro in TOOLS]


def invoke(name:str,args:dict) -> dict:
    functions={'library_info':library_info,'search_assets':search_assets,'get_asset':asset_info,'list_templates':list_templates,'get_template':get_template,'get_guidelines':get_guidelines,'stencil_guide':stencil_guide,'get_scene_schema':schema,'layout_diagram':auto_layout,'validate_diagram':validate,'render_diagram':render_diagram,'preview_diagram':preview_diagram,'export_diagram':export_diagram}
    if name not in functions:raise ValueError('Unknown tool.')
    return functions[name](**args)
