"""Regression for --diagnose ignoring --directory-key and stale D recovery.

All credentials, responses, hosts and clocks here are synthetic. No external
network, account, or native Windows assumption is used by these tests.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from sdp_audit.catalog import RESOURCES
from sdp_audit.cli import main
from sdp_audit.collect import CollectionOptions
from sdp_audit.diagnostics import diagnostics_document
from sdp_audit.environment import EnvironmentCollector, EnvironmentOptions
from sdp_audit.models import EnvironmentSnapshot, PortalInfo
from sdp_audit.portal_scope import PortalScopeResolver, ScopeOptions, save_scope
from sdp_audit.synthetic import (SYNTHETIC_HOST, SYNTHETIC_KEY,
    SYNTHETIC_SENSITIVE_MARKERS, SyntheticResponse, create_synthetic_client)

SECOND_KEY = 'synthetic-second-directory-credential-72937'


def denial(code=4002, status=403):
    return SyntheticResponse({'response_status': [{'status_code': 4000, 'status': 'failed',
        'messages': [{'status_code': code, 'message': 'User does not have this permission' if code == 4002 else 'Invalid API Key'}]}]}, status)


class Router:
    """Log credential categories, never their values; use the real transport."""
    def __init__(self, server, primary='denied', secondary='success', rate_once=False):
        self.server, self.primary, self.secondary = server, primary, secondary
        self.rate_once = rate_once
        self.calls = []

    def open(self, request, timeout):
        path = urlsplit(request.full_url).path.removeprefix('/api/v3')
        key = request.get_header('Authtoken')
        scope = 'directory' if key == SECOND_KEY else 'integration' if key == SYNTHETIC_KEY else 'unexpected'
        assert scope != 'unexpected'
        assert key not in request.full_url
        assert request.get_method() == 'GET' and request.data is None
        portal = request.get_header('Portalid')
        self.calls.append({'path': path, 'scope': scope, 'portal': portal,
                           'time': self.server.clock(), 'method': request.get_method()})
        if scope == 'directory':
            assert path == '/portals' and portal is None
        if path == '/portals':
            if scope == 'directory' and self.rate_once:
                self.rate_once = False
                return SyntheticResponse({'response_status': [{'status_code': 4015, 'status': 'failed'}]}, 429, {'Retry-After': '7'})
            decision = self.secondary if scope == 'directory' else self.primary
            if decision == 'denied':
                return denial()
            if decision == 'invalid':
                return denial(4022, 401)
        return self.server.open(request, timeout)


def routed(**kwargs):
    client, server, clock = create_synthetic_client('multi')
    router = Router(server, **kwargs)
    client._opener = router
    return client, router, clock


def collect(client, options=None, *, diagnose=True, page_size=2):
    # Deliberately omit diagnose_only from settings. EnvironmentOptions must
    # communicate it BEFORE the scope resolver runs, including library calls.
    env = EnvironmentSnapshot('2026-10-14T12:00:00+00:00',
        {'host': SYNTHETIC_HOST, 'demo': True}, {'max_requests': client.max_requests, 'rpm': 30})
    resolver = PortalScopeResolver(client, options or ScopeOptions(
        directory_key=True, no_portal_cache=True, non_interactive=True), page_size=page_size)
    collector = EnvironmentCollector(client, [r for r in RESOURCES if r.key in {'requests', 'projects'}],
        CollectionOptions(page_size=page_size, max_records=1, detail_limit=1, subresource_parents=0),
        EnvironmentOptions(diagnose_only=diagnose, collect_orgusers=False, discover_fields=False),
        scope_resolver=resolver)
    return collector.collect(env)


class DiagnosticCredentialTests(unittest.TestCase):
    def run_cli(self, client, *extra, second=SECOND_KEY):
        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as tmp, \
             patch('sdp_audit.cli.ReadOnlyClient', return_value=client), \
             patch('sdp_audit.cli.acquire_api_key', return_value=SYNTHETIC_KEY) as first_prompt, \
             patch('sdp_audit.portal_scope.acquire_api_key', return_value=second) as second_prompt, \
             patch('builtins.input', side_effect=AssertionError('diagnose must not ask for lists/cache')), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = main(['--host', SYNTHETIC_HOST, '--diagnose', '--no-portal-cache',
                           '--output-dir', tmp, *extra])
            documents = {p.name: p.read_text(encoding='utf-8') for p in Path(tmp).glob('*/*') if p.is_file()}
            return result, stdout.getvalue() + stderr.getvalue(), documents, first_prompt.call_count, second_prompt.call_count

    def test_cli_diagnose_directory_key_prompts_and_performs_two_credential_attempts(self):
        client, router, _ = routed(secondary='denied')
        code, output, docs, first, second = self.run_cli(client, '--directory-key')
        self.assertEqual((code, first, second), (2, 1, 1))
        self.assertEqual([c['scope'] for c in router.calls], ['integration', 'directory'])
        data = json.loads(docs['diagnostics.json'])
        self.assertEqual(data['mode'], 'DISCOVERY_ONLY')
        self.assertEqual(data['http_attempts'], 2)
        self.assertEqual(len(data['diagnostics']), 2)
        self.assertEqual({d['credential_scope'] for d in data['diagnostics']}, {'integration_key', 'directory_key'})
        self.assertNotIn('Portal scope [', output)
        self.assertIn('separate directory-only credential was attempted', output)

    def test_successful_second_directory_is_paginated_but_never_assesses_modules(self):
        client, router, _ = routed()
        code, _, docs, _, count = self.run_cli(client, '--directory-key', '--page-size', '2')
        self.assertEqual(code, 0)
        self.assertEqual(count, 1)
        self.assertEqual(len(router.calls), 3)
        self.assertTrue(all(c['path'] == '/portals' and c['portal'] is None for c in router.calls))
        data = json.loads(docs['assessment.json'])
        self.assertEqual(len(data['portals']), 4)
        self.assertEqual(data['environment']['topology']['credential_scope'], 'directory_key')
        self.assertEqual(json.loads(docs['diagnostics.json'])['authentication'], 'UNVERIFIED')

    def test_directory_env_option_is_honored_in_diagnostic_mode(self):
        client, router, _ = routed(secondary='denied')
        code, _, _, _, second = self.run_cli(client, '--directory-key-env', 'SDP_TEST_DIRECTORY')
        self.assertEqual((code, second), (2, 1))
        self.assertEqual(len(router.calls), 2)

    def test_no_requested_secondary_means_one_directory_attempt(self):
        client, router, _ = routed()
        code, _, _, _, second = self.run_cli(client)
        self.assertEqual((code, second, len(router.calls)), (2, 0, 1))

    def test_successful_initial_directory_does_not_prompt_for_unneeded_key(self):
        client, router, _ = routed(primary='success')
        code, _, _, _, second = self.run_cli(client, '--directory-key')
        self.assertEqual((code, second, len(router.calls)), (0, 0, 1))

    def test_library_diagnostic_mode_sets_boundary_before_resolver(self):
        client, router, _ = routed()
        with patch('sdp_audit.portal_scope.acquire_api_key', return_value=SECOND_KEY) as prompt, \
             patch('builtins.input', side_effect=AssertionError('no list recovery')), contextlib.redirect_stdout(io.StringIO()):
            env = collect(client)
        prompt.assert_called_once()
        self.assertTrue(env.settings['diagnose_only'])
        self.assertTrue(env.source['diagnostic_only'])
        self.assertEqual(set(env.portals), {'1', '2', '3', '4'})
        self.assertTrue(all(not d.read_attempted for p in env.portals.values() for d in p.snapshot.datasets.values()))
        self.assertIsNone(env.global_snapshot)
        self.assertTrue(all(c['path'] == '/portals' for c in router.calls))

    def test_no_saved_list_recovery_or_save_in_diagnostic_mode(self):
        client, router, _ = routed(secondary='denied')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'scope.json'
            save_scope(path, SYNTHETIC_HOST, [PortalInfo('987', 'Unqueried fixture')])
            previous = path.read_bytes()
            with patch('sdp_audit.portal_scope.acquire_api_key', return_value=SECOND_KEY), \
                 patch('sdp_audit.portal_scope.read_scope', side_effect=AssertionError('no profile read')), \
                 patch('sdp_audit.portal_scope.save_scope', side_effect=AssertionError('no profile save')), \
                 contextlib.redirect_stdout(io.StringIO()):
                env = collect(client, ScopeOptions(directory_key=True, save_portals=True, cache_path=path))
            self.assertEqual(path.read_bytes(), previous)
        self.assertFalse(env.portals)
        self.assertEqual(len(router.calls), 2)

    def test_cli_rejects_list_override_or_save_in_diagnostic_before_credentials(self):
        for flags in (['--portal-id', '1'], ['--portal-file', 'does-not-exist.json'], ['--save-portals']):
            with self.subTest(flags=flags), \
                 patch('sdp_audit.cli.acquire_api_key', side_effect=AssertionError('no prompt')), \
                 patch('sdp_audit.cli.ReadOnlyClient', side_effect=AssertionError('no client')), \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(['--diagnose', *flags]), 1)

    def test_invalid_initial_key_is_terminal_and_no_secondary_prompt(self):
        client, router, _ = routed(primary='invalid')
        code, _, docs, _, count = self.run_cli(client, '--directory-key')
        self.assertEqual((code, count, len(router.calls)), (2, 0, 1))
        self.assertEqual(json.loads(docs['diagnostics.json'])['authentication'], 'FAILED')

    def test_invalid_second_key_does_not_mark_original_key_failed(self):
        client, router, _ = routed(secondary='invalid')
        code, _, docs, _, count = self.run_cli(client, '--directory-key')
        self.assertEqual((code, count, len(router.calls)), (2, 1, 2))
        data = json.loads(docs['diagnostics.json'])
        self.assertEqual(data['authentication'], 'UNVERIFIED')
        self.assertEqual(data['diagnostics'][-1]['classification'], 'AUTHENTICATION_FAILED')
        self.assertEqual(data['diagnostics'][-1]['credential_scope'], 'directory_key')

    def test_network_pacing_and_retry_after_stay_global_in_diagnostic(self):
        client, router, _ = routed(rate_once=True)
        code, _, _, _, _ = self.run_cli(client, '--directory-key')
        self.assertEqual(code, 0)
        self.assertEqual(len(router.calls), 3)
        self.assertGreaterEqual(router.calls[1]['time'] - router.calls[0]['time'], 2)
        self.assertGreaterEqual(router.calls[2]['time'] - router.calls[1]['time'], 7)

    def test_attempt_budget_applies_to_second_directory_and_retains_first_denial(self):
        client, router, _ = routed()
        client.max_requests = 1
        code, _, docs, _, _ = self.run_cli(client, '--directory-key')
        self.assertEqual(code, 2)
        self.assertEqual(len(router.calls), 1)
        data = json.loads(docs['diagnostics.json'])
        self.assertEqual(data['scan_stop'], 'REQUEST_BUDGET_REACHED')
        self.assertEqual(data['diagnostics'][0]['classification'], 'PERMISSION_DENIED')

    def test_time_budget_stops_before_second_http_without_losing_diagnostic(self):
        client, router, clock = routed()
        def key_input(*args):
            clock.sleep(client.max_runtime + 1)
            return SECOND_KEY
        with patch('sdp_audit.portal_scope.acquire_api_key', side_effect=key_input), contextlib.redirect_stdout(io.StringIO()):
            env = collect(client)
        self.assertEqual(len(router.calls), 1)
        self.assertEqual(env.stop_classification, 'TIME_BUDGET_REACHED')
        self.assertEqual(env.topology.diagnostics[0]['classification'], 'PERMISSION_DENIED')

    def test_cancel_second_key_preserves_initial_diagnostic_and_no_module_reads(self):
        client, router, _ = routed()
        with patch('sdp_audit.portal_scope.acquire_api_key', side_effect=KeyboardInterrupt), contextlib.redirect_stdout(io.StringIO()):
            env = collect(client)
        self.assertEqual(env.stop_classification, 'INTERRUPTED')
        self.assertEqual(len(router.calls), 1)
        self.assertEqual(env.topology.diagnostics[0]['classification'], 'PERMISSION_DENIED')
        self.assertTrue(json.loads(diagnostics_document(env))['diagnostics'])

    def test_rejected_second_key_input_is_not_printed_or_retried(self):
        client, router, _ = routed()
        output = io.StringIO()
        with patch('sdp_audit.portal_scope.acquire_api_key', side_effect=ValueError(SECOND_KEY)), \
             contextlib.redirect_stdout(output):
            env = collect(client)
        self.assertEqual(len(router.calls), 1)
        self.assertNotIn(SECOND_KEY, output.getvalue())
        self.assertFalse(env.portals)

    def test_failed_second_key_does_not_claim_directory_was_enumerated(self):
        client, _, _ = routed(secondary='denied')
        with patch('sdp_audit.portal_scope.acquire_api_key', return_value=SECOND_KEY), contextlib.redirect_stdout(io.StringIO()):
            env = collect(client)
        self.assertFalse(env.topology.complete)
        self.assertFalse(env.portals)
        self.assertNotIn('Portal metadata was enumerated', ' '.join(env.topology.limitations))

    def test_credentials_and_private_source_canaries_absent_from_all_output(self):
        client, router, _ = routed()
        router.server.portals[0]['name'] = SYNTHETIC_KEY + ' ' + SECOND_KEY
        _, output, docs, _, _ = self.run_cli(client, '--directory-key')
        for text in [output, *docs.values()]:
            for secret in [SECOND_KEY, *SYNTHETIC_SENSITIVE_MARKERS]:
                self.assertNotIn(secret, text)


class RecoveryMenuTests(unittest.TestCase):
    def run_menu(self, *, requested=True, answers, seeds=None):
        client, router, _ = routed(secondary='denied')
        output = io.StringIO()
        prompts = []
        values = iter(answers)
        def input_(prompt):
            prompts.append(prompt)
            return next(values)
        with patch('sdp_audit.portal_scope.acquire_api_key', return_value=SECOND_KEY) as key_prompt, \
             patch('sdp_audit.portal_scope.sys.stdin.isatty', return_value=True), \
             patch('builtins.input', side_effect=input_), contextlib.redirect_stdout(output):
            env = collect(client, ScopeOptions(directory_key=requested, no_portal_cache=True, seed_ids=seeds), diagnose=False)
        return env, router, prompts, output.getvalue(), key_prompt.call_count

    def test_menu_omits_D_when_cli_directory_attempt_has_already_run(self):
        env, router, prompts, output, count = self.run_menu(answers=[''])
        self.assertEqual(prompts, ['Portal scope [L/F/Enter]: '])
        self.assertEqual((count, len(router.calls)), (1, 2))
        self.assertIn('D is unavailable', output)
        self.assertIn('diagnostic reports only; no module assessment', output)
        self.assertFalse(env.portals)

    def test_extra_D_is_explained_but_never_repeats_http_or_key_prompt(self):
        env, router, prompts, output, count = self.run_menu(answers=['d', ''])
        self.assertEqual((len(router.calls), count), (2, 1))
        self.assertTrue(all(p == 'Portal scope [L/F/Enter]: ' for p in prompts))
        self.assertIn('No repeat request was made', output)
        self.assertFalse(env.portals)

    def test_failed_interactive_D_changes_next_prompt_and_preserves_list_recovery(self):
        env, router, prompts, output, count = self.run_menu(requested=False, answers=['d', 'l', '1,3'])
        self.assertEqual(prompts[0], 'Portal scope [D/L/F/Enter]: ')
        self.assertEqual(prompts[1], 'Portal scope [L/F/Enter]: ')
        self.assertEqual(set(env.portals), {'1', '3'})
        self.assertEqual(count, 1)
        self.assertEqual(len([c for c in router.calls if c['path'] == '/portals']), 2)
        self.assertTrue(all(c['scope'] == 'integration' for c in router.calls if c['path'] != '/portals'))
        self.assertTrue(all(c['portal'] in {'1', '3'} for c in router.calls if c['path'] != '/portals'))

    def test_complete_verified_list_still_scans_both_portals_in_same_run(self):
        env, router, _, _, count = self.run_menu(answers=['l', '1,3'])
        self.assertEqual(set(env.portals), {'1', '3'})
        self.assertTrue(all(p.portal.accessible for p in env.portals.values()))
        self.assertFalse(env.topology.complete)
        self.assertEqual(count, 1)
        self.assertGreater(len(router.calls), 2)
        self.assertTrue(all(b['time'] - a['time'] >= 2 for a, b in zip(router.calls, router.calls[1:])))

    def test_blank_input_with_existing_seed_retains_known_scope(self):
        env, router, _, output, _ = self.run_menu(answers=[''], seeds=['1'])
        self.assertEqual(set(env.portals), {'1'})
        self.assertNotIn('No portal IDs are available', output)
        self.assertTrue(any(c['portal'] == '1' for c in router.calls))

    def test_unused_D_is_still_available_before_separate_attempt(self):
        env, router, prompts, _, count = self.run_menu(requested=False, answers=[''])
        self.assertEqual(prompts, ['Portal scope [D/L/F/Enter]: '])
        self.assertEqual((count, len(router.calls)), (0, 1))
        self.assertFalse(env.portals)

    def test_no_permission_bypass_or_endpoint_guess_after_both_denied(self):
        _, router, _, _, _ = self.run_menu(answers=['d', 'd', ''])
        self.assertEqual([(c['method'], c['path'], c['portal']) for c in router.calls],
                         [('GET', '/portals', None), ('GET', '/portals', None)])


if __name__ == '__main__':
    unittest.main()
