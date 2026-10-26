"""Synthetic regressions for the reported coverage gaps; no live source data."""
import contextlib
from dataclasses import replace
import http.client
import io
import json
import socket
import unittest

from sdp_audit.catalog import RESOURCES, FALLBACKS
from sdp_audit.collect import Collector, CollectionOptions
from sdp_audit.diagnostics import diagnostics_document, guidance, safe_diagnostic
from sdp_audit.environment import PortalClient
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.fields import FieldDiscovery, normalize_metainfo
from sdp_audit.models import Dataset, Snapshot, PortalInfo, PortalSnapshot, EnvironmentSnapshot
from sdp_audit.progress import print_environment_coverage
from sdp_audit.report import render_report_documents
from sdp_audit.synthetic import create_synthetic_client
from test_startup_and_publication import make_client
from test_transport import Response
from test_collect import FakeClient, page, SPEC

SPECS = {s.key: s for s in RESOURCES}


def response(wrapper, rows, more=False):
    return Response({'response_status': {'status_code': 2000, 'status': 'success'},
                     wrapper: rows, 'list_info': {'has_more_rows': more}})


def error(status, code):
    return Response({'response_status': {'status_code': code, 'status': 'failed'}}, status)


class CoverageRemediationTests(unittest.TestCase):
    def collect(self, key, responses, *, cap=0):
        client, opener, _ = make_client(responses, max_requests=40)
        spec = SPECS[key]
        snap = Snapshot('2026-10-26T12:00:00+00:00', {'portal_id': '7'}, {'max_requests': 40})
        collector = Collector(PortalClient(client, PortalInfo('7', 'Example'), [spec]), [spec],
            CollectionOptions(page_size=2, max_records=cap, subresource_parents=0), fallbacks=FALLBACKS)
        collector.prepare(snap)
        while collector.read_page(snap, key):
            pass
        return snap.datasets[key], client, opener

    def test_current_asset_module_wrapper_pages_and_preserves_ids(self):
        ds, _, opener = self.collect('asset_modules', [response('asset_modules', [
            {'id': '7', 'api_plural_name': 'asset_workstations'}], True),
            response('asset_modules', [{'id': '8', 'api_plural_name': 'asset_servers'}])])
        self.assertTrue(ds.list_complete)
        self.assertEqual(len(ds.records), 2)
        self.assertEqual(len(opener.calls), 2)
        self.assertEqual(ds.records[0]['api_plural_name'], 'asset_workstations')
        engine = FieldDiscovery(create_synthetic_client()[0], '7', 'Example', {
            'asset_modules': ds, 'assets': Dataset('assets', '/asset_assets', list_complete=True)})
        self.assertTrue(any(job.path == '/asset_workstations/_metainfo' for job in engine._jobs))

    def test_legacy_asset_wrapper_remains_supported_unknown_and_conflict_fail(self):
        ds, _, _ = self.collect('asset_modules', [response('all_product_types', [])])
        self.assertTrue(ds.list_complete)
        ds, _, _ = self.collect('asset_modules', [response('invented_wrapper', [])])
        self.assertEqual(ds.outcome, 'PARSE_ERROR')
        ds, _, _ = self.collect('asset_modules', [Response({'asset_modules': [{'id': '7'}], 'all_product_types': []})])
        self.assertEqual(ds.diagnostics[-1]['parse_reason'], 'CONFLICTING_COLLECTION_WRAPPERS')

    def test_modern_workstation_fallback_is_bounded_and_scoped_get(self):
        ds, _, opener = self.collect('computers', [error(404, 4007), response('asset_workstations', [{'id': '7'}])])
        self.assertTrue(ds.list_complete)
        self.assertEqual(ds.endpoint, '/asset_workstations')
        self.assertEqual(ds.diagnostics[0]['http_status'], 404)
        self.assertEqual(len(opener.calls), 2)
        for _, req, _ in opener.calls:
            self.assertEqual(req.get_method(), 'GET')
            self.assertIsNone(req.data)
            self.assertEqual(req.get_header('Portalid'), '7')

    def test_fallback_chain_preserves_server_failures_no_absence_inference(self):
        ds, _, opener = self.collect('computers', [error(404, 4007), error(404, 4007),
                                                           *[error(500, 4004) for _ in range(4)]])
        self.assertFalse(ds.list_complete)
        self.assertEqual(ds.outcome, 'SERVER_ERROR')
        self.assertEqual([d['http_status'] for d in ds.diagnostics], [404, 404, 500])
        self.assertEqual(len(opener.calls), 6)
        self.assertIn('administrator/vendor', guidance(ds.diagnostics[-1]))

    def test_permission_denial_never_triggers_computer_fallback(self):
        ds, _, opener = self.collect('computers', [error(403, 4002)])
        self.assertEqual(ds.outcome, 'PERMISSION_DENIED')
        self.assertEqual(len(opener.calls), 1)

    def test_mid_page_timeout_recovers_without_duplicate_records(self):
        ds, _, opener = self.collect('users', [response('users', [{'id': '7'}], True),
            socket.timeout('private exception text'), response('users', [{'id': '8'}])])
        self.assertTrue(ds.list_complete)
        self.assertEqual([r['id'] for r in ds.records], ['7', '8'])
        self.assertEqual(len(opener.calls), 3)

    def test_mid_page_timeout_exhaustion_keeps_lower_bound_and_detail(self):
        ds, _, _ = self.collect('users', [response('users', [{'id': '7'}], True),
                                                  *[socket.timeout('private') for _ in range(4)]])
        self.assertFalse(ds.list_complete)
        self.assertEqual(len(ds.records), 1)
        self.assertEqual(ds.diagnostics[-1]['transport_detail'], 'CONNECTION_TIMED_OUT')
        self.assertNotIn('private', json.dumps(ds.diagnostics))

    def test_incomplete_http_response_keeps_fixed_category_only(self):
        client, _, _ = make_client([http.client.IncompleteRead(b'private secret body') for _ in range(4)])
        from sdp_audit.transport import ApiError
        with self.assertRaises(ApiError) as error_info:
            client.get_json('/users', portal_id='7')
        diag = safe_diagnostic(error_info.exception.to_dict())
        self.assertEqual(diag['transport_detail'], 'HTTP_RESPONSE_INCOMPLETE')
        self.assertNotIn('private secret body', json.dumps(diag))

    def test_change_metadata_known_form_parses_without_saving_values(self):
        value = {'metainfo': {'fields': {'title': {'type': 'string', 'display_name': 'Title'},
            'udf_fields': {'type': 'udf', 'fields': {'udf_example': {
                'type': 'string', 'default_value': 'PRIVATE_DEFAULT', 'allowed_values': ['PRIVATE_OPTION']}}}}}}
        rows = normalize_metainfo(value, portal_id='7', portal_name='Example', module='changes', endpoint='/changes/metainfo')
        self.assertEqual(len(rows), 2)
        self.assertNotIn('PRIVATE_', json.dumps([r.to_dict() for r in rows]))

    def test_change_role_id_slots_are_schema_fields_not_free_text_names(self):
        role = {'id': '7', 'type': 'lookup', 'name': 'Example role with spaces', 'display_name': 'Example role'}
        value = {'metainfo': {'fields': {'roles': {'fields': {'7': role}}}}}
        fields = normalize_metainfo(value, portal_id='42', portal_name='Example', module='changes', endpoint='/changes/metainfo')
        self.assertEqual(fields[0].internal_name, 'role_7')
        self.assertEqual(fields[0].field_path, 'roles.7')
        self.assertEqual(fields[0].field_id, '7')
        from sdp_audit.fields import MetadataParseError
        for module, parent, wrong in [('requests', 'roles', role), ('changes', 'udf_fields', role),
                                      ('changes', 'roles', {**role, 'id': '8'})]:
            with self.assertRaises(MetadataParseError):
                normalize_metainfo({'metainfo': {'fields': {parent: {'fields': {'7': wrong}}}}},
                    portal_id='42', portal_name='Example', module=module, endpoint='/changes/metainfo')

    def test_change_metadata_failure_has_safe_structural_reason(self):
        from test_fields import FakeClient as FieldClient, execute, dataset
        client = FieldClient([{'metainfo': {'fields': {'udf_fields': {'type': 'udf'}}}}])
        engine = FieldDiscovery(client, '7', 'Example', {'changes': dataset([])})
        execute(engine)
        diag = engine.inventories['changes'].diagnostics[0]
        self.assertEqual(diag['parse_reason'], 'METADATA_UDF_FIELDS_MISSING')
        self.assertEqual(diag['response_shape']['recognized_root_types'], {'metainfo': 'object'})
        self.assertEqual(diag['response_format'], 'json_object')

    def child_snapshot(self, children):
        client = FakeClient(children)
        collector = Collector(client, [SPEC], CollectionOptions(subresource_parents=1))
        snapshot = Snapshot('2026-10-26T00:00:00+00:00', {'portal_id': '7'}, {})
        snapshot.datasets['requests'] = Dataset('requests', '/requests', records=[{'id': '7'}, {'id': '8'}], list_complete=True, portal_id='7')
        return snapshot, collector

    def test_empty_and_nonempty_child_samples_complete_but_not_population(self):
        for note_rows in ([], [{'id': '20'}]):
            snap, collector = self.child_snapshot([{'notes': note_rows, 'list_info': {'has_more_rows': False}},
                                                   {'tasks': [], 'list_info': {'has_more_rows': False}}])
            list(collector.child_steps(snap))
            for key in ('request_notes', 'request_tasks'):
                ds = snap.datasets[key]
                self.assertTrue(ds.sample_complete)
                self.assertFalse(ds.list_complete)
                self.assertEqual(ds.outcome, 'SAMPLE_COMPLETE')
                self.assertEqual(ds.sampled_parents, 1)
                self.assertEqual(ds.detail_succeeded, 1)

    def test_failed_child_sample_is_not_marked_complete(self):
        from sdp_audit.transport import ApiError
        snap, collector = self.child_snapshot([ApiError('forbidden', 'denied'),
            {'tasks': [], 'list_info': {'has_more_rows': False}}])
        list(collector.child_steps(snap))
        self.assertFalse(snap.datasets['request_notes'].sample_complete)
        self.assertNotEqual(snap.datasets['request_notes'].outcome, 'SAMPLE_COMPLETE')

    def test_console_and_reports_explain_sampling_caps_and_optional_scope(self):
        snap, collector = self.child_snapshot([
            {'notes': [], 'list_info': {'has_more_rows': False}},
            {'tasks': [], 'list_info': {'has_more_rows': False}}])
        list(collector.child_steps(snap))
        snap.datasets['users'] = Dataset('users', '/users', records=[{'id': '7'}],
            pages=1, outcome='RECORD_LIMIT_REACHED', portal_id='7', module='users')
        env = EnvironmentSnapshot(snap.generated_at, {'orgusers_collection': 'credential_missing'}, {})
        portal = PortalInfo('7', 'Example')
        env.topology.portals = [portal]
        env.portals['7'] = PortalSnapshot(portal, snap)
        text = io.StringIO()
        with contextlib.redirect_stdout(text):
            print_environment_coverage(env)
        self.assertIn('1/1 sampled parents complete', text.getvalue())
        self.assertIn('Row cap reached', text.getvalue())
        self.assertIn('Orguser access is optional', text.getvalue())
        documents = render_report_documents(analyze_environment(env))
        self.assertIn('sampled parents complete', documents['report.html'])
        self.assertIn('--restart-all', documents['report.md'])
        self.assertIn('sample_complete', documents['coverage.csv'])

    def test_cap_guidance_and_optional_scope_and_permission_guidance(self):
        ds, _, _ = self.collect('users', [response('users', [{'id': '7'}, {'id': '8'}], True)], cap=2)
        text = guidance({'classification': ds.outcome, 'endpoint': ds.endpoint})
        self.assertIn('--restart-all', text)
        self.assertIn('not the global HTTP budget', text)
        self.assertIn('Optional directory', guidance({'classification': 'CREDENTIAL_MISSING', 'endpoint': '/portals'}))
        self.assertIn('ESM Org', guidance({'classification': 'CREDENTIAL_MISSING', 'endpoint_name': 'orgusers', 'endpoint': '/orgusers'}))
        text = guidance({'classification': 'PERMISSION_DENIED', 'endpoint_name': 'projects', 'endpoint': '/projects'})
        self.assertIn('--retry-portals', text)
        self.assertNotIn('Project Admin', text)


if __name__ == '__main__':
    unittest.main()
