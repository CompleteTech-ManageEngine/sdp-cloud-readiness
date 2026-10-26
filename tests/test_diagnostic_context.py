"""2.1.1 regressions for contextual diagnostics and optional count queries.

The failure pattern is based on supplied sanitized diagnostic classifications;
all response content, hostnames, credentials and portal IDs here are synthetic.
The tests never connect to a customer's server.
"""
from __future__ import annotations

from dataclasses import replace
import contextlib
import io
import json
import socket
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from sdp_audit.catalog import RESOURCES, GLOBAL_RESOURCES
from sdp_audit.cli import _cli_options, _cli_parser, main
from sdp_audit.collect import CollectionOptions, Collector
from sdp_audit.diagnostics import diagnostics_document, guidance, safe_diagnostic, diagnostic_lines
from sdp_audit.environment import PortalClient
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.fields import FieldInventory
from sdp_audit.models import Dataset, EnvironmentSnapshot, PortalInfo, PortalSnapshot, Snapshot
from sdp_audit.report import render_report_documents
from sdp_audit.response_contract import shape_evidence, safe_shape
from sdp_audit.topology import discover_topology, topology_scope_evidence
from test_collect import FakeClient, SPEC, page
from test_startup_and_publication import make_client
from test_transport import Response, SECRET

SPECS = {spec.key: spec for spec in RESOURCES + GLOBAL_RESOURCES}
PRIVATE = 'CANARY-TICKET-CONTENT-7f849c'


def ok(wrapper, rows, more=False):
    return Response({'response_status': {'status_code': 2000, 'status': 'success'},
                     wrapper: rows, 'list_info': {'has_more_rows': more}},
                    headers={'Content-Type': 'application/json'})


def mixed_failures():
    """Collect a real transport-shaped mix without real HTTP connections."""
    responses = [ok('requests', [{'id': '9', 'subject': PRIVATE}]),
                 *[socket.timeout(PRIVATE) for _ in range(4)],
                 Response({'response_status': {'status_code': 2000, 'status': 'success'},
                           'modules': [{'id': '67', 'name': PRIVATE}], PRIVATE: PRIVATE,
                           'list_info': {'has_more_rows': False}},
                          headers={'Content-Type': 'application/json'}),
                 Response({'response_status': {'status_code': 4000, 'status': 'failed',
                             'messages': [{'status_code': 4002, 'message': 'User does not have this permission'}]}},
                          403, headers={'Content-Type': 'application/json'})]
    client, opener, clock = make_client(responses, max_requests=30)
    env = EnvironmentSnapshot('2026-10-14T10:00:00+00:00', {'demo': True}, {'count_policy': 'first'})
    env.topology = discover_topology(client, ['7'])
    portal = env.topology.portals[0]
    snap = Snapshot(env.generated_at, {'portal_id': '7', 'portal_name': 'Synthetic IT'}, {'count_policy': 'first'})
    env.portals['7'] = PortalSnapshot(portal, snap)
    resources = [replace(SPECS[key], detail=False) for key in ('requests', 'users', 'asset_modules', 'projects')]
    collector = Collector(PortalClient(client, portal, resources), resources,
                          CollectionOptions(max_records=1, subresource_parents=0))
    collector.prepare(snap)
    for resource in resources:
        collector.read_page(snap, resource.key)
    env.stats = client.stats
    env.authentication = client.stats['authentication'].upper()
    return env, opener


class ContextualDiagnosticTests(unittest.TestCase):
    def test_reported_failure_pattern_keeps_valid_authentication(self):
        env, _ = mixed_failures()
        data = json.loads(diagnostics_document(env))
        self.assertEqual(data['authentication'], 'VALID')
        self.assertNotIn('No successful SDP authentication', json.dumps(data))
        self.assertEqual(len(data['diagnostics']), 3)

    def test_timeout_guidance_not_blanket_authentication_failure(self):
        env, _ = mixed_failures()
        diag = json.loads(diagnostics_document(env))['diagnostics'][0]
        self.assertEqual(diag['transport_detail'], 'CONNECTION_TIMED_OUT')
        self.assertIn('Other successful reads', diag['next_step'])
        self.assertIn('--count-policy never', diag['next_step'])
        self.assertIn('--timeout 90', diag['next_step'])

    def test_projects_advice_does_not_request_directory_access(self):
        env, _ = mixed_failures()
        diag = json.loads(diagnostics_document(env))['diagnostics'][2]
        self.assertEqual(diag['endpoint'], '/projects')
        self.assertEqual(diag['portal_id'], '7')
        self.assertEqual(diag['http_status'], 403)
        self.assertEqual(diag['api_codes'], [4000, 4002])
        self.assertNotIn('Confirm read visibility for the portal directory', diag['next_step'])
        self.assertNotIn('Project Admin', diag['next_step'])
        self.assertIn('specific module operation', diag['next_step'])

    def test_actual_directory_denial_still_has_directory_recovery(self):
        text = guidance({'classification': 'PERMISSION_DENIED', 'endpoint': '/portals'})
        self.assertIn('portal directory', text)
        self.assertIn('full verified portal list', text)

    def test_parse_failure_retains_operation_and_protocol(self):
        env, _ = mixed_failures()
        diag = json.loads(diagnostics_document(env))['diagnostics'][1]
        for key, value in {'endpoint': '/asset_modules', 'endpoint_name': 'asset_modules',
                           'module': 'assets', 'portal_id': '7', 'http_status': 200,
                           'response_format': 'json_object', 'content_type': 'application/json',
                           'parse_reason': 'MISSING_COLLECTION_WRAPPER'}.items():
            self.assertEqual(diag[key], value, key)
        self.assertEqual(diag['api_codes'], [2000])
        self.assertTrue(diag['has_sdp_status'])
        self.assertEqual(diag['response_shape']['expected_wrapper'], 'all_product_types')
        self.assertEqual(diag['response_shape']['recognized_root_types']['modules'], 'array')
        self.assertNotIn('sign-in', diag['next_step'])

    def test_unknown_wrapper_is_not_guessed_or_accepted_as_empty(self):
        env, _ = mixed_failures()
        ds = env.portals['7'].snapshot.datasets['asset_modules']
        self.assertEqual(ds.outcome, 'PARSE_ERROR')
        self.assertFalse(ds.list_complete)
        self.assertIsNone(ds.coverage()['records_observed'])

    def test_explicit_is_not_automatic_or_directory_complete(self):
        env, _ = mixed_failures()
        topology = json.loads(diagnostics_document(env))['topology']
        self.assertEqual(topology['selection_source'], 'explicit')
        self.assertEqual(topology['directory_outcome'], 'NOT_ATTEMPTED')
        self.assertFalse(topology['directory_complete'])
        self.assertTrue(topology['complete'])  # retained selection-complete compatibility
        self.assertEqual(topology['complete_scope'], 'explicit_selection')
        self.assertEqual(topology['portals_discovered'], 0)
        self.assertEqual(topology['portals_supplied'], 1)

    def test_all_report_formats_keep_context_without_content(self):
        env, _ = mixed_failures()
        assessment = analyze_environment(env)
        documents = render_report_documents(assessment)
        documents['diagnostics.json'] = diagnostics_document(env)
        for name, text in documents.items():
            self.assertNotIn(PRIVATE, text, name)
            self.assertNotIn(SECRET, text, name)
        data = json.loads(documents['assessment.json'])
        diag = next(item for item in data['diagnostics'] if item.get('parse_reason'))
        self.assertEqual(diag['endpoint'], '/asset_modules')
        self.assertIn('response_shape', diag)
        self.assertIn('Operation-specific next step', documents['report.html'])
        self.assertIn('MISSING_COLLECTION_WRAPPER', documents['report.md'].replace('\\_', '_'))
        self.assertEqual(data['settings']['count_policy'], 'first')

    def test_only_get_headers_and_one_scheduler(self):
        _, opener = mixed_failures()
        self.assertEqual(len(opener.calls), 7)
        for _, request, _ in opener.calls:
            self.assertEqual(request.get_method(), 'GET')
            self.assertIsNone(request.data)
            self.assertEqual(request.get_header('Portalid'), '7')
            self.assertNotIn(SECRET, request.full_url)
        times = [item[0] for item in opener.calls]
        self.assertTrue(all(b-a >= 2 for a,b in zip(times, times[1:])))

    def test_diagnostics_include_global_and_field_failures(self):
        env, _ = mixed_failures()
        env.global_snapshot = Snapshot(env.generated_at, {}, {})
        env.global_snapshot.datasets['orgusers'] = Dataset('orgusers', '/orgusers', scope='environment',
            diagnostics=[{'classification': 'PERMISSION_DENIED'}])
        env.portals['7'].snapshot.fields['assets'] = {'diagnostics': [
            {'classification': 'ENDPOINT_UNSUPPORTED', 'endpoint': '/asset_servers/_metainfo',
             'endpoint_name': 'fields.assets', 'module': 'assets', 'portal_id': '7', 'message_sanitized': True}]}
        data = json.loads(diagnostics_document(env))
        self.assertTrue(any(d['endpoint_name'] == 'orgusers' for d in data['diagnostics']))
        self.assertTrue(any(d['endpoint_name'] == 'fields.assets' for d in data['diagnostics']))

    def test_safe_dynamic_metadata_path_retained(self):
        d = safe_diagnostic({'classification': 'PARSE_ERROR', 'endpoint': '/custom_asset_desks/_metainfo',
                             'endpoint_name': 'fields.assets', 'module': 'assets', 'message_sanitized': True})
        self.assertEqual(d['endpoint'], '/custom_asset_desks/_metainfo')
        self.assertIsNone(safe_diagnostic({**d, 'endpoint': '/custom_asset_desks/_download'})['endpoint'])

    def test_unknown_raw_logical_names_not_printed(self):
        d = safe_diagnostic({'endpoint_name': PRIVATE, 'module': PRIVATE, 'message_sanitized': True})
        self.assertNotIn(PRIVATE, json.dumps(d))

    def test_sanitized_shape_rejects_injected_names_and_values(self):
        raw = {PRIVATE: PRIVATE, 'all_product_types': PRIVATE, 'list_info': {'total_count': PRIVATE, PRIVATE: PRIVATE}}
        evidence = shape_evidence(raw, 'all_product_types')
        self.assertNotIn(PRIVATE, json.dumps(evidence))
        self.assertEqual(evidence['expected_wrapper_type'], 'string')
        self.assertEqual(evidence['other_root_key_count'], 1)
        evidence['recognized_root_types'][PRIVATE] = 'string'
        evidence['list_info_types']['total_count'] = PRIVATE
        evidence['raw_body'] = PRIVATE
        self.assertNotIn(PRIVATE, json.dumps(safe_shape(evidence)))

    def test_json_parse_guidance_does_not_assume_login_page(self):
        d = {'classification': 'PARSE_ERROR', 'response_format': 'json_object', 'endpoint': '/asset_modules'}
        self.assertNotIn('sign-in', guidance(d))
        self.assertIn('collector contract', guidance(d))

    def test_html_guidance_is_only_for_observed_html(self):
        d = {'classification': 'PARSE_ERROR', 'response_format': 'html', 'endpoint': '/users'}
        self.assertIn('sign-in/proxy', guidance(d))
        self.assertNotIn('No successful SDP', guidance(d, authentication='VALID'))

    def test_different_directory_credential_not_marked_authenticated_by_modules(self):
        d = {'classification': 'NETWORK_ERROR', 'transport_detail': 'CONNECTION_TIMED_OUT',
             'endpoint': '/portals', 'credential_scope': 'directory_key'}
        self.assertNotIn('Other successful reads', guidance(d, authentication='VALID'))

    def test_detail_mismatch_has_exact_detail_path(self):
        client, _, _ = make_client([ok('users', [{'id': '1'}]), ok('user', {'id': '2'})])
        spec = SPECS['users']; portal = PortalInfo('7','Synthetic')
        snapshot = Snapshot('2026-10-14', {'portal_id': '7'}, {})
        collector = Collector(PortalClient(client, portal, [spec]), [spec], CollectionOptions(detail_limit=1))
        collector.prepare(snapshot); collector.read_page(snapshot, 'users')
        list(collector.detail_steps(snapshot))
        d = safe_diagnostic(snapshot.datasets['users'].diagnostics[-1])
        self.assertEqual(d['endpoint'], '/users/1')
        self.assertEqual(d['http_status'], 200)
        self.assertEqual(d['parse_reason'], 'DETAIL_ENTITY_OR_ID_MISMATCH')

    def test_no_stale_protocol_evidence_from_another_operation(self):
        client = FakeClient([{'all_product_types': None}])
        client.last_response = {'endpoint': '/projects', 'http_status': 403, 'api_codes': [4002]}
        collector = Collector(client, [SPECS['asset_modules']])
        snapshot = Snapshot('2026-10-14', {'portal_id': '7'}, {})
        collector.prepare(snapshot);collector.read_page(snapshot,'asset_modules')
        d = snapshot.datasets['asset_modules'].diagnostics[-1]
        self.assertIsNone(d['http_status']);self.assertEqual(d['api_codes'], [])
        self.assertEqual(d['endpoint'], '/asset_modules')


class CountPolicyTests(unittest.TestCase):
    def collect(self, responses, policy='first', page_size=1):
        client = FakeClient(responses)
        snapshot = Snapshot('2026-10-14', {}, {})
        collector = Collector(client,[SPEC],CollectionOptions(page_size=page_size,max_records=0,subresource_parents=0,count_policy=policy))
        collector.prepare(snapshot)
        while collector.read_page(snapshot, 'requests'):
            pass
        return snapshot.datasets['requests'],client

    def test_default_count_only_on_first_page(self):
        ds,c = self.collect([page([1],True,2),page([2],False)])
        flags = [json.loads(params['input_data'])['list_info']['get_total_count'] for _,params in c.calls]
        self.assertEqual(flags,[True,False]);self.assertTrue(ds.list_complete)
        self.assertEqual(ds.total_count,2);self.assertEqual(ds.total_count_page,1)

    def test_never_counts_but_still_paginates(self):
        ds,c = self.collect([page([1],True),page([2],False)],'never')
        self.assertTrue(all(not json.loads(p['input_data'])['list_info']['get_total_count'] for _,p in c.calls))
        self.assertTrue(ds.list_complete);self.assertIsNone(ds.total_count)

    def test_always_restores_previous_query_policy(self):
        ds,c = self.collect([page([1],True,2),page([2],False,2)],'always')
        self.assertTrue(all(json.loads(p['input_data'])['list_info']['get_total_count'] for _,p in c.calls))
        self.assertTrue(ds.list_complete);self.assertEqual(ds.total_count_page,2)

    def test_old_count_cannot_terminate_page_without_continuation_evidence(self):
        ds,c = self.collect([page([1],True,2),{'requests':[{'id':'2'}]}])
        self.assertFalse(ds.list_complete)
        self.assertEqual(ds.diagnostics[-1]['parse_reason'],'PAGINATION_TERMINATION_MISSING')
        self.assertEqual(len(c.calls),2)

    def test_initial_count_conflict_is_not_certified_complete(self):
        ds,_ = self.collect([page([1],True,3),page([2],False)])
        self.assertFalse(ds.list_complete)
        self.assertEqual(ds.diagnostics[-1]['parse_reason'],'TOTAL_COUNT_CONFLICT')

    def test_record_limit_preserves_first_count(self):
        client=FakeClient([page([1],True,1000000)])
        snapshot=Snapshot('2026-10-14',{}, {})
        collector=Collector(client,[SPEC],CollectionOptions(max_records=1,subresource_parents=0))
        collector.prepare(snapshot);collector.read_page(snapshot,'requests')
        ds=snapshot.datasets['requests']
        self.assertEqual(ds.outcome,'RECORD_LIMIT_REACHED')
        self.assertEqual(ds.coverage()['api_reported_total_page'],1)

    def test_invalid_policies_fail_locally(self):
        for policy in ('yes',None,42):
            with self.assertRaises(ValueError):CollectionOptions(count_policy=policy)

    def test_cli_count_policy_is_validated_and_applied(self):
        for policy in ('first','never','always'):
            settings=_cli_options(_cli_parser().parse_args(['--count-policy',policy]))
            self.assertEqual(settings['count_policy'],policy)
            self.assertEqual(settings['rpm'],30)
        self.assertEqual(_cli_options(_cli_parser().parse_args([]))['count_policy'],'first')

    def test_empty_without_count_is_still_successfully_empty(self):
        ds,_=self.collect([page([],False)],'never')
        self.assertEqual(ds.outcome,'EMPTY');self.assertTrue(ds.list_complete)

    def test_malformed_wrapper_remains_unknown_not_empty(self):
        for rows in ('not a list',[9],None):
            ds,_=self.collect([{'requests':rows,'list_info':{'has_more_rows':False}}],'never')
            self.assertEqual(ds.outcome,'PARSE_ERROR');self.assertIsNone(ds.coverage()['records_observed'])

    def test_two_portals_share_one_scheduler_and_independent_first_counts(self):
        client,opener,_=make_client([ok('requests',[{'id':'1'}],True),ok('requests',[{'id':'2'}],True),
                                   ok('requests',[{'id':'3'}]),ok('requests',[{'id':'4'}])])
        collectors=[]
        for pid in ['7','11']:
            snap=Snapshot('2026-10-14',{'portal_id':pid},{})
            c=Collector(PortalClient(client,PortalInfo(pid,'Synthetic'),[SPEC]),[SPEC],CollectionOptions(page_size=1,max_records=0))
            c.prepare(snap);collectors.append((c,snap))
        for _ in range(2):
            for c,snap in collectors:c.read_page(snap,'requests')
        self.assertEqual([t for t,_,_ in opener.calls],[0,2,4,6])
        flags=[json.loads(parse_qs(urlsplit(r.full_url).query)['input_data'][0])['list_info']['get_total_count'] for _,r,_ in opener.calls]
        self.assertEqual(flags,[True,True,False,False])
        self.assertTrue(all(s.datasets['requests'].list_complete for _,s in collectors))


if __name__ == '__main__':
    unittest.main()
