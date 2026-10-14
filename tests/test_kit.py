from __future__ import annotations
import unittest, json, copy, hashlib, os, sys, tempfile, subprocess, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from diagramkit.library import catalog,asset_info,search_assets,list_templates,get_template,ROOT as LIB
from diagramkit.scene import schema,validate,structural_errors,auto_layout,edge_points
from diagramkit.renderer import render,asset_art
from diagramkit.service import export_diagram,tool_definitions,library_info,invoke
from diagramkit.server import Server


def scene():
    return {'version':'1.0','title':'Test diagram','width':850,'height':420,'nodes':[
       {'id':'a','kind':'component','asset':'network/router','x':40,'y':180,'w':200,'h':146,'label':'Router'},
       {'id':'b','kind':'component','asset':'compute/rack-server','x':590,'y':180,'w':200,'h':146,'label':'Server'}
    ],'edges':[{'id':'ab','source':'a','target':'b','label':'Data'}]}

def req(method,params=None,id=1):return {'jsonrpc':'2.0','id':id,'method':method,**({'params':params} if params is not None else {})}
def init(server,version='2025-06-18'):
    result=server.dispatch(req('initialize',{'protocolVersion':version,'capabilities':{},'clientInfo':{'name':'test','version':'1'}}))
    server.dispatch({'jsonrpc':'2.0','method':'notifications/initialized'})
    return result

class CatalogTests(unittest.TestCase):
    def test_counts(self):
        c=catalog();self.assertEqual(324,len(c['assets']));self.assertEqual(20,len(c['categories']));self.assertEqual(324,sum(cat['count'] for cat in c['categories']))
    def test_unique_ids(self):
        ids=[a['id'] for a in catalog()['assets']];self.assertEqual(len(ids),len(set(ids)))
    def test_all_assets_parse_and_checksums_match(self):
        for a in catalog()['assets']:
            with self.subTest(a=a['id']):
                raw=(LIB/a['file']).read_text(encoding='utf-8');root=ET.fromstring(raw)
                self.assertEqual('0 0 144 112',root.attrib['viewBox']);self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),a['sha256'])
                self.assertTrue(asset_art(a['id']))
    def test_anchor_bounds(self):
        for a in catalog()['assets']:
            self.assertEqual({'n','e','s','w'},set(a['anchors']))
            for point in a['anchors'].values():self.assertTrue(all(0<=v<=1 for v in point))
    def test_lookup_and_metadata(self):
        self.assertNotIn('svg',asset_info('network/router'));self.assertIn('<svg',asset_info('network/router',True)['svg'])
    def test_lookup_does_not_accept_path(self):
        with self.assertRaises(ValueError):asset_info('../../etc/passwd',True)
    def test_search(self):
        self.assertTrue(any(a['id']=='compute/hypervisor' for a in search_assets('proxmox')['assets']))
        self.assertTrue(any(a['id']=='hardware/rdma-nic' for a in search_assets('rdma')['assets']))
    def test_search_category_pagination(self):
        r=search_assets('',category='network',limit=5);self.assertEqual(5,len(r['assets']));self.assertEqual(5,r['next_offset'])
        self.assertTrue(all(a['category']=='network' for a in r['assets']))
    def test_all_templates_valid_no_warnings(self):
        self.assertEqual(24,len(list_templates()['templates']))
        for t in list_templates()['templates']:
            with self.subTest(template=t['id']):self.assertEqual([],validate(get_template(t['id']))['issues'])
    def test_template_copy(self):
        s=get_template('mrc-loss-recovery');s['title']='Changed';self.assertNotEqual('Changed',get_template('mrc-loss-recovery')['title'])
    def test_mrc_states_are_consistent(self):
        s=get_template('mrc-loss-recovery');n={x['id']:x for x in s['nodes']}
        self.assertEqual(['1','2','3','—','5'],[c['value'] for c in n['rx-before']['cells']])
        self.assertEqual(['1','2','3','4','5'],[c['value'] for c in n['rx-after']['cells']])
        self.assertEqual('4',n['retry4']['label']);self.assertEqual('dropped',n['loss']['state'])
        sack=next(e for e in s['edges'] if e['kind']=='feedback')
        self.assertEqual('retry-receiver',sack['source']);self.assertEqual('retry-sender',sack['target'])
        self.assertTrue(any(e['target']=='loss' and e['palette']=='purple' for e in s['edges']))
        self.assertFalse(any(e['target']=='receiver' and e['palette']=='purple' for e in s['edges']))

class ValidationTests(unittest.TestCase):
    def test_valid_scene(self):self.assertEqual({'valid':True,'issues':[]},validate(scene()))
    def test_bad_asset(self):
        s=scene();s['nodes'][0]['asset']='bad/id';self.assertFalse(validate(s)['valid'])
    def test_bad_endpoint(self):
        s=scene();s['edges'][0]['target']='missing';self.assertFalse(validate(s)['valid'])
    def test_duplicate(self):
        s=scene();s['nodes'][1]['id']='a';self.assertFalse(validate(s)['valid'])
    def test_negative_coordinates(self):
        s=scene();s['nodes'][0]['x']=-1;self.assertFalse(validate(s)['valid'])
    def test_nonfinite(self):
        s=scene();s['nodes'][0]['x']=float('nan');self.assertFalse(validate(s)['valid'])
    def test_bool_is_not_coordinate(self):
        s=scene();s['nodes'][0]['x']=True;self.assertFalse(validate(s)['valid'])
    def test_unknown_fields(self):
        s=scene();s['nodes'][0]['onclick']='bad';self.assertFalse(validate(s)['valid'])
    def test_bounds(self):
        s=scene();s['nodes'][0]['x']=800;self.assertFalse(validate(s)['valid'])
    def test_overlap(self):
        s=scene();s['nodes'][1]['x']=90;self.assertIn('node_overlap',[i['code'] for i in validate(s)['issues']])
    def test_text_warning(self):
        s=scene();s['nodes'][0]['label']='Really long text '*10;self.assertIn('text_height',[i['code'] for i in validate(s)['issues']])
    def test_group_scope(self):
        s=scene();s['nodes'][0]['group']='absent';self.assertFalse(validate(s)['valid'])
    def test_waypoints(self):
        s=scene();s['edges'][0]['points']=[{'x':-5,'y':200}];self.assertFalse(validate(s)['valid'])
    def test_edges_compact_collinear_points(self):
        s=scene();self.assertEqual(2,len(edge_points(s['edges'][0],{n['id']:n for n in s['nodes']})))
    def test_jsonschema_agrees_for_examples(self):
        try:import jsonschema
        except ImportError:self.skipTest('Optional jsonschema dependency is not installed.')
        jsonschema.Draft202012Validator.check_schema(schema())
        for t in list_templates()['templates']:jsonschema.validate(get_template(t['id']),schema())
    def test_layout_dag(self):
        s=auto_layout('Flow',[{'id':'a','asset':'network/router','label':'Router'},{'id':'b','asset':'compute/rack-server','label':'Server'}],[{'id':'e1','source':'a','target':'b'}])
        self.assertTrue(validate(s)['valid']);self.assertLess(s['nodes'][0]['x'],s['nodes'][1]['x'])
    def test_layout_cycle(self):
        s=auto_layout('Cycle',[{'id':'a','asset':'network/router','label':'A'},{'id':'b','asset':'network/router','label':'B'}],[{'id':'e1','source':'a','target':'b'},{'id':'e2','source':'b','target':'a'}])
        self.assertIn('cycle',s['description'])

class RendererTests(unittest.TestCase):
    def test_svg_xml_and_unique_ids(self):
        for t in list_templates()['templates']:
            svg=render(get_template(t['id']));root=ET.fromstring(svg)
            ids=[el.attrib['id'] for el in root.iter() if 'id' in el.attrib];self.assertEqual(len(ids),len(set(ids)),t['id'])
    def test_themes(self):
        for theme in ('light','dark','monochrome'):
            s=scene();s['theme']=theme;ET.fromstring(render(s))
    def test_escape(self):
        s=scene();s['nodes'][0]['label']='<script>alert("x")</script>'
        svg=render(s);self.assertNotIn('<script>',svg);self.assertIn('&lt;script&gt;',svg)
    def test_deterministic(self):self.assertEqual(render(scene()),render(scene()))
    def test_invalid_render_refused(self):
        s=scene();s['nodes'][0]['asset']='bad'
        with self.assertRaises(ValueError):render(s)
    def test_exports(self):
        with tempfile.TemporaryDirectory() as td:
            out=export_diagram(scene(),'test',output_dir=Path(td));self.assertTrue(Path(out['svg_path']).exists());self.assertTrue(Path(out['scene_path']).exists())
            with self.assertRaises(ValueError):export_diagram(scene(),'test',output_dir=Path(td))
            export_diagram(scene(),'test',True,output_dir=Path(td))
    def test_export_paths_rejected(self):
        for name in ('../test','/tmp/test','C:\\tmp\\test','test.svg','a/b','', 'a'*81):
            with self.subTest(name=name),self.assertRaises(ValueError):export_diagram(scene(),name)
    def test_export_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);outside=root/'target';outside.write_text('unchanged')
            try:(root/'link.svg').symlink_to(outside)
            except OSError:self.skipTest('Symlinks not permitted on this host.')
            with self.assertRaises(ValueError):export_diagram(scene(),'link',True,output_dir=root)
            self.assertEqual('unchanged',outside.read_text())
    def test_preview_optional(self):
        try:import cairosvg
        except (ImportError,OSError):self.skipTest('Optional preview renderer or native Cairo library not installed.')
        from diagramkit.service import preview_diagram
        out=preview_diagram(scene(),400);self.assertTrue(out['_image'].startswith('iVBOR'))
    def test_preview_missing_dependency_messages(self):
        # Both ways the optional extra can be unavailable must give an actionable ValueError.
        import builtins
        from unittest import mock
        from diagramkit.service import preview_diagram
        real=builtins.__import__
        for exc,expect in ((ImportError('No module named cairosvg'),'stencil-mcp[preview]'),
                           (OSError('no library called "cairo-2" was found'),'native Cairo library')):
            with self.subTest(exc=type(exc).__name__):
                def fake(name,*a,**k):
                    if name=='cairosvg':raise exc
                    return real(name,*a,**k)
                with mock.patch.object(builtins,'__import__',fake):
                    with self.assertRaises(ValueError) as ctx:preview_diagram(scene(),400)
                self.assertIn(expect,str(ctx.exception))

class MCPTests(unittest.TestCase):
    def test_handshake_and_version_negotiation(self):
        srv=Server();result=init(srv,'2026-07-28');self.assertEqual('2025-06-18',result['result']['protocolVersion'])
        self.assertIn('tools',result['result']['capabilities'])
    def test_confirm_brief_guidance_on_every_channel(self):
        # Models skip get_guidelines, so "ask before guessing" must reach them however they start.
        from diagramkit.service import get_guidelines
        srv=Server();result=init(srv)
        self.assertIn('confirm the brief',result['result']['instructions'])
        prompt=srv.dispatch(req('prompts/get',{'name':'diagram_brief','arguments':{'brief':'Two racks and a firewall'}}))
        self.assertIn('Ask the user about every open fact',prompt['result']['messages'][0]['content']['text'])
        self.assertTrue(library_info()['workflow'][0].startswith('confirm the brief'))
        self.assertIn('## Confirm the brief before drawing',json.dumps(get_guidelines()))
    def test_preinit_guard(self):self.assertIn('error',Server().dispatch(req('tools/list')))
    def test_notifications_no_response(self):self.assertIsNone(Server().dispatch({'jsonrpc':'2.0','method':'notifications/anything'}))
    def test_invalid_request(self):self.assertEqual(-32600,Server().dispatch([])['error']['code'])
    def test_invalid_id(self):self.assertEqual(-32600,Server().dispatch(req('ping',id=[]))['error']['code'])
    def test_ping(self):self.assertEqual({},Server().dispatch(req('ping'))['result'])
    def test_tools_list(self):
        srv=Server();init(srv);tools=srv.dispatch(req('tools/list'))['result']['tools'];self.assertEqual(12,len(tools));self.assertLess(len(json.dumps(tools)),15000)
    def test_tool_search(self):
        srv=Server();init(srv);r=srv.dispatch(req('tools/call',{'name':'search_assets','arguments':{'query':'firewall'}}))
        self.assertFalse(r['result']['isError']);self.assertGreater(r['result']['structuredContent']['total'],0)
    def test_tool_schema_error(self):
        srv=Server();init(srv);r=srv.dispatch(req('tools/call',{'name':'search_assets','arguments':{'limit':0}}));self.assertEqual(-32602,r['error']['code'])
    def test_tool_execution_error(self):
        srv=Server();init(srv);r=srv.dispatch(req('tools/call',{'name':'get_asset','arguments':{'asset_id':'missing'}}));self.assertTrue(r['result']['isError'])
    def test_validate_tool_returns_report(self):
        srv=Server();init(srv);r=srv.dispatch(req('tools/call',{'name':'validate_diagram','arguments':{'scene':{}}}));self.assertFalse(r['result']['isError']);self.assertFalse(r['result']['structuredContent']['valid'])
    def test_resources(self):
        srv=Server();init(srv);r=srv.dispatch(req('resources/read',{'uri':'infra-diagram://library/guidelines'}));self.assertIn('Diagram composition',r['result']['contents'][0]['text'])
        self.assertIn('error',srv.dispatch(req('resources/read',{'uri':'file:///etc/passwd'})))
    def test_prompt(self):
        srv=Server();init(srv);r=srv.dispatch(req('prompts/get',{'name':'diagram_brief','arguments':{'brief':'A small network'}}));self.assertEqual('user',r['result']['messages'][0]['role'])
    def test_stdio_subprocess_roundtrip(self):
        init_msg=req('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'test-client','version':'1'}},1)
        lines=[init_msg,{'jsonrpc':'2.0','method':'notifications/initialized'},req('tools/list',id=2),req('tools/call',{'name':'search_assets','arguments':{'query':'rdma'}},3),req('tools/call',{'name':'render_diagram','arguments':{'scene':scene()}},4),req('resources/read',{'uri':'infra-diagram://library/overview'},5)]
        run=subprocess.run([sys.executable,str(ROOT/'server.py')],input='\n'.join(json.dumps(x) for x in lines)+'\n',text=True,encoding='utf-8',capture_output=True,timeout=15)
        self.assertEqual(0,run.returncode,run.stderr);out=[json.loads(line) for line in run.stdout.splitlines()];self.assertEqual(5,len(out));self.assertIn('<svg',out[3]['result']['structuredContent']['svg'])
    def test_malformed_input_then_recovery(self):
        run=subprocess.run([sys.executable,str(ROOT/'server.py')],input='not json\n'+json.dumps(req('ping'))+'\n',text=True,capture_output=True,timeout=5)
        out=[json.loads(line) for line in run.stdout.splitlines()];self.assertEqual(-32700,out[0]['error']['code']);self.assertEqual({},out[1]['result'])
    def test_oversized_line(self):
        run=subprocess.run([sys.executable,str(ROOT/'server.py')],input='x'*1_048_578,text=True,capture_output=True,timeout=5)
        self.assertEqual(2,run.returncode);self.assertIn('exceeds',run.stdout)

class HardeningTests(unittest.TestCase):
    """Regression tests for the 0.2.0 design-gauntlet findings."""
    def test_legacy_asset_bytes_frozen(self):
        frozen=json.loads((ROOT/'tests/fixtures/legacy_sha256.json').read_text(encoding='utf-8'));idx={a['id']:a for a in catalog()['assets']}
        self.assertEqual(300,len(frozen))
        for aid,digest in frozen.items():
            with self.subTest(asset=aid):
                self.assertEqual(digest,idx[aid]['sha256']);self.assertEqual(digest,hashlib.sha256((LIB/idx[aid]['file']).read_bytes()).hexdigest())
    def test_active_svg_content_rejected(self):
        # A tampered asset whose catalog checksum was updated to match must still be refused.
        from unittest import mock
        import diagramkit.renderer as r
        ns='xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
        bad={'script':f'<svg {ns}><g><script>alert(1)</script></g></svg>',
             'onload':f'<svg {ns}><g><path d="M0 0" onload="x()"/></g></svg>',
             'href':f'<svg {ns}><g><path d="M0 0" href="https://example.com"/></g></svg>',
             'xlink_href':f'<svg {ns}><g><path d="M0 0" xlink:href="https://example.com"/></g></svg>',
             'style':f'<svg {ns}><g><rect width="1" height="1" style="fill:red"/></g></svg>',
             'url':f'<svg {ns}><g><rect width="1" height="1" fill="url(https://example.com/x)"/></g></svg>',
             'foreign':f'<svg {ns}><g><foreignObject/></g></svg>'}
        for case,svg in bad.items():
            with self.subTest(case=case):
                meta={'svg':svg,'sha256':hashlib.sha256(svg.encode()).hexdigest()}
                r.asset_art.cache_clear()
                with mock.patch.object(r,'asset_info',return_value=meta):
                    with self.assertRaises(ValueError):r.asset_art('test/'+case)
        r.asset_art.cache_clear()
    def test_source_has_no_hidden_characters(self):
        # Trojan Source (CVE-2021-42574): bidi overrides and zero-width characters make code
        # read differently from how it runs. Patterns that block them must use escapes.
        hidden=set(range(0x200b,0x2010))|set(range(0x202a,0x202f))|set(range(0x2066,0x206a))|{0xfeff}
        files=[*ROOT.glob('diagramkit/*.py'),*ROOT.glob('scripts/*.py'),*ROOT.glob('tests/*.py'),*ROOT.glob('.github/**/*.yml'),ROOT/'server.py']
        for path in files:
            with self.subTest(file=path.name):
                text=path.read_text(encoding='utf-8')
                self.assertFalse([hex(ord(c)) for c in text if ord(c) in hidden])
    def test_catalog_hashes_match_disk_bytes(self):
        for a in catalog()['assets']:
            with self.subTest(a=a['id']):self.assertEqual(a['sha256'],hashlib.sha256((LIB/a['file']).read_bytes()).hexdigest())
    def test_identifier_trailing_newline_rejected(self):
        s=scene();s['nodes'][0]['id']='a\n';s['edges'][0]['source']='a\n';self.assertFalse(validate(s)['valid'])
    def test_illegal_characters_rejected(self):
        for bad in ('\u202eevorppA','zero\u200bwidth','tag\U000e0041','lone\ud800','bom\ufeff','bell\x07'):
            with self.subTest(text=repr(bad)):
                s=scene();s['nodes'][0]['label']=bad;r=validate(s)
                self.assertFalse(r['valid']);self.assertIn('illegal_character',[i['code'] for i in r['issues']])
    def test_script_joiners_still_allowed(self):
        s=scene();s['nodes'][0]['label']='\u0645\u06cc\u200c\u062e\u0648\u0627\u0647\u0645';self.assertTrue(validate(s)['valid'])
    def test_oversized_array_not_traversed(self):
        s=scene();s['nodes']=[{} for _ in range(19000)];r=validate(s)
        self.assertFalse(r['valid']);self.assertLessEqual(len(r['issues']),5)
    def test_warning_flood_is_capped(self):
        s={'version':'1.0','title':'Flood','width':1000,'height':800,'nodes':[{'id':f'm{i}','kind':'marker','x':100,'y':100} for i in range(200)],'edges':[]}
        r=validate(s);self.assertTrue(r['valid']);self.assertEqual(200,len(r['issues']));self.assertGreater(r['truncated'],0)
    def test_marker_states_select_matching_symbol(self):
        def one(state):return render({'version':'1.0','title':'M','width':600,'height':300,'nodes':[{'id':'m','kind':'marker','x':100,'y':100,'state':state}],'edges':[]})
        self.assertIn(asset_art('status/blocked'),one('blocked'));self.assertNotIn(asset_art('status/healthy'),one('blocked'))
        self.assertIn(asset_art('status/pending'),one('pending'));self.assertIn(asset_art('status/healthy'),one('received'))
    def test_symbol_caption_is_visible(self):
        s=scene();s['nodes'].append({'id':'g','kind':'symbol','asset':'presentation/decision','x':340,'y':40,'w':124,'h':108,'label':'Approved?','caption':'Approved?'})
        self.assertTrue(validate(s)['valid']);self.assertIn('>Approved?</text>',render(s))
    def test_accessible_name_and_description_split(self):
        svg=render(scene());self.assertIn('aria-labelledby="diagram-title"',svg);self.assertIn('aria-describedby="diagram-description"',svg)
    def test_export_reserved_windows_names(self):
        for name in ('NUL','con','Com1','LPT9','aux'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as td,self.assertRaises(ValueError):export_diagram(scene(),name,output_dir=Path(td))
    def test_export_leaves_no_staging_or_lock_files(self):
        with tempfile.TemporaryDirectory() as td:
            export_diagram(scene(),'clean',output_dir=Path(td));export_diagram(scene(),'clean',True,output_dir=Path(td))
            self.assertEqual(['clean.scene.json','clean.svg'],sorted(p.name for p in Path(td).iterdir()))
            self.assertNotIn(b'\r\n',(Path(td)/'clean.svg').read_bytes())
    def test_export_concurrent_writer_refused(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'.busy.lock').write_text('')
            with self.assertRaises(ValueError):export_diagram(scene(),'busy',output_dir=Path(td))
            self.assertFalse((Path(td)/'busy.svg').exists())
    def test_export_stale_lock_cleared(self):
        with tempfile.TemporaryDirectory() as td:
            lock=Path(td)/'.old.lock';lock.write_text('');os.utime(lock,(0,0))
            export_diagram(scene(),'old',output_dir=Path(td));self.assertFalse(lock.exists())
    def test_lone_surrogate_request_does_not_kill_server(self):
        lines='{"jsonrpc":"2.0","id":"\\ud800","method":"ping"}\n'+json.dumps(req('ping',id=7))+'\n'
        run=subprocess.run([sys.executable,str(ROOT/'server.py')],input=lines,text=True,encoding='utf-8',capture_output=True,timeout=10)
        self.assertEqual(0,run.returncode,run.stderr);out=[json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual(-32600,out[0]['error']['code']);self.assertEqual({'jsonrpc':'2.0','id':7,'result':{}},out[1])
    def test_department_templates_use_lanes(self):
        for tid in ('eng-platform-delivery','sec-incident-response','it-onboarding-access','fin-procurement-approval','hr-employee-onboarding','sales-lead-to-cash','it-change-approval','support-escalation'):
            with self.subTest(template=tid):
                s=get_template(tid);self.assertTrue(any(g.get('style')=='lane' for g in s['groups']))
                self.assertTrue(all(n.get('group') for n in s['nodes'] if n['kind'] in ('component','symbol')))

if __name__=='__main__':unittest.main()
