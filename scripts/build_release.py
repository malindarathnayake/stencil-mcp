#!/usr/bin/env python3
"""Regenerate release metadata: asset-packs.json, VALIDATION_REPORT.json and MANIFEST.sha256.

Run after build_library, build_schema, build_templates and build_gallery. The manifest is
drift detection for the bundle, not a tamper-proof signature.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, platform, subprocess, re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from diagramkit import __version__
from diagramkit.library import catalog, list_templates, get_template
from diagramkit.scene import validate
from diagramkit.renderer import render
from diagramkit.service import tool_definitions

SKIP_DIRS={'.git','.playwright-mcp','__pycache__','.venv','.pytest_cache','build','dist','exports'}

def write(path,data):path.write_bytes(data.encode('utf-8'))

def asset_packs(c):
    packs=[{'id':cat['id'],'name':cat['name'],'count':cat['count'],'preview':f'previews/{cat["id"]}.svg',
            'assets':[{'id':a['id'],'name':a['name'],'description':a['description'],'file':'diagramkit/library/'+a['file']} for a in c['assets'] if a['category']==cat['id']]}
           for cat in c['categories']]
    return {'name':'Stencil','catalog':'diagramkit/library/catalog.json','guidelines':'diagramkit/library/guidelines.md','packs':packs}

def run_tests():
    run=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    log=run.stderr.replace('\r\n','\n');write(ROOT/'docs/TEST_RESULTS.txt',log)
    ran=int(re.search(r'Ran (\d+) tests',log).group(1));skipped=int((re.search(r'skipped=(\d+)',log) or [0,0])[1])
    failed=sum(int(n) for n in re.findall(r'(?:failures|errors)=(\d+)',log))
    return {'run':ran,'passed':ran-failed-skipped,'failed':failed,'skipped':skipped,'details':'docs/TEST_RESULTS.txt'}

def report(c,tests):
    frozen=json.loads((ROOT/'tests/fixtures/legacy_sha256.json').read_text(encoding='utf-8'));idx={a['id']:a for a in c['assets']}
    lib=ROOT/'diagramkit/library'
    templates=[]
    for t in list_templates()['templates']:
        s=get_template(t['id']);r=validate(s)
        templates.append({'template':t['id'],'valid':r['valid'],'warnings':sum(i['severity']=='warning' for i in r['issues']),'deterministic_svg':render(s)==render(s)})
    return {'bundle':'Stencil','bundle_version':__version__,'core_asset_catalog_version':c['version'],
      'generated_utc':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),'os':platform.system(),
      'assets':len(c['assets']),'categories':len(c['categories']),'base_glyph_families':len({a['glyph_family'] for a in c['assets']}),
      'mcp_tools':len(tool_definitions()),'template_count':len(templates),'automated_tests':tests,
      'package_checks':{
        'all_asset_hashes_match_catalog':all(hashlib.sha256((lib/a['file']).read_bytes()).hexdigest()==a['sha256'] for a in c['assets']),
        'legacy_300_asset_svgs_byte_identical':all(idx[k]['sha256']==v and hashlib.sha256((lib/idx[k]['file']).read_bytes()).hexdigest()==v for k,v in frozen.items()),
        'all_template_svgs_repeatable':all(t['deterministic_svg'] for t in templates),
        'server_identifies_as':'stencil-mcp'},
      'template_validation':templates,
      'limits':["No live test against the user's installed Codex or Claude clients.",
        'Concept-sheet PNGs are visual references, not vector source or runtime asset IDs.',
        'Department process templates are illustrative; they are BPMN-lite flowcharts, not BPMN-conformant models.',
        'Protocol semantics, legal name availability and all possible diagram compositions were not verified.']}

def manifest():
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(ROOT).parts)
                 and p.name!='MANIFEST.sha256' and p.suffix!='.pyc')
    return ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in files)

def main():
    c=catalog()
    write(ROOT/'asset-packs.json',json.dumps(asset_packs(c),indent=2,ensure_ascii=False)+'\n')
    write(ROOT/'VALIDATION_REPORT.json',json.dumps(report(c,run_tests()),indent=2)+'\n')
    write(ROOT/'MANIFEST.sha256',manifest())
    print('Release metadata rebuilt.')
if __name__=='__main__':main()
