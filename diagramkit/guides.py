"""Topic guides (knowledge bases) the model reads before composing a diagram.

Bundled guides live in library/guides/*.md. An operator may add or override topics with
house conventions by setting STENCIL_GUIDE_DIR to a local folder of .md files. That folder
is read-only input: only regular *.md files directly inside it, with a valid topic name and
a bounded size, are used; symlinks, subfolders and anything else are ignored. No network.
"""
from __future__ import annotations
import os, re
from pathlib import Path
from .library import ROOT

BUNDLED=ROOT/'guides'
TOPIC=re.compile(r'[a-z0-9][a-z0-9-]{0,39}')
MAX_GUIDE_BYTES=65_536
MAX_GUIDES=100

RULE=('Before composing, confirm the brief. List what it states and what it leaves open; ask the user '
      'about every open fact that changes what is drawn (components, counts, placement, links, protocol '
      'or process behaviour, boundaries, redundancy), giving the default you would use for each. Push back '
      'when the brief conflicts with how a technology works. Do not add components the user did not '
      'mention. Then read the guide for your diagram type.')


def _scan(folder:Path,source:str) -> dict:
    found={}
    try:entries=sorted(folder.iterdir())
    except OSError:return found
    for path in entries:
        if len(found)>=MAX_GUIDES:break
        topic=path.name[:-3] if path.name.endswith('.md') else ''
        if not TOPIC.fullmatch(topic) or path.is_symlink() or not path.is_file():continue
        try:
            if path.stat().st_size>MAX_GUIDE_BYTES:continue
            text=path.read_text(encoding='utf-8')
        except (OSError,UnicodeError):continue
        found[topic]={'id':topic,'source':source,'markdown':text,**_heading(text,topic)}
    return found


def _heading(text:str,topic:str) -> dict:
    title=next((l[2:].strip() for l in text.splitlines() if l.startswith('# ')),topic)
    summary=next((l[1:].strip() for l in text.splitlines() if l.startswith('>')),'')
    return {'title':title[:120],'summary':summary[:300]}


def _all() -> dict:
    guides=_scan(BUNDLED,'bundled')
    extra=os.environ.get('STENCIL_GUIDE_DIR','').strip()
    if extra:guides.update(_scan(Path(extra).expanduser(),'local'))
    return guides


def stencil_guide(topic:str='') -> dict:
    guides=_all()
    if not topic:
        index=[{k:g[k] for k in ('id','title','summary','source')} for g in guides.values()]
        return {'rule':RULE,'how_to_use':'Call stencil_guide with a topic id. Read "brief" first, then the topic that matches the diagram, then "style".','topics':index}
    if not isinstance(topic,str) or not TOPIC.fullmatch(topic):raise ValueError('Topic ids are lower-case words joined by hyphens, such as "network".')
    if topic not in guides:raise ValueError(f'No guide named {topic!r}. Available: {", ".join(sorted(guides))}.')
    g=guides[topic]
    return {'id':g['id'],'title':g['title'],'source':g['source'],'rule':RULE,'markdown':g['markdown']}
