#!/usr/bin/env python3
"""Create local configuration snippets; never edit a client's live settings.

Uses the installed `stencil-mcp` command when it is on PATH (wheel install or
`pip install -e .`), otherwise this interpreter plus the clone's server.py.
"""
from pathlib import Path
import json,sys,os,shlex,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'config';out.mkdir(exist_ok=True)
    installed=shutil.which('stencil-mcp')
    if installed:command,args=str(Path(installed).resolve()),[]
    else:command,args=str(Path(sys.executable).resolve()),[str(ROOT/'server.py')]
    exports=str(Path.home()/'infra-diagram-exports')
    entry={'command':command,'args':args,'env':{'INFRA_DIAGRAM_OUTPUT_DIR':exports}}
    code={'mcpServers':{'stencil':dict(entry,type='stdio')}}
    desktop={'mcpServers':{'stencil':entry}}
    def write(path,text):path.write_bytes(text.encode('utf-8'))
    write(out/'local.mcp.json',json.dumps(code,indent=2)+'\n')
    write(out/'local.claude-desktop.json',json.dumps(desktop,indent=2)+'\n')
    # JSON-escaped basic strings are valid TOML strings for these local filesystem paths.
    toml='[mcp_servers.stencil]\ncommand = '+json.dumps(command)+'\nargs = '+json.dumps(args)+'\nstartup_timeout_sec = 10\ntool_timeout_sec = 30\n\n[mcp_servers.stencil.env]\nINFRA_DIAGRAM_OUTPUT_DIR = '+json.dumps(exports)+'\n'
    write(out/'local.codex.toml',toml)
    quote=subprocess.list2cmdline if os.name=='nt' else shlex.join
    run=['stencil-mcp'] if installed else [command,*args]
    print('Using '+('the installed stencil-mcp command' if installed else 'this clone (stencil-mcp is not on PATH)'))
    print('Wrote configuration snippets under: '+str(out))
    print('Live client settings were not changed. Registration commands:')
    print(quote(['codex','mcp','add','stencil','--',*run]))
    print(quote(['claude','mcp','add','--transport','stdio','--scope','user','stencil','--',*run]))
if __name__=='__main__':main()
