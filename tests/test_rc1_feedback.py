"""RC1 Windows report regressions; fixtures do not claim live Windows coverage."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
import warnings
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from academic_automation import cli, browser, interaction, pdf_verify, pubmed, pmc, ncbi, publisher
from academic_automation import browser_runtime as br
from academic_automation.errors import BrowserError
from test_pubmed import xml


class RC1FeedbackTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name); self.dest = self.root/'中文 papers'
        env = patch.dict(os.environ, {'ACADEMIC_STATE_DIR':str(self.root/'state'),
            'CNKI_DOWNLOADS_DIR':str(self.root/'downloads'), 'ACADEMIC_BROWSER_BACKEND':'extension'})
        env.start(); self.addCleanup(env.stop)
        self.manifest = self.root/'清单.json'
        br.atomic_json(self.manifest, {'access_policy':'free-only', 'rows':['123','456']})
        self.batch = ['batch', self.manifest, '--source','pubmed','--dest',self.dest]

    def call(self, args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out): code = cli.main(['--json', *map(str,args)])
        return code, json.loads(out.getvalue())['result']

    def pending(self, ident='999', route='auto'):
        args = ['download','pubmed',ident,self.dest,'--access-policy','free-only','--route',route]
        with patch.object(pubmed,'download',side_effect=BrowserError('fixture needs review',2)):
            code, result = self.call(args)
        self.assertEqual(code,2)
        return result['pending']

    def verify(self, text):
        fake = types.ModuleType('pypdf')
        fake.PdfReader = lambda p: types.SimpleNamespace(pages=[types.SimpleNamespace(extract_text=lambda:text)])
        with patch.dict(sys.modules, {'pypdf':fake}), patch.object(pdf_verify,'available',return_value=True):
            return pdf_verify.verify('fixture.pdf', {'title':'Evidence linking diabetic retinopathy to Alzheimer disease','first_author_family':'Davies'})

    def test_main_article_supplement_notice_and_wrapping_pass_identity(self):
        notice = 'Electronic supplementary material: The online version of this article contains supplementary material.'
        for text in (notice, notice.replace('version of', 'version\nof')):
            result = self.verify(text+'\nEvidence linking diabetic retinopathy to Alzheimer disease\nDavies\nAbstract')
            self.assertTrue(result['content_verified'])

    def test_true_supplement_and_notice_combined_still_rejected(self):
        for prefix in ('Supplementary material','Supporting Information',
            'Electronic supplementary material: The online version of this article contains supplementary material.\nSupplementary material'):
            with self.assertRaises(BrowserError) as exc:
                self.verify(prefix+'\nEvidence linking diabetic retinopathy to Alzheimer disease\nDavies')
            self.assertIn('PDF_SUPPLEMENT',str(exc.exception))

    def test_notice_exception_does_not_waive_wrong_identity(self):
        with self.assertRaises(BrowserError) as exc:
            self.verify('Electronic supplementary material: The online version of this article contains supplementary material.\nA different article about an unrelated disease, by Other Author, published elsewhere.')
        self.assertIn('PDF_IDENTITY_MISMATCH',str(exc.exception))

    def test_query_file_preserves_quotes_unicode_and_bom(self):
        query = '("Mendelian randomization"[TIAB]) AND "眼科"[Title]'
        path = self.root/'query 中文.txt'; path.write_text(query, encoding='utf-8-sig')
        with patch.object(pubmed,'search',return_value={}) as search:
            code,_ = self.call(['search','pubmed',self.root/'out.json','--query-file',path,'--access-policy','free-only'])
        self.assertEqual(code,0); self.assertEqual(search.call_args.args[0],query)
        inline = cli.parser().parse_args(['search','pubmed',query,str(self.root/'out.json')])
        fromfile = cli.parser().parse_args(['search','pubmed',str(self.root/'out.json'),'--query-file',str(path)])
        cli.normalize_args(fromfile)
        self.assertEqual(interaction.action(inline),interaction.action(fromfile))

    def test_query_file_rejects_ambiguous_or_empty_request_before_dispatch(self):
        path = self.root/'q.txt'; path.write_text('')
        with patch.object(pubmed,'search') as search:
            for args in (['query',self.root/'out.json','--query-file',path],
                         [self.root/'out.json','--query-file',path], [self.root/'out.json']):
                self.assertEqual(self.call(['search','pubmed',*args])[0],64)
        search.assert_not_called()

    def test_pmc_only_no_pdf_never_calls_publisher_and_can_keep_bibliography(self):
        for choice in ('defer','bibliography'):
            with patch.object(ncbi,'fetch',return_value=xml()), patch.object(ncbi,'links',return_value=[]), patch.object(pmc,'versions',return_value=[]), patch.object(publisher,'article') as article:
                code,result = self.call(['download','pubmed','123',self.dest/choice,'--route','pmc-only','--on-unavailable',choice,'--access-policy','free-only'])
            self.assertEqual(code,0); article.assert_not_called()
            self.assertEqual(result['status'],'deferred' if choice=='defer' else 'metadata_only')
            self.assertEqual(result['access'],'unknown')

    def test_independent_pmc_download_keeps_browser_pending_and_works_under_browser_lock(self):
        pending = self.pending()
        with browser.browser_lock(), patch.object(ncbi,'fetch',return_value=xml()), patch.object(ncbi,'links',return_value=[]), patch.object(pmc,'versions',return_value=[]):
            code,result = self.call(['download','pubmed','123',self.dest,'--route','pmc-only','--access-policy','free-only'])
        self.assertEqual(code,0); self.assertEqual(result['status'],'deferred')
        self.assertEqual(interaction.read(),pending)

    def test_route_switch_cannot_evade_same_article_pause_either_direction(self):
        for original, other in [('auto','pmc-only'),('pmc-only','auto')]:
            pending = self.pending('123',original)
            with patch.object(pubmed,'download') as download:
                self.assertEqual(self.call(['download','pubmed','123',self.dest,'--route',other,'--access-policy','free-only'])[0],2)
            download.assert_not_called()
            self.call(['browser','resolve','--pending-id',pending['id'],'--decision','skip','--note','fixture user skips'])

    def test_pmc_pause_keeps_browser_pending_and_resolves_by_own_id(self):
        other = self.pending()
        current = self.pending('123','pmc-only')
        self.assertEqual(current['channel'],'pubmed-data'); self.assertEqual(interaction.read(),other)
        self.assertEqual(self.call(['browser','resolve','--pending-id',current['id'],'--decision','retry','--note','fixture actual reply'])[0],0)
        self.assertEqual(interaction.read(),other)
        self.assertTrue(interaction.pending_for_id(current['id'])['user_confirmed'])

    def test_pmc_batch_passes_route_to_children_without_blocking_other_browser_task(self):
        pending = self.pending()
        def child(cmd,**kwargs):
            self.assertIn('pmc-only',cmd)
            return subprocess.CompletedProcess(cmd,0,json.dumps({'result':{'status':'deferred'}}),'')
        with patch.object(pubmed.subprocess,'run',side_effect=child) as run:
            code,result = self.call([*self.batch,'--route','pmc-only'])
        self.assertEqual(code,0); self.assertEqual(run.call_count,2); self.assertEqual(result['deferred'],2)
        self.assertEqual(interaction.read(),pending)

    def test_cancel_batch_is_durable_on_reorder_and_preserves_other_pending(self):
        pending = self.pending()
        with patch.object(pubmed.subprocess,'run') as run:
            code,result = self.call([*self.batch,'--cancel','--note','用户：全部停，只保留题录'])
            self.assertEqual(code,0); self.assertEqual(result['cancelled_by_user'],2)
            br.atomic_json(self.manifest, {'rows':['456','123','789']})
            self.assertEqual(self.call(self.batch)[1]['cancelled_by_user'],3)
            run.assert_not_called()
        self.assertEqual(interaction.read(),pending)

    def test_cancel_requires_reply_and_only_clears_matching_child(self):
        pending = self.pending('123')
        self.assertEqual(self.call([*self.batch,'--cancel'])[0],64)
        self.assertEqual(interaction.read(),pending)
        self.assertEqual(self.call([*self.batch,'--cancel','--note','用户停止该清单'])[0],0)
        self.assertIsNone(interaction.read())
        self.assertIsNotNone(interaction.pending_for_id(pending['id']) if interaction.pending_for_id(pending['id']) else br.read_json(interaction.state_dir()/'user-decisions'/(pending['id']+'.json')))

    def test_cancel_preserves_completed_and_explicit_skips(self):
        cp = str(self.manifest)+'.batch-progress.json'
        br.atomic_json(cp, {'records':{'123':{'code':0,'status':'complete','path':'paper.pdf'},'456':{'code':6,'status':'skipped_by_user'}}})
        code,result = self.call([*self.batch,'--cancel','--note','stop now'])
        self.assertEqual(code,0); self.assertEqual(result['archived'],1); self.assertEqual(result['skipped_by_user'],1)

    def test_cancel_missing_scope_can_clear_parent_handoff(self):
        br.atomic_json(self.manifest, {'rows':['123']})
        code,result = self.call(self.batch); self.assertEqual(code,2)
        self.assertEqual(self.call([*self.batch,'--cancel','--note','cancel this task'])[0],0)
        self.assertIsNone(interaction.read())

    def test_cancelled_batch_only_restarts_after_explicit_reply(self):
        self.call([*self.batch,'--cancel','--note','stop'])
        self.assertEqual(self.call([*self.batch,'--resume-cancelled'])[0],64)
        def child(cmd,**kwargs): return subprocess.CompletedProcess(cmd,0,json.dumps({'result':{'status':'deferred'}}),'')
        with patch.object(pubmed.subprocess,'run',side_effect=child) as run:
            code,_ = self.call([*self.batch,'--resume-cancelled','--note','restart remaining'])
        self.assertEqual(code,0); self.assertEqual(run.call_count,2)

    def test_bibliography_keeps_non_pmc_manifest_rows_and_deduplicates(self):
        allrows = self.root/'all.json'; progress = self.root/'progress.json'
        br.atomic_json(allrows, {'rows':[{'pmid':str(i),'title':'Title'} for i in range(1,41)]})
        br.atomic_json(progress, {'requested_pmids':[str(i) for i in range(1,26)],'records':{'1':{'code':6,'status':'skipped_by_user'},'2':{'code':6,'status':'skipped_by_user'}}})
        code,result = self.call(['bibliography','pubmed',allrows,self.root/'all.md','--progress',progress])
        self.assertEqual(code,0); self.assertEqual(result['records'],40)
        self.assertEqual(result['summary']['pending'],38); self.assertEqual(result['summary']['skipped_by_user'],2)

    def test_status_marks_internal_page_unusable_and_normal_page_unverified(self):
        for url, usable in [('chrome-extension://fixture/connect.html',False),('https://example.test',None)]:
            browser.save_session({'connected':True,'page':{'url':url}})
            code,result = self.call(['browser','status'])
            self.assertEqual(code,0); self.assertIs(result['connection']['usable'],usable)

    def test_browser_source_compiles_without_escape_warnings(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            compile((ROOT/'src/academic_automation/browser.py').read_text(),'browser.py','exec')
        self.assertEqual(caught,[])

    def test_cancelled_parent_can_restart_with_new_scope_reply(self):
        br.atomic_json(self.manifest, {'rows':['123']})
        self.assertEqual(self.call(self.batch)[0],2)
        self.assertEqual(self.call([*self.batch,'--cancel','--note','stop'])[0],0)
        def child(cmd,**kwargs): return subprocess.CompletedProcess(cmd,0,json.dumps({'result':{'status':'deferred'}}),'')
        with patch.object(pubmed.subprocess,'run',side_effect=child) as run:
            code,_ = self.call([*self.batch,'--resume-cancelled','--note','restart only free','--access-policy','free-only'])
        self.assertEqual(code,0); self.assertEqual(run.call_count,1)

    def test_pmc_cancel_clears_only_matching_api_pending(self):
        other = self.pending()
        current = self.pending('123','pmc-only')
        code,_ = self.call([*self.batch,'--route','pmc-only','--cancel','--note','stop this batch'])
        self.assertEqual(code,0); self.assertIsNone(interaction.pending_for_id(current['id']))
        self.assertEqual(interaction.read(),other)

    def test_powershell_bom_manifest_keeps_policy_and_metadata(self):
        self.manifest.write_text(json.dumps({'access_policy':'free-only','rows':[{'pmid':'123','title':'Real title'}]}), encoding='utf-8-sig')
        def child(cmd,**kwargs): return subprocess.CompletedProcess(cmd,0,json.dumps({'result':{'status':'deferred'}}),'')
        with patch.object(pubmed.subprocess,'run',side_effect=child):
            self.assertEqual(self.call(self.batch)[0],0)
        self.assertEqual(br.read_json(str(self.manifest)+'.batch-progress.json')['rows'][0]['title'],'Real title')

    def test_bibliography_alone_deduplicates_and_counts_metadata_as_pending(self):
        br.atomic_json(self.manifest, {'rows':[{'pmid':'123','title':'Real title'},{'pmid':'123','title':'Real title'}]})
        code,result = self.call(['bibliography','pubmed',self.manifest,self.root/'out.md'])
        self.assertEqual(code,0); self.assertEqual(result['records'],1); self.assertEqual(result['summary']['pending'],1)

    def test_legacy_builder_preserves_code_and_excludes_private_files(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        import build_release
        import zipfile
        commit = '1'*40
        blobs = {'SKILL.md':b'---\nname: legacy-skill\nmetadata:\n  version: "1.6.0"\n---\n',
                 'scripts/run.sh':b'#!/bin/sh\necho legacy\n', 'README.md':b'Original README\n',
                 'state/token.json':b'secret', 'papers/private.pdf':b'private'}
        def git(cmd):
            args=cmd[3:]
            if args[0]=='rev-parse': return commit.encode()+b'\n'
            if args[0]=='ls-tree': return '\n'.join(blobs).encode()
            if args[0]=='show': return blobs[args[1].split(':',1)[1]]
            raise AssertionError(args)
        with patch.object(build_release.subprocess,'check_output',side_effect=git):
            path = build_release.legacy_asset(ROOT,self.root,'legacy-version-1')
        with zipfile.ZipFile(path) as z:
            self.assertEqual({name.split('/')[0] for name in z.namelist()}, {'legacy-skill'})
            self.assertEqual(z.read('legacy-skill/SKILL.md'),blobs['SKILL.md'])
            self.assertEqual(z.read('legacy-skill/scripts/run.sh'),blobs['scripts/run.sh'])
            self.assertEqual(z.read('legacy-skill/README.md'),blobs['README.md'])
            self.assertNotIn('legacy-skill/state/token.json',z.namelist())
            meta=json.loads(z.read('legacy-skill/LEGACY_SOURCE.json'))
            self.assertEqual(meta['commit'],commit)
            self.assertEqual(meta['files_sha256']['scripts/run.sh'],hashlib.sha256(blobs['scripts/run.sh']).hexdigest())
            self.assertIn('Accessibility',z.read('legacy-skill/INSTALL.md').decode())

    def test_article_lock_prevents_cross_route_duplicate_transfer(self):
        key=hashlib.sha256(('123\0'+str(self.dest.resolve())).encode()).hexdigest()[:24]
        with browser.browser_lock('pubmed-article-'+key), patch.object(ncbi,'fetch') as fetch:
            code,_=self.call(['download','pubmed','123',self.dest,'--route','pmc-only','--access-policy','free-only'])
        self.assertEqual(code,75); fetch.assert_not_called()
