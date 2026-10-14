#!/usr/bin/env python3
"""Check a built wheel: contents, a clean install, the CLI and one MCP render over stdio.

Usage: python scripts/smoke_wheel.py dist/stencil_mcp-<version>-py3-none-any.whl
Creates a throwaway virtual environment; nothing outside it is installed or changed.
"""
from pathlib import Path
import json, subprocess, sys, tempfile, venv, zipfile

def fail(msg):
    sys.exit('smoke_wheel: '+msg)

def check_contents(wheel):
    names=zipfile.ZipFile(wheel).namelist()
    svgs=sum(n.startswith('diagramkit/library/assets/') and n.endswith('.svg') for n in names)
    templates=sum(n.startswith('diagramkit/library/templates/') and n.endswith('.json') for n in names)
    licenses=[n for n in names if '.dist-info/licenses/' in n and n.endswith('LICENSE')]
    for need in ('diagramkit/library/catalog.json','diagramkit/library/scene.schema.json','diagramkit/library/guidelines.md'):
        if need not in names:fail('missing '+need)
    if not licenses:fail('LICENSE not in wheel metadata')
    if not any(n.startswith('diagramkit/library/guides/') and n.endswith('.md') for n in names):fail('no topic guides in wheel')
    return svgs,templates

def main():
    if len(sys.argv)!=2:fail('pass the wheel path')
    wheel=Path(sys.argv[1]).resolve()
    svgs,templates=check_contents(wheel)
    with tempfile.TemporaryDirectory() as tmp:
        env_dir=Path(tmp)/'venv';venv.create(env_dir,with_pip=True)
        bin_dir=env_dir/('Scripts' if sys.platform=='win32' else 'bin')
        py=bin_dir/('python.exe' if sys.platform=='win32' else 'python')
        subprocess.run([str(py),'-m','pip','install','-q','--disable-pip-version-check',str(wheel)],check=True)
        exe=lambda name:str(bin_dir/(name+('.exe' if sys.platform=='win32' else '')))
        info=json.loads(subprocess.run([exe('stencil-diagram'),'info'],cwd=tmp,check=True,capture_output=True,text=True,encoding='utf-8').stdout)
        if info['asset_count']!=svgs:fail(f"catalog lists {info['asset_count']} assets, wheel has {svgs} SVGs")
        scene=subprocess.run([str(py),'-I','-c','import json;from diagramkit.library import list_templates,get_template;'
                              'print(json.dumps(get_template(list_templates()["templates"][0]["id"])))'],
                             cwd=tmp,check=True,capture_output=True,text=True,encoding='utf-8').stdout
        msgs=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'smoke','version':'1'}}},
              {'jsonrpc':'2.0','method':'notifications/initialized'},
              {'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'render_diagram','arguments':{'scene':json.loads(scene)}}},
              {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'stencil_guide','arguments':{'topic':'network'}}}]
        out=subprocess.run([exe('stencil-mcp')],cwd=tmp,input=''.join(json.dumps(m)+'\n' for m in msgs),
                           capture_output=True,text=True,encoding='utf-8',timeout=60).stdout
        replies={r['id']:r for r in map(json.loads,out.splitlines())}
        if replies.get(1,{}).get('result',{}).get('protocolVersion')!='2025-06-18':fail('initialize failed: '+out[:300])
        render=replies.get(2,{}).get('result',{})
        if render.get('isError') or '<svg' not in json.dumps(render):fail('render failed: '+json.dumps(render)[:300])
        guide=replies.get(3,{}).get('result',{})
        if guide.get('isError') or 'Questions to ask first' not in json.dumps(guide):fail('stencil_guide failed: '+json.dumps(guide)[:300])
    print(f'smoke_wheel: OK {wheel.name}: {svgs} SVGs, {templates} templates, CLI, MCP render and topic guides work')

if __name__=='__main__':main()
