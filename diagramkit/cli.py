"""Local CLI. The render command writes to the explicit user-supplied output path."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .library import catalog, list_templates, search_assets
from .renderer import render
from .scene import validate
from .service import library_info

def main():
    ap=argparse.ArgumentParser(description='Stencil: editable SVG assets and scenes')
    sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('info');sub.add_parser('templates')
    search=sub.add_parser('search');search.add_argument('query');search.add_argument('--category',default='')
    check=sub.add_parser('validate');check.add_argument('scene')
    make=sub.add_parser('render');make.add_argument('scene');make.add_argument('--output',required=True);make.add_argument('--overwrite',action='store_true')
    args=ap.parse_args()
    try:
        if args.command=='info':print(json.dumps(library_info(),indent=2))
        elif args.command=='templates':print(json.dumps(list_templates(),indent=2))
        elif args.command=='search':print(json.dumps(search_assets(args.query,args.category),indent=2))
        else:
            path=Path(args.scene)
            if path.stat().st_size>1_048_576:raise ValueError('Scene exceeds 1 MiB limit.')
            scene=json.loads(path.read_text(encoding='utf-8'));report=validate(scene)
            if args.command=='validate':print(json.dumps(report,indent=2));return 0 if report['valid'] else 1
            if not report['valid']:raise ValueError(json.dumps(report,indent=2))
            dest=Path(args.output)
            if dest.is_symlink():raise ValueError('Refusing symlink output.')
            if dest.exists() and not args.overwrite:raise ValueError('Output exists; pass --overwrite or choose another path.')
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(render(scene).encode('utf-8'))
            print(json.dumps({'output':str(dest.resolve()),'validation':report},indent=2))
    except (ValueError,OSError,TypeError) as exc:ap.exit(1,str(exc)+'\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
