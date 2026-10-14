"""Small local stdio MCP server implementing the 2025-06-18 tools/resources subset.

No HTTP listener, shell execution, outbound requests, package downloads, or SDK dependency.
This intentionally does not implement sampling, subscriptions, tasks or streaming progress.
For a shared HTTP deployment, replace this adapter with the official MCP SDK plus auth.
"""
from __future__ import annotations
import json, sys
from . import __version__
from .library import ROOT, asset_info, get_template
from .scene import structural_errors, schema
from .service import tool_definitions, invoke, library_info, get_guidelines

PROTOCOL='2025-06-18'
MAX_LINE=1_048_576
RESOURCES=[
 {'uri':'infra-diagram://library/overview','name':'Library overview','mimeType':'application/json'},
 {'uri':'infra-diagram://library/guidelines','name':'Diagram design rules','mimeType':'text/markdown'},
 {'uri':'infra-diagram://library/schema','name':'Scene schema','mimeType':'application/json'}]
PROMPTS=[{'name':'diagram_brief','description':'Plan a technically explicit, readable architecture or explanation diagram.','arguments':[{'name':'brief','description':'What the diagram must explain.','required':True}]}]

def has_lone_surrogate(value,depth=0) -> bool:
    # json.loads turns "\ud800" into an unencodable str; reject it before any part is echoed back.
    if isinstance(value,str):return any('\ud800'<=ch<='\udfff' for ch in value)
    if depth>64:return False
    if isinstance(value,dict):return any(has_lone_surrogate(k,depth+1) or has_lone_surrogate(v,depth+1) for k,v in value.items())
    if isinstance(value,list):return any(has_lone_surrogate(v,depth+1) for v in value)
    return False

def encode(response) -> str:
    try:
        line=json.dumps(response,ensure_ascii=False,separators=(',',':'),allow_nan=False);line.encode('utf-8')
    except (UnicodeEncodeError,ValueError):
        line=json.dumps(Server.error(response.get('id') if isinstance(response.get('id'),int) else None,-32603,'Response could not be encoded.'))
    return line

class RPCError(Exception):
    def __init__(self,code:int,message:str):super().__init__(message);self.code=code

class Server:
    def __init__(self):self.initialized=False;self.ready=False;self.tools={t['name']:t for t in tool_definitions()}

    def dispatch(self,msg):
        if not isinstance(msg,dict) or msg.get('jsonrpc')!='2.0' or not isinstance(msg.get('method'),str):
            return self.error(None,-32600,'Invalid JSON-RPC request.')
        if has_lone_surrogate(msg):return None if 'id' not in msg else self.error(None,-32600,'Request contains invalid Unicode (lone surrogate).')
        ident=msg.get('id');notification='id' not in msg
        if not notification and (type(ident) not in (str,int)):
            return self.error(None,-32600,'Request id must be a string or integer.')
        method=msg['method'];params=msg.get('params',{})
        if not isinstance(params,dict):return None if notification else self.error(ident,-32602,'params must be an object.')
        if notification:
            if method=='notifications/initialized' and self.initialized:self.ready=True
            # Unknown notifications and late cancellation notifications have no response.
            return None
        try:
            if method=='initialize':
                if self.initialized:raise RPCError(-32600,'Already initialized.')
                if not isinstance(params.get('protocolVersion'),str) or not isinstance(params.get('capabilities'),dict) or not isinstance(params.get('clientInfo'),dict):raise RPCError(-32602,'Initialization requires protocolVersion, capabilities and clientInfo.')
                self.initialized=True
                result={'protocolVersion':PROTOCOL,'capabilities':{'tools':{'listChanged':False},'resources':{'subscribe':False,'listChanged':False},'prompts':{'listChanged':False}},'serverInfo':{'name':'stencil-mcp','version':__version__},'instructions':'Before composing, confirm the brief: ask the user about missing facts that change the topology (components, counts, placement, links, protocol behaviour) instead of filling them with a typical pattern, and push back when the brief conflicts with how a technology works. Then start with library_info and get_guidelines. Search existing assets; choose a template; validate and visually inspect the scene. SVG exports are editable. Export writes are confined to INFRA_DIAGRAM_OUTPUT_DIR. Physical links, traffic and feedback are different connector roles.'}
            elif method=='ping':result={}
            elif not self.ready:raise RPCError(-32000,'Complete initialize and notifications/initialized first.')
            elif method=='tools/list':
                if params.get('cursor'):raise RPCError(-32602,'This small tool list has no additional pages.')
                result={'tools':list(self.tools.values())}
            elif method=='tools/call':
                name=params.get('name');args=params.get('arguments',{})
                if not isinstance(name,str) or name not in self.tools:raise RPCError(-32602,'Unknown tool name.')
                errors=structural_errors(args,self.tools[name]['inputSchema'])
                if errors:raise RPCError(-32602,json.dumps(errors,ensure_ascii=False))
                try:
                    payload=invoke(name,args)
                    image=payload.pop('_image',None)
                    result={'content':[{'type':'text','text':json.dumps(payload,ensure_ascii=False)}],'structuredContent':payload,'isError':False}
                    if image:result['content'].append({'type':'image','data':image,'mimeType':'image/png'})
                except (ValueError,KeyError,OSError,TypeError) as exc:
                    result={'content':[{'type':'text','text':str(exc)}],'isError':True}
            elif method=='resources/list':result={'resources':RESOURCES}
            elif method=='resources/templates/list':result={'resourceTemplates':[{'uriTemplate':'infra-diagram://asset/{category}/{name}','name':'SVG asset','mimeType':'image/svg+xml'},{'uriTemplate':'infra-diagram://template/{name}','name':'Diagram scene','mimeType':'application/json'}]}
            elif method=='resources/read':
                uri=params.get('uri','');mime='application/json'
                if not isinstance(uri,str):raise RPCError(-32602,'uri must be a string.')
                if uri==RESOURCES[0]['uri']:data=json.dumps(library_info())
                elif uri==RESOURCES[1]['uri']:data=get_guidelines()['guidelines'];mime='text/markdown'
                elif uri==RESOURCES[2]['uri']:data=json.dumps(schema())
                elif uri.startswith('infra-diagram://asset/'):
                    try:data=asset_info(uri[len('infra-diagram://asset/'):],True)['svg'];mime='image/svg+xml'
                    except ValueError as exc:raise RPCError(-32002,str(exc))
                elif uri.startswith('infra-diagram://template/'):
                    try:data=json.dumps(get_template(uri[len('infra-diagram://template/'):]))
                    except ValueError as exc:raise RPCError(-32002,str(exc))
                else:raise RPCError(-32002,'Unknown registered resource.')
                result={'contents':[{'uri':uri,'mimeType':mime,'text':data}]}
            elif method=='prompts/list':result={'prompts':PROMPTS}
            elif method=='prompts/get':
                args=params.get('arguments',{})
                if params.get('name')!='diagram_brief' or not isinstance(args,dict) or not isinstance(args.get('brief'),str) or not 1<=len(args['brief'])<=2000:raise RPCError(-32602,'Use diagram_brief with a brief string of 1–2000 characters.')
                content='Create a diagram for this brief:\n'+args['brief']+'\n\n'+'Before drawing, list what the brief states and what it leaves open. Ask the user about every open fact that would change the topology (components, counts, placement, links, protocol behaviour), giving the default you would use for each; do not fill gaps with a typical pattern or add components the user did not mention. Push back if the brief conflicts with how a technology works. '+'Then identify entities, ownership/trust boundaries, and the exact relationship of each connector. Separate physical topology from traffic overlays. Use library asset IDs and a template. Keep labels brief; split crowded explanations into panels. Produce scene JSON, run validation, render SVG, inspect it, then revise overlaps. Do not infer product compatibility or protocol behavior from icons.'
                result={'description':'Diagram planning prompt','messages':[{'role':'user','content':{'type':'text','text':content}}]}
            else:raise RPCError(-32601,'Method not found.')
            return {'jsonrpc':'2.0','id':ident,'result':result}
        except RPCError as exc:return self.error(ident,exc.code,str(exc))
        except Exception as exc:
            print(f'Internal error: {type(exc).__name__}: {exc}',file=sys.stderr)
            return self.error(ident,-32603,'Internal error; see server stderr.')

    @staticmethod
    def error(ident,code,message):return {'jsonrpc':'2.0','id':ident,'error':{'code':code,'message':message}}

def main():
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8',newline='\n')
    # Keep stdout for JSON-RPC only: any stray print from library code goes to stderr instead.
    out=sys.stdout;sys.stdout=sys.stderr
    server=Server()
    while True:
        raw=sys.stdin.buffer.readline(MAX_LINE+1)
        if not raw:break
        if len(raw)>MAX_LINE:
            print(json.dumps(server.error(None,-32700,'Message exceeds 1 MiB limit.')),file=out,flush=True)
            return 2
        if not raw.strip():continue
        try:
            msg=json.loads(raw.decode('utf-8'),parse_constant=lambda value:(_ for _ in ()).throw(ValueError('Non-finite JSON number.')))
            response=server.dispatch(msg)
        except (ValueError,UnicodeError,RecursionError):response=server.error(None,-32700,'Invalid UTF-8 JSON.')
        if response is not None:
            try:print(encode(response),file=out,flush=True)
            except BrokenPipeError:break
    return 0

if __name__=='__main__':raise SystemExit(main())
