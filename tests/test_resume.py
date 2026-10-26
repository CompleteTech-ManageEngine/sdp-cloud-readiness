"""Synthetic instance-boundary durability, isolation, and privacy regressions."""
import contextlib
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sdp_audit.cli import main
from sdp_audit.collect import CollectionOptions
from sdp_audit.environment import EnvironmentOptions
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.diagnostics import diagnostics_document
from sdp_audit.models import EnvironmentSnapshot, ResourceSpec
from sdp_audit.resume import ResumableAssessment, checkpoint_lock, read_checkpoint, retry_candidates
from sdp_audit.synthetic import (create_synthetic_client, SYNTHETIC_HOST, PRIVATE_DESCRIPTION,
    PRIVATE_SUBJECT, PRIVATE_EMAIL, PRIVATE_FILENAME, PRIVATE_DEFAULT, PRIVATE_SCRIPT, PRIVATE_OPTION)


RESOURCE = ResourceSpec('requests', '/requests', 'requests', 'request',
                        'https://example.org/api', detail=False)


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.options = CollectionOptions(page_size=2, subresource_parents=0)
        self.env_options = EnvironmentOptions(discover_fields=False, collect_orgusers=False)
        self.counter = 0

    def run_scan(self, *, budget=3, resume=None, options=None, host=None, scenario=None,
                 multi_key=False, keys=None, env_options=None, runtime=1200, discover=False, retry_failed=False, retry_portals=None, restart_all=False):
        self.counter += 1
        output = self.root / str(self.counter)
        output.mkdir()
        client, server, _ = create_synthetic_client(scenario or {
            'topology': 'multi', 'record_counts': {'1': {'requests': 3}, '2': {'requests': 3}}},
            max_requests=budget, max_runtime=runtime, multi_key=multi_key, api_key=None if multi_key else 'synthetic-key')
        self.last_server = server
        if host:
            client.base_url = host
        for pid, key in (keys or {}).items():
            client.bind_portal_credential(client.base_url, pid, key)
        env = EnvironmentSnapshot('2026-10-26T12:00:00+00:00',
            {'host': client.base_url, 'product': 'ServiceDesk Plus On-Premises'},
            {'max_requests': budget, 'collections_selected': ['requests'], 'portal_ids': ['1', '2'],
             'portal_discovery_mode': 'explicit'})
        runner = ResumableAssessment(client, [RESOURCE], options or self.options,
            env_options or self.env_options, None, None, output, resume=resume,
            retry_failed=retry_failed, retry_portals=retry_portals, restart_all=restart_all)
        with contextlib.redirect_stdout(io.StringIO()):
            runner.collect(env, None if discover else ['1', '2'])
        return env, server, output / 'checkpoint.json'

    def test_budget_resume_skips_committed_instance_and_preserves_report(self):
        first, _, checkpoint = self.run_scan(budget=3)
        saved = read_checkpoint(checkpoint)
        self.assertEqual(set(saved['portals']), {'1'})
        self.assertEqual(first.stop_classification, 'REQUEST_BUDGET_REACHED')
        resumed, server, latest = self.run_scan(budget=20, resume=checkpoint)
        self.assertTrue(server.calls)
        self.assertTrue(all(call['portal_id'] == '2' for call in server.calls))
        self.assertEqual(set(read_checkpoint(latest)['portals']), {'1', '2'})
        self.assertEqual(resumed.resume_history[0]['requests'], 3)
        fresh, _, _ = self.run_scan(budget=20)
        report, baseline = analyze_environment(resumed), analyze_environment(fresh)
        self.assertEqual(report.coverage, baseline.coverage)
        self.assertEqual([f.__dict__ for f in report.findings], [f.__dict__ for f in baseline.findings])
        self.assertTrue(report.portals[0]['checkpoint_reused'])
        self.assertIsNone(resumed.stop_classification)

    def test_complete_checkpoint_makes_no_http_requests(self):
        _, _, checkpoint = self.run_scan(budget=20)
        _, server, latest = self.run_scan(budget=20, resume=checkpoint)
        self.assertEqual(server.calls, [])
        self.assertTrue(read_checkpoint(latest)['global_done'])

    def test_changed_host_or_plan_rejected_before_http(self):
        _, _, checkpoint = self.run_scan()
        for kwargs in ({'host': 'https://other.example.org'},
                       {'options': replace(self.options, page_size=1)}):
            with self.assertRaisesRegex(ValueError, 'differ'):
                self.run_scan(resume=checkpoint, **kwargs)
            self.assertEqual(self.last_server.calls, [])

    def test_corrupt_truncated_and_wrong_version_rejected(self):
        _, _, checkpoint = self.run_scan()
        raw = checkpoint.read_bytes()
        for content in (raw[:40], raw.replace(b'"schema_version":1', b'"schema_version":2'),
                        raw.replace(b'"global_done":false', b'"global_done":true')):
            checkpoint.write_bytes(content)
            with self.assertRaisesRegex(ValueError, 'Invalid'):
                read_checkpoint(checkpoint)
        checkpoint.write_bytes(raw)

    def test_locks_fail_closed_and_release(self):
        path = self.root / 'checkpoint.json'
        with checkpoint_lock(path):
            with self.assertRaisesRegex(ValueError, 'locked'):
                with checkpoint_lock(path):
                    self.fail('Concurrent resume accepted')
        self.assertFalse(path.with_name('checkpoint.json.lock').exists())

    def test_failed_checkpoint_replace_preserves_previous_bytes(self):
        _, _, checkpoint = self.run_scan()
        before = checkpoint.read_bytes()
        with patch('sdp_audit.artifacts.os.replace', side_effect=OSError('synthetic failure')):
            from sdp_audit.artifacts import atomic_write_bytes
            with self.assertRaises(OSError):
                atomic_write_bytes(checkpoint, b'incomplete')
        self.assertEqual(checkpoint.read_bytes(), before)

    def test_missing_assignment_remains_pending_independent_key_finishes(self):
        _, _, checkpoint = self.run_scan(budget=20, multi_key=True, keys={'2': 'second-key'})
        self.assertEqual(set(read_checkpoint(checkpoint)['portals']), {'2'})
        _, server, latest = self.run_scan(budget=20, resume=checkpoint, multi_key=True,
            keys={'1': 'first-key', '2': 'rotated-second-key'})
        self.assertEqual(set(read_checkpoint(latest)['portals']), {'1', '2'})
        self.assertTrue(all(call['portal_id'] == '1' for call in server.calls))
        self.assertNotIn('second-key', latest.read_text())
        self.assertNotIn('first-key', latest.read_text())
        self.assertNotIn('rotated-second-key', latest.read_text())

    def test_checkpoint_excludes_raw_records_and_private_fields(self):
        env, _, checkpoint = self.run_scan(budget=20)
        text = checkpoint.read_text()
        self.assertNotIn('synthetic-key', text)
        self.assertNotIn('"records":', text)
        self.assertNotIn('"details":', text)
        self.assertEqual(json.loads(text)['contract']['resources'][0]['description'], '')
        self.assertEqual(len(analyze_environment(env).portals), 2)
        for secret in (PRIVATE_DESCRIPTION, PRIVATE_SUBJECT, PRIVATE_EMAIL, PRIVATE_FILENAME,
                       PRIVATE_DEFAULT, PRIVATE_SCRIPT, PRIVATE_OPTION):
            self.assertNotIn(secret, text)

    def test_partial_directory_checkpoint_does_not_repeat_terminal_stop(self):
        first, _, checkpoint = self.run_scan(budget=1, discover=True)
        self.assertEqual(first.stop_classification, 'REQUEST_BUDGET_REACHED')
        self.assertFalse(read_checkpoint(checkpoint)['portals'])
        resumed, server, _ = self.run_scan(budget=20, resume=checkpoint, discover=True)
        self.assertIsNone(resumed.stop_classification)
        self.assertTrue(server.calls)
        self.assertTrue(all(call['path'] != '/portals' for call in server.calls))
        self.assertFalse(resumed.topology.complete)
        self.assertEqual({p for p in resumed.portals}, {'1', '2'})

    def test_time_budget_and_interrupt_keep_completed_instances(self):
        for kwargs, reason in (({'runtime': 3}, 'TIME_BUDGET_REACHED'),
                ({'scenario': {'topology': 'multi', 'record_counts': {
                    '1': {'requests': 3}, '2': {'requests': 3}}, 'interrupt_at_attempt': 3}}, 'INTERRUPTED')):
            first, _, checkpoint = self.run_scan(budget=20, **kwargs)
            self.assertEqual(first.stop_classification, reason)
            self.assertEqual(set(read_checkpoint(checkpoint)['portals']), {'1'})
            _, server, _ = self.run_scan(budget=20, resume=checkpoint)
            self.assertTrue(all(call['portal_id'] == '2' for call in server.calls))

    def test_denied_operations_are_retained_as_gaps_not_retried_forever(self):
        scenario = {'topology': 'multi', 'errors': {'1:/requests': {
            'http_status': 403, 'api_code': 4002, 'message': 'Forbidden'}}}
        _, _, checkpoint = self.run_scan(budget=20, scenario=scenario)
        saved = read_checkpoint(checkpoint)
        self.assertEqual(saved['portals']['1']['coverage'][0]['outcome'], 'PERMISSION_DENIED')
        env, server, _ = self.run_scan(budget=20, resume=checkpoint, scenario=scenario)
        self.assertFalse(server.calls)
        row = next(row for row in analyze_environment(env).coverage if row['portal_id'] == '1')
        self.assertFalse(row['list_complete'])
        self.assertIsNone(row['records_observed'])
        self.assertIn('PERMISSION_DENIED', diagnostics_document(env))

    def test_global_credential_uses_only_global_reads_and_is_retained_once(self):
        output = self.root / 'global-first'
        output.mkdir()
        client, server, _ = create_synthetic_client(multi_key=True, api_key=None)
        for pid in ('1', '2'):
            client.bind_portal_credential(client.base_url, pid, 'instance-key-' + pid)
        client.bind_global_credential(client.base_url, '1', 'global-only-key')
        env = EnvironmentSnapshot('2026-10-26T12:00:00+00:00', {'host': client.base_url}, {'max_requests': 500})
        options = replace(self.env_options, collect_orgusers=True)
        runner = ResumableAssessment(client, [RESOURCE], self.options, options, None, None, output)
        with contextlib.redirect_stdout(io.StringIO()):
            runner.collect(env, ['1', '2'])
        self.assertTrue(any(call['path'] == '/orgusers' for call in server.calls))
        checkpoint = output / 'checkpoint.json'
        self.assertTrue(read_checkpoint(checkpoint)['global_done'])
        second = self.root / 'global-second'
        second.mkdir()
        client, server, _ = create_synthetic_client(multi_key=True, api_key=None)
        for pid in ('1', '2'):
            client.bind_portal_credential(client.base_url, pid, 'rotated-instance-' + pid)
        client.bind_global_credential(client.base_url, '1', 'rotated-global')
        env = EnvironmentSnapshot('2026-10-26T13:00:00+00:00', {'host': client.base_url}, {'max_requests': 500})
        runner = ResumableAssessment(client, [RESOURCE], self.options, options, None, None, second, resume=checkpoint)
        with contextlib.redirect_stdout(io.StringIO()):
            runner.collect(env, ['1', '2'])
        self.assertFalse(server.calls)
        self.assertEqual(len(analyze_environment(env).global_resources['coverage']), 1)
        for key in ('instance-key-1', 'global-only-key', 'rotated-global'):
            self.assertNotIn(key, (second / 'checkpoint.json').read_text())

    def test_retry_selection_ignores_successfully_recovered_history(self):
        entries = {'7': {'coverage': [{'outcome': 'COMPLETE'}],
                         'fields': [{'status': 'COMPLETE'}],
                         'diagnostics': [{'classification': 'PARSE_ERROR'}]},
                   '42': {'coverage': [], 'fields': [{'status': 'PARSE_ERROR'}]}}
        self.assertEqual(retry_candidates(entries), {'42'})

    def test_retry_failed_recollects_only_transient_failure(self):
        scenario = {'topology': 'multi', 'errors': {'1:/requests': {
            'http_status': 500, 'api_code': 4004, 'message': 'Internal error'}}}
        _, _, checkpoint = self.run_scan(budget=30, scenario=scenario)
        old = read_checkpoint(checkpoint)
        env, server, latest = self.run_scan(budget=30, resume=checkpoint, retry_failed=True)
        self.assertTrue(server.calls)
        self.assertTrue(all(call['portal_id'] == '1' for call in server.calls))
        self.assertTrue(next(r for r in analyze_environment(env).coverage if r['portal_id'] == '1')['list_complete'])
        self.assertEqual(read_checkpoint(latest)['portals']['2']['findings'], old['portals']['2']['findings'])
        self.assertIn('SERVER_ERROR', env.resume_history[-1]['prior_outcomes']['1'])

    def test_selective_retry_does_not_automatically_retry_permission_denial(self):
        scenario = {'topology': 'multi', 'inaccessible_portals': ['1']}
        _, _, checkpoint = self.run_scan(budget=30, scenario=scenario)
        _, server, _ = self.run_scan(budget=30, resume=checkpoint, retry_failed=True, scenario=scenario)
        self.assertFalse(server.calls)
        env, server, _ = self.run_scan(budget=30, resume=checkpoint, retry_portals='1')
        self.assertTrue(server.calls)
        self.assertTrue(all(call['portal_id'] == '1' for call in server.calls))
        self.assertTrue(next(r for r in analyze_environment(env).coverage if r['portal_id'] == '1')['list_complete'])

    def test_interrupted_retry_preserves_prior_commit_and_pending_selection(self):
        _, _, checkpoint = self.run_scan(budget=30)
        old = read_checkpoint(checkpoint)
        _, _, stopped = self.run_scan(budget=1, resume=checkpoint, retry_portals='1')
        data = read_checkpoint(stopped)
        self.assertEqual(data['pending_retries'], ['1'])
        self.assertEqual(data['portals']['1']['findings'], old['portals']['1']['findings'])
        _, server, latest = self.run_scan(budget=30, resume=stopped)
        self.assertTrue(all(call['portal_id'] == '1' for call in server.calls))
        self.assertFalse(read_checkpoint(latest)['pending_retries'])

    def test_restart_all_allows_limit_change_but_not_host_or_scope_change(self):
        capped = replace(self.options, max_records=2)
        _, _, checkpoint = self.run_scan(budget=30, options=capped)
        with self.assertRaisesRegex(ValueError, 'differ'):
            self.run_scan(budget=30, resume=checkpoint, options=self.options)
        _, server, latest = self.run_scan(budget=30, resume=checkpoint, options=self.options, restart_all=True)
        self.assertEqual({c['portal_id'] for c in server.calls}, {'1', '2'})
        self.assertTrue(all(r['list_complete'] for e in read_checkpoint(latest)['portals'].values() for r in e['coverage']))
        with self.assertRaisesRegex(ValueError, 'differ'):
            self.run_scan(budget=30, resume=checkpoint, restart_all=True, host='https://other.example.org')
        with self.assertRaisesRegex(ValueError, 'checkpoint scope'):
            self.run_scan(budget=30, resume=checkpoint, options=capped, retry_portals='999')
        self.assertFalse(self.last_server.calls)

    def test_cli_rejects_diagnostic_checkpoint_and_resumes_slots(self):
        with patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['--no-env', '--diagnose', '--checkpoint']), 1)
        env_file = self.root / '.env'
        env_file.write_text('SDP_HOST=' + SYNTHETIC_HOST + '\n'
            'SDP_INSTANCE_01_PORTAL_ID=1\nSDP_INSTANCE_01_API_KEY=first-key\n'
            'SDP_INSTANCE_02_PORTAL_ID=2\nSDP_INSTANCE_02_API_KEY=second-key\n')
        common = ['--env-file', str(env_file), '--non-interactive', '--quiet',
                  '--modules', 'sites', '--subresource-parents', '0', '--no-portal-cache',
                  '--output-dir', str(self.root / 'reports')]
        with patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            client, _, _ = create_synthetic_client(multi_key=True, api_key=None, max_requests=100)
            with patch('sdp_audit.cli.ReadOnlyClient', return_value=client):
                self.assertEqual(main(common + ['--checkpoint']), 0)
            checkpoint = next((self.root / 'reports').glob('*/checkpoint.json'))
            client, server, _ = create_synthetic_client(multi_key=True, api_key=None, max_requests=100)
            with patch('sdp_audit.cli.ReadOnlyClient', return_value=client):
                self.assertEqual(main(common + ['--resume', str(checkpoint)]), 0)
            self.assertEqual(server.calls, [])


if __name__ == '__main__':
    unittest.main()
