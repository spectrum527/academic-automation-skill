"""Portable contracts; fixtures never access a real academic account."""
import contextlib
import hashlib
import io
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote
from pathlib import Path
from unittest.mock import patch

from pdf_fixture import PDF

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from academic_automation import browser, browser_runtime as br, cli, cnki, publisher, cnki_batch as batch, download_watch as dw
from academic_automation.errors import BrowserError
import build_release


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='academic-tests-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        env = patch.dict(os.environ, {'ACADEMIC_STATE_DIR': str(self.root / 'state'),
                                      'CNKI_DOWNLOADS_DIR': str(self.root),
                                      'ACADEMIC_BROWSER_BACKEND': 'extension',
                                      'ACADEMIC_BROWSER_SESSION': 'test'})
        env.start(); self.addCleanup(env.stop)

    def pdf(self, name='论文_张三.pdf'):
        path = self.root / name
        path.write_bytes(PDF)
        return path

    def test_cli_json_missing_author_and_argument_errors(self):
        for args in [['download', 'cnki', '论文', '', str(self.root)], ['search', 'not-a-source']]:
            output = io.StringIO()
            with contextlib.redirect_stdout(output), patch.object(browser, 'get_browser') as get:
                code = cli.main(['--json'] + args)
            self.assertEqual(code, 64)
            self.assertFalse(json.loads(output.getvalue())['ok'])
            get.assert_not_called()

    def test_unsupported_search_filters_are_not_silently_ignored(self):
        args = cli.parser().parse_args(['search','cnki-foreign','Q',str(self.root/'out.json'),'--oa'])
        with patch.object(cnki,'foreign_search') as search:
            with self.assertRaises(BrowserError) as error: cli.dispatch(args)
        self.assertEqual(error.exception.code,64); search.assert_not_called()

    def test_result_parser_preserves_json_and_multiline_strings(self):
        payload = '{"title":"中文","body":"line\\n### Result"}'
        self.assertEqual(browser.cli_result('### Result\n' + json.dumps(payload) + '\n### Page\n'), payload)
        with self.assertRaises(BrowserError): browser.cli_result('### Page\nno result')

    def test_backend_switch_and_package_default(self):
        with patch.dict(os.environ, {'ACADEMIC_BROWSER_BACKEND': ''}), patch.object(browser, 'ROOT', self.root):
            (self.root/'platform.json').write_text('{"default_backend":"extension"}', encoding='utf-8')
            self.assertEqual(browser.backend_name(), 'extension')
            (self.root/'platform.json').unlink()
            with patch.object(browser.platform, 'system', return_value='Darwin'):
                self.assertEqual(browser.backend_name(), 'apple-events')
            with patch.object(browser.platform, 'system', return_value='Windows'):
                self.assertEqual(browser.backend_name(), 'extension')

    def test_browser_exclusion_is_released_after_failure(self):
        with browser.browser_lock():
            with self.assertRaises(BrowserError) as error:
                with browser.browser_lock(): pass
            self.assertEqual(error.exception.code, 75)
        with browser.browser_lock(): pass

    def test_extension_requires_explicit_connection(self):
        with self.assertRaises(BrowserError) as error:
            browser.ExtensionBrowser().evaluate('document.title')
        self.assertEqual(error.exception.code, 2)

    def test_long_javascript_uses_file_and_round_trips_unicode(self):
        browser.save_session({'connected': True})
        source = '"' + '中文' * 25000 + '"'
        def execute(*args, **kwargs):
            self.assertEqual(args[0], 'run-code')
            path = Path(args[1].split('=', 1)[1])
            self.assertIn(json.dumps(source), path.read_text(encoding='utf-8'))
            return '### Result\n"返回值"\n'
        with patch.object(browser, 'cli_call', side_effect=execute):
            self.assertEqual(browser.ExtensionBrowser().evaluate(source), '返回值')

    def test_windows_safe_names_and_archive_copy_failure(self):
        self.assertEqual(dw.safe_name('CON.pdf'), '_CON.pdf')
        self.assertEqual(dw.safe_name('题名: a?.pdf '), '题名_ a_.pdf')
        source = self.pdf(); dest = self.root / '含空格 archive'
        with patch.object(dw.shutil, 'copyfileobj', side_effect=PermissionError('locked')):
            with self.assertRaises(PermissionError): dw.archive(source, dest)
        self.assertTrue(source.exists())
        self.assertEqual(list(dest.iterdir()), [])
        saved = dw.archive(source, dest)
        self.assertTrue(dw.valid_file(saved))

    def test_manual_save_resumes_before_any_navigation(self):
        dest = self.root / '文献 archive'
        cp = cnki.pending_path(dest, batch.identity('论文', '张三', dest))
        br.atomic_json(cp, {'status':'waiting', 'downloads':str(self.root), 'before':dw.snapshot(self.root), 'since':0})
        self.pdf()
        with patch.object(cnki, 'locate') as locate:
            first = cnki._download('论文', '张三', dest)
            second = cnki._download('论文', '张三', dest)
        locate.assert_not_called()
        self.assertEqual(first['path'], second['path'])
        self.assertTrue(second['cached'])

    def test_waiting_without_file_does_not_retry_download(self):
        dest = self.root/'archive'; cp = cnki.pending_path(dest, batch.identity('论文', '张三', dest))
        br.atomic_json(cp, {'status':'waiting', 'downloads':str(self.root), 'before':{}, 'since':0})
        with patch.object(dw, 'wait_download', side_effect=BrowserError('not found',4)), patch.object(cnki, 'locate') as locate:
            with self.assertRaises(BrowserError) as error: cnki._download('论文','张三',dest)
        self.assertEqual(error.exception.code,2); locate.assert_not_called()

    def test_explicit_manual_archive_finishes_checkpoint(self):
        dest = self.root/'archive'; cp = cnki.pending_path(dest,batch.identity('论文','张三',dest))
        br.atomic_json(cp,{'status':'waiting','title':'论文','author':'张三','downloads':str(self.root),'before':{},'since':0})
        manual = self.pdf('manual-name.pdf')
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(['--json','archive',str(dest),'--file',str(manual),'--name','论文_张三.pdf','--checkpoint',str(cp)])
        self.assertEqual(code,0)
        with patch.object(cnki,'locate') as locate:
            result = cnki._download('论文','张三',dest)
        locate.assert_not_called(); self.assertTrue(result['cached'])

    def test_archive_recovery_after_move_before_checkpoint(self):
        saved = self.pdf('already-saved.pdf'); cp = self.root/'journal.json'
        br.atomic_json(cp, {'status':'archiving','candidate':str(self.root/'deleted-temp.pdf'),
                           'archive_target':str(saved), 'candidate_sha256':hashlib.sha256(saved.read_bytes()).hexdigest()})
        result = cnki.resume_download(cp, self.root)
        self.assertEqual(result['path'],str(saved))
        self.assertEqual(br.read_json(cp)['status'],'complete')

    def test_batch_pause_does_not_start_next_article(self):
        listing = self.root/'titles.txt'
        listing.write_text('甲论文|张三|'+str(self.root/'out')+'\n乙论文|李四|'+str(self.root/'out'),encoding='utf-8')
        with patch.object(sys,'argv',['batch',str(listing)]), patch.object(batch.subprocess,'run',return_value=subprocess.CompletedProcess([],2,'NEEDS_USER\n')) as call:
            with self.assertRaises(SystemExit) as error: batch.main()
        self.assertEqual(error.exception.code,2); self.assertEqual(call.call_count,1)
        self.assertIn('待人工',Path(batch.state_path(str(listing))).read_text(encoding='utf-8'))
        self.assertIn('academic.py',call.call_args.args[0][1])

    def test_foreign_checkpoint_replay_is_offline(self):
        output = self.root/'foreign.json'
        br.atomic_json(str(output)+'.progress.json', {'version':1,'config':{'mode':'cnki-foreign','query':'assessment'},
            'pages':{'1':{'rows':[{'title':'A','href':'https://example.org/a'}]}},'records':{}})
        with patch.object(br,'navigate') as navigate:
            result = cnki._foreign_search('assessment',output)
        navigate.assert_not_called(); self.assertEqual(result['n'],1)

    def test_publisher_candidates_preserve_ojs_download_and_ignore_non_http(self):
        result = publisher.pdf_candidates('PDF@@https://example.org/article/view/1/2\nPDF@@javascript:bad')
        self.assertEqual(result,['https://example.org/article/download/1/2'])

    def test_direct_download_rejects_html(self):
        with patch.object(publisher,'urlopen',return_value=io.BytesIO(b'<html>paywall</html>')):
            self.assertFalse(publisher.direct_pdf('https://example.org/a',self.root/'bad.pdf'))
        self.assertFalse((self.root/'bad.pdf').exists())

    def test_shared_cli_bibliography_has_only_one_json_response(self):
        source = self.root/'input.json'; output = self.root/'目录.md'
        source.write_text(json.dumps({'rows':[{'title':'Title','href':'https://example.org/article'}]}),encoding='utf-8')
        result = subprocess.run([sys.executable,str(ROOT/'scripts/academic.py'),'--json','bibliography','scholar',str(source),str(output)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['ok'])
        self.assertIn('[Title](https://example.org/article)',output.read_text(encoding='utf-8'))

    def test_platform_packages_are_reproducible_and_unpack_as_skills(self):
        one = build_release.build(ROOT,self.root/'one')
        two = build_release.build(ROOT,self.root/'two')
        for a,b in zip(one,two):
            self.assertEqual(a.read_bytes(),b.read_bytes())
            with zipfile.ZipFile(a) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertEqual({name.split('/')[0] for name in names}, {'academic-automation'})
                self.assertRegex(archive.read('academic-automation/SKILL.md').decode('utf-8'), r'(?m)^name: academic-automation$')
                for document in ('README.md', 'README.zh-CN.md'):
                    text = archive.read('academic-automation/' + document).decode('utf-8')
                    for asset in re.findall(r'(?:\]\(|src=")(assets/[^)"\s]+)', text):
                        self.assertEqual(archive.read('academic-automation/' + asset), (ROOT/asset).read_bytes())
                self.assertFalse(any('node_modules/' in n or '.academic-downloads/' in n or '.git/' in n for n in names))
                if a.name.endswith('windows.zip'):
                    self.assertIn('academic-automation/academic.cmd',names)
                    self.assertFalse(any(n.endswith('.sh') for n in names))
                target = self.root/a.stem; archive.extractall(target)
            skill = target/'academic-automation'
            for link in re.findall(r'\]\(([^)]+)\)', (skill/'INSTALL.md').read_text(encoding='utf-8')):
                if not re.match(r'(?:[a-zA-Z][\w+.-]*:|/|#)', link):
                    self.assertTrue((skill/link.split('#',1)[0]).is_file(), link)
            result = subprocess.run([sys.executable,str(skill/'scripts/academic.py'),'--help'],cwd=str(self.root),capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)

    def test_apple_navigation_waits_for_new_document_across_proxy_redirect(self):
        transport = browser.AppleEventsBrowser()
        # The complete old document must not satisfy a publisher readiness wait.
        with patch.object(transport, 'evaluate', side_effect=['https://institution.example/login', 'false', 'false', 'true']) as evaluate, patch.object(transport, 'target') as target, patch.object(browser.time, 'sleep'):
            self.assertEqual(transport.navigate('https://publisher.example/article'), 'navigated')
        self.assertEqual(evaluate.call_count, 4)
        target.assert_called_once()
        with patch.object(transport, 'evaluate', return_value='https://publisher.example/article#one') as evaluate, patch.object(transport, 'target'):
            transport.navigate('https://publisher.example/article#two')
        self.assertEqual(evaluate.call_count, 1)

    def test_readiness_detects_visible_institution_login_only(self):
        source = (ROOT/'scripts/browser_ready.js').read_text().replace('__OPTIONS__', json.dumps({'mode':'wos-basic'}))
        for visible in (True, False):
            fixture = '''const vm=require('vm');
const password={getClientRects:()=>VISIBLE?[{}]:[]};
const context={location:{href:'https://institution.example/idp/profile/SAML2/POST/SSO'},window:{innerHeight:900},
getComputedStyle:()=>({visibility:'visible'}),URL,
document:{title:'统一身份认证',body:{innerText:'请登录'},readyState:'complete',querySelector:()=>null,
querySelectorAll:s=>s==='input[type="password"]'?[password]:[]}};
process.stdout.write(vm.runInNewContext(SOURCE,context));'''.replace('VISIBLE', json.dumps(visible)).replace('SOURCE', json.dumps(source))
            result = subprocess.run(['node','-e',fixture],capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(result.stdout)['login'], visible)


@unittest.skipUnless(os.environ.get('ACADEMIC_BROWSER_TESTS') == '1','Set ACADEMIC_BROWSER_TESTS=1 for isolated Chrome transport tests')
class ChromeTransportTests(unittest.TestCase):
    def test_pinned_cli_and_real_page_scripts(self):
        def task(args):
            output = io.StringIO()
            with contextlib.redirect_stdout(output): code = cli.main(['--json', *args])
            response = json.loads(output.getvalue())
            self.assertEqual(code, 0, response)
            return response['result']
        with tempfile.TemporaryDirectory(prefix='academic-chrome-') as folder:
            env = {'PWTEST_DAEMON_SESSION_DIR':str(Path(folder)/'daemon'),
                   'ACADEMIC_STATE_DIR':str(Path(folder)/'state'), 'ACADEMIC_BROWSER_BACKEND':'extension',
                   'ACADEMIC_BROWSER_SESSION':'academic-fixture'}
            with patch.dict(os.environ,env):
                try:
                    browser.cli_call('open','about:blank','--browser=chrome')
                    # This test verifies the CLI transport only, not extension attach.
                    browser.save_session({'connected':True})
                    transport = browser.ExtensionBrowser()
                    transport.code('async page => {await page.setContent("<title>Academic fixture</title><p>中文校验</p>"); return true;}')
                    result = json.loads(transport.evaluate('JSON.stringify({title:document.title,text:document.body.innerText})'))
                    self.assertEqual(result,{'title':'Academic fixture','text':'中文校验'})
                    requests = []
                    class Fixture(BaseHTTPRequestHandler):
                        def log_message(self, *args): pass
                        def do_GET(self):
                            requests.append((self.path, self.headers.get('Referer','')))
                            if self.path.startswith('/download') or self.path == '/protected.pdf':
                                if self.path == '/protected.pdf' and '/protected-article' not in self.headers.get('Referer', ''):
                                    self.send_response(202); self.end_headers()
                                    self.wfile.write(b'<html>Browser request required</html>'); return
                                content = PDF
                                self.send_response(200)
                                self.send_header('Content-Type','application/pdf')
                                self.send_header('Content-Disposition',"attachment; filename*=UTF-8''"+quote('测试论文_张三.pdf'))
                            else:
                                if self.path == '/protected-article':
                                    content = '<title>Protected article</title><p>' + ('Article body. '*40) + '</p><a href="/protected.pdf">Article PDF</a>'
                                elif self.path.startswith('/kcms2/article/abstract'):
                                    control = '<a href="/download.pdf">PDF下载</a>'
                                    if 'handler=1' in self.path:
                                        # A bare href cannot download this article: the site's
                                        # actual click handler and user activation are required.
                                        control = '<a style="display:none" href="/wrong.pdf">PDF下载</a><a id="pdfDown" href="javascript:void(0)" onclick="if(event.isTrusted) location.href=\'/download.pdf\'">PDF 下载</a>'
                                    content = '<title>测试论文 - 中国知网</title><div class="author">张三</div><p>摘要：'+('测试摘要。'*60)+'</p>'+control
                                else:
                                    content = '<title>检索</title><input id="txt_search"><a class="ch" data-val="Chinese">中文</a><p>共找到 1 条</p><table><tbody><tr><td><a href="/kcms2/article/abstract?filename=fixture&handler=1">测试论文</a></td><td>张三</td></tr></tbody></table>'
                                content = content.encode('utf-8')
                                self.send_response(200)
                                self.send_header('Content-Type','text/html; charset=utf-8')
                            self.send_header('Content-Length',str(len(content)))
                            self.end_headers(); self.wfile.write(content)
                    server = ThreadingHTTPServer(('127.0.0.1',0),Fixture)
                    thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
                    base = 'http://127.0.0.1:'+str(server.server_port)
                    downloads = Path(folder)/'downloads'; downloads.mkdir()
                    try:
                        with patch.dict(os.environ,{'CNKI_DOWNLOADS_DIR':str(downloads)}), patch.object(cnki,'BASE',base+'/search?korder='):
                            args=['download','cnki','测试论文','张三',str(Path(folder)/'中文 archive')]
                            downloaded = task(args)
                            self.assertTrue(dw.valid_file(downloaded['path']))
                            self.assertTrue(br.read_json(downloaded['checkpoint'])['download_event']['saved'])
                            self.assertEqual(task(args)['path'],downloaded['path'])
                        self.assertEqual(sum(path.startswith('/download') for path,ref in requests),1)
                        self.assertFalse(any(path == '/wrong.pdf' for path,ref in requests))
                        self.assertTrue(any(path.startswith('/download') and '/kcms2/article/abstract' in ref for path,ref in requests))
                        # Publisher now owns the same download-event capture, with
                        # no external save listener or default-folder dependency.
                        with patch.object(publisher,'resolve_doi',return_value=base+'/kcms2/article/abstract'):
                            result = task(['download','doi','10.1234/fixture',str(Path(folder)/'publisher'),'--access-policy','all'])
                        self.assertTrue(dw.valid_file(result['path']))
                        with patch.dict(os.environ,{'CNKI_DOWNLOADS_DIR':str(downloads)}), patch.object(publisher,'resolve_doi',return_value=base+'/protected-article'):
                            result = task(['download','doi','10.1234/protected',str(Path(folder)/'browser-publisher'),'--access-policy','all'])
                        self.assertTrue(dw.valid_file(result['path']))
                        self.assertTrue(br.read_json(result['checkpoint'])['download_event']['saved'])
                        self.assertTrue(any(path == '/protected.pdf' and '/protected-article' in ref for path, ref in requests))
                    finally:
                        server.shutdown(); server.server_close(); thread.join(timeout=3)
                    transport.navigate('about:blank')
                    self.assertEqual(transport.evaluate('location.href'),'about:blank')
                finally:
                    browser.cli_call('close')


if __name__ == '__main__':
    unittest.main()
