# (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import copy
try:
    from ansible_collections.infoblox.nios_modules.tests.unit.compat import unittest
except ImportError:
    import unittest
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api


class TestNiosApi(unittest.TestCase):

    def setUp(self):
        super(TestNiosApi, self).setUp()

        self.module = MagicMock(name='AnsibleModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}

        self.mock_connector = patch('ansible_collections.infoblox.nios_modules.plugins.module_utils.api.get_connector')
        self.mock_connector.start()
        self.mock_check_type_dict = patch('ansible.module_utils.common.validation.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosApi, self).tearDown()

        self.mock_connector.stop()
        self.mock_check_type_dict.stop()

    def test_get_provider_spec(self):
        provider_options = ['host', 'username', 'password', 'cert', 'key', 'validate_certs', 'silent_ssl_warnings',
                            'http_request_timeout', 'http_pool_connections',
                            'http_pool_maxsize', 'max_retries', 'wapi_version', 'max_results']
        res = api.WapiBase.provider_spec
        self.assertIsNotNone(res)
        self.assertIn('provider', res)
        self.assertIn('options', res['provider'])
        returned_options = res['provider']['options']
        self.assertEqual(sorted(provider_options), sorted(returned_options.keys()))

    def _get_wapi(self, test_object):
        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(name='get_object', return_value=test_object)
        wapi.create_object = Mock(name='create_object')
        wapi.update_object = Mock(name='update_object')
        wapi.delete_object = Mock(name='delete_object')
        return wapi

    def test_wapi_no_change(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'default',
                              'comment': 'test comment', 'extattrs': None}

        test_object = [
            {
                "comment": "test comment",
                "_ref": "networkview/ZG5zLm5ldHdvcmtfdmlldyQw:default/true",
                "name": 'default',
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertFalse(res['changed'])

    def test_wapi_change(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'default',
                              'comment': 'updated comment', 'extattrs': None}
        ref = "networkview/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "default",
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(ref, {'comment': 'updated comment', 'name': 'default'})

    def test_wapi_change_false(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'default',
                              'comment': 'updated comment', 'extattrs': None, 'fqdn': 'foo'}
        ref = "networkview/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "default",
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "fqdn": {"ib_req": True, 'update': False},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(
            ref, {'comment': 'updated comment', 'name': 'default'}
        )

    def test_wapi_extattrs_change(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'default',
                              'comment': 'test comment', 'extattrs': {'Site': 'update'}}

        ref = "networkview/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "name": "default",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        kwargs = copy.deepcopy(test_object[0])
        kwargs['extattrs']['Site']['value'] = 'update'
        kwargs['name'] = 'default'
        del kwargs['_ref']

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(ref, kwargs)

    def test_wapi_extattrs_nochange(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'default',
                              'comment': 'test comment', 'extattrs': {'Site': 'test'}}

        ref = "networkview/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "name": "default",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertFalse(res['changed'])
        wapi.update_object.assert_not_called()

    def test_wapi_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible',
                              'comment': None, 'extattrs': None}

        test_object = None

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'name': 'ansible'})

    def test_wapi_delete(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'ansible',
                              'comment': None, 'extattrs': None}

        ref = "networkview/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "name": "ansible",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_wapi_strip_network_view(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible',
                              'comment': 'updated comment', 'extattrs': None,
                              'network_view': 'default'}

        test_object = [{
            "comment": "test comment",
            "_ref": "view/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/true",
            "name": "ansible",
            "extattrs": {},
            "network_view": "default"
        }]

        test_spec = {
            "name": {"ib_req": True},
            "network_view": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        kwargs = test_object[0].copy()
        ref = kwargs.pop('_ref')
        kwargs['comment'] = 'updated comment'
        kwargs['name'] = 'ansible'
        del kwargs['network_view']
        del kwargs['extattrs']

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(ref, kwargs)

    # ------------------------------------------------------------------
    # Issue #300: IPAM-only (non-DNS) host records carry view=' ' in WAPI.
    # The tests below cover the new view-handling paths in WapiModule.run()
    # and WapiModule.get_object_ref().
    # ------------------------------------------------------------------

    @staticmethod
    def _host_record_spec():
        return {
            "name": {"ib_req": True},
            "view": {"ib_req": True},
            "configure_for_dns": {"ib_req": True},
            "ipv4addrs": {},
            "comment": {},
            "extattrs": {},
        }

    def test_host_record_blank_view_omits_view_from_lookup(self):
        # User explicitly passes view=' ' (an IPAM-only host record's WAPI
        # marker). The lookup must be performed without 'view' in the
        # search filter so WAPI doesn't return 'View not found'.
        ref = "record:host/ZG5zLmhvc3QkLl9kZWZhdWx0Lmlwc28x:ipso-host/%20"
        ipam_only = {
            "_ref": ref, "name": "ipso-host", "view": " ",
            "configure_for_dns": False, "ipv4addrs": [], "extattrs": {},
        }
        self.module.params = {
            'provider': None, 'state': 'absent', 'name': 'ipso-host',
            'view': ' ', 'configure_for_dns': False,
            'ipv4addrs': None, 'comment': None, 'extattrs': None,
        }
        wapi = self._get_wapi([ipam_only])
        res = wapi.run(api.NIOS_HOST_RECORD, self._host_record_spec())

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)
        # The lookup filter passed to get_object must not contain 'view'
        # when the user-supplied view is blank/whitespace.
        called_filter = wapi.get_object.call_args[0][1]
        self.assertNotIn('view', called_filter)

    def test_host_record_default_view_retry_finds_ipam_only(self):
        # User runs state=absent without specifying view, so view defaults
        # to 'default'. The first lookup (view='default') returns nothing;
        # the retry without the view filter must find the IPAM-only record
        # (view=' ') and delete it.
        ref = "record:host/ZG5zLmhvc3QkLl9kZWZhdWx0Lmlwc28x:ipso-host/%20"
        ipam_only = {
            "_ref": ref, "name": "ipso-host", "view": " ",
            "configure_for_dns": False, "ipv4addrs": [], "extattrs": {},
        }
        responses = [[], [ipam_only]]
        self.module.params = {
            'provider': None, 'state': 'absent', 'name': 'ipso-host',
            'view': 'default', 'configure_for_dns': True,
            'ipv4addrs': None, 'comment': None, 'extattrs': None,
        }
        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(side_effect=responses)
        wapi.create_object = Mock()
        wapi.update_object = Mock()
        wapi.delete_object = Mock()

        res = wapi.run(api.NIOS_HOST_RECORD, self._host_record_spec())

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_host_record_default_view_retry_ignores_other_dns_views(self):
        # The retry path must NOT match records that live in a non-default
        # DNS view (view='external'); those are not IPAM-only records and
        # acting on them would be wrong. The module should treat the
        # absent operation as a no-op (changed=False).
        external_view_record = {
            "_ref": "record:host/abc:ipso-host/external",
            "name": "ipso-host", "view": "external",
            "configure_for_dns": True, "ipv4addrs": [], "extattrs": {},
        }
        responses = [[], [external_view_record]]
        self.module.params = {
            'provider': None, 'state': 'absent', 'name': 'ipso-host',
            'view': 'default', 'configure_for_dns': True,
            'ipv4addrs': None, 'comment': None, 'extattrs': None,
        }
        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(side_effect=responses)
        wapi.create_object = Mock()
        wapi.update_object = Mock()
        wapi.delete_object = Mock()

        res = wapi.run(api.NIOS_HOST_RECORD, self._host_record_spec())

        self.assertFalse(res['changed'])
        wapi.delete_object.assert_not_called()

    def test_host_record_blank_view_multiple_matches_fails(self):
        # If the IPAM-only name-only fallback search returns more than one
        # eligible (blank-view) record, the module must fail rather than
        # silently picking one.
        match_a = {
            "_ref": "record:host/a:ipso-host/%20",
            "name": "ipso-host", "view": " ",
            "configure_for_dns": False, "ipv4addrs": [], "extattrs": {},
        }
        match_b = {
            "_ref": "record:host/b:ipso-host/%20",
            "name": "ipso-host", "view": " ",
            "configure_for_dns": False, "ipv4addrs": [], "extattrs": {},
        }
        self.module.params = {
            'provider': None, 'state': 'absent', 'name': 'ipso-host',
            'view': ' ', 'configure_for_dns': False,
            'ipv4addrs': None, 'comment': None, 'extattrs': None,
        }
        wapi = self._get_wapi([match_a, match_b])
        self.module.fail_json.reset_mock()
        self.module.fail_json.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            wapi.run(api.NIOS_HOST_RECORD, self._host_record_spec())

        self.module.fail_json.assert_called_once()
        msg_kwargs = self.module.fail_json.call_args[1]
        self.assertIn('multiple IPAM-only host records', msg_kwargs.get('msg', ''))
        wapi.delete_object.assert_not_called()

    def test_host_record_configure_for_dns_false_filters_out_dns_records(self):
        # Legacy fallback: when configure_for_dns=False, the lookup falls
        # back to name-only even if view='default'. If a DNS-enabled host
        # with the same name exists in some view, name-only search returns
        # both. The module must filter out the DNS-enabled record and act
        # only on the IPAM-only one (configure_for_dns=False).
        ipam_only_ref = "record:host/a:ipso-host/%20"
        dns_record = {
            "_ref": "record:host/b:ipso-host/default",
            "name": "ipso-host", "view": "default",
            "configure_for_dns": True, "ipv4addrs": [], "extattrs": {},
        }
        ipam_only = {
            "_ref": ipam_only_ref, "name": "ipso-host", "view": " ",
            "configure_for_dns": False, "ipv4addrs": [], "extattrs": {},
        }
        self.module.params = {
            'provider': None, 'state': 'absent', 'name': 'ipso-host',
            'view': 'default', 'configure_for_dns': False,
            'ipv4addrs': None, 'comment': None, 'extattrs': None,
        }
        wapi = self._get_wapi([dns_record, ipam_only])

        res = wapi.run(api.NIOS_HOST_RECORD, self._host_record_spec())

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ipam_only_ref)

    # ------------------------------------------------------------------
    # Issue #135: nios_network state=absent should fall back to a viewless
    # lookup when the default network_view does not resolve the object.
    # If the fallback is ambiguous across multiple views, fail loudly.
    # ------------------------------------------------------------------

    def test_wapi_delete_network_without_network_view_falls_back(self):
        self.module.params = {
            'provider': None,
            'state': 'absent',
            'network': '192.0.2.0/24',
            'network_view': 'default',
        }

        ref = 'network/ZG5zLm5ldHdvcmtfdmlldyQw:issue135_ansible_view/false'

        test_spec = {
            'network': {'ib_req': True},
            'network_view': {'ib_req': True},
            'template': {},
        }

        wapi = self._get_wapi(None)
        # First lookup in default view misses, fallback without network_view finds object.
        wapi.get_object.side_effect = [[], [{'_ref': ref, 'network': '192.0.2.0/24'}]]

        res = wapi.run(api.NIOS_IPV4_NETWORK, test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)
        self.assertEqual(wapi.get_object.call_count, 2)
        first_filter = wapi.get_object.call_args_list[0][0][1]
        second_filter = wapi.get_object.call_args_list[1][0][1]
        self.assertIn('network_view', first_filter)
        self.assertNotIn('network_view', second_filter)

    def test_wapi_delete_network_without_network_view_fallback_ambiguous_fails(self):
        self.module.params = {
            'provider': None,
            'state': 'absent',
            'network': '192.0.2.0/24',
            'network_view': 'default',
        }

        test_spec = {
            'network': {'ib_req': True},
            'network_view': {'ib_req': True},
            'template': {},
        }

        wapi = self._get_wapi(None)
        wapi.get_object.side_effect = [
            [],
            [
                {'_ref': 'network/view1/false', 'network': '192.0.2.0/24', 'network_view': 'view1'},
                {'_ref': 'network/view2/false', 'network': '192.0.2.0/24', 'network_view': 'view2'},
            ],
        ]

        wapi.run(api.NIOS_IPV4_NETWORK, test_spec)

        msgs = [c[1].get('msg', '') for c in wapi.module.fail_json.call_args_list]
        self.assertTrue(
            any('Set network_view explicitly for state=absent' in m for m in msgs),
            "Expected fail_json to be called with the ambiguity message"
        )
        wapi.delete_object.assert_not_called()

    # ------------------------------------------------------------------
    # Issue #139: state=absent should be idempotent when the object is
    # already gone (NIOS returns NotFound). handle_exception must swallow
    # the exception for delete_object + state=absent only.
    # ------------------------------------------------------------------

    def test_wapi_handle_exception_delete_notfound_absent_is_ignored(self):
        self.module.params = {'provider': {}, 'state': 'absent'}
        self.module.fail_json = Mock(name='fail_json')

        wapi = api.WapiModule(self.module)
        exc = Exception('not found')
        exc.response = {
            'text': 'Reference record:a/... not found',
            'Error': 'AdmConDataNotFoundError: Reference not found',
            'code': 'Client.Ibap.Data.NotFound',
        }

        wapi.handle_exception('delete_object', exc)

        self.module.fail_json.assert_not_called()

    def test_wapi_handle_exception_delete_notfound_present_fails(self):
        self.module.params = {'provider': {}, 'state': 'present'}
        self.module.fail_json = Mock(name='fail_json')

        wapi = api.WapiModule(self.module)
        exc = Exception('not found')
        exc.response = {
            'text': 'Reference record:a/... not found',
            'Error': 'AdmConDataNotFoundError: Reference not found',
            'code': 'Client.Ibap.Data.NotFound',
        }

        wapi.handle_exception('delete_object', exc)

        self.module.fail_json.assert_called_once_with(
            msg='Reference record:a/... not found',
            type='AdmConDataNotFoundError',
            code='Client.Ibap.Data.NotFound',
            operation='delete_object',
        )

    # ------------------------------------------------------------------
    # handle_exception robustness against malformed exception responses.
    # Two real-world defects:
    #   * WapiModule did response['Error'].split(':') without a guard,
    #     raising KeyError if NIOS returned text without an Error key.
    #   * WapiLookup did 'text' in exc.response without a guard, raising
    #     AttributeError if exc.response was None.
    # ------------------------------------------------------------------

    def test_wapi_handle_exception_text_without_error_key_does_not_raise(self):
        '''WapiModule must not raise KeyError when response has text but no Error key.'''
        self.module.params = {'provider': {}, 'state': 'present'}
        self.module.fail_json = Mock(name='fail_json')

        wapi = api.WapiModule(self.module)
        exc = Exception('boom')
        exc.response = {'text': 'something broke', 'code': 'Client.Ibap.Some.Code'}

        # Must not raise — the bug was a KeyError on response['Error'].
        wapi.handle_exception('create_object', exc)

        self.module.fail_json.assert_called_once_with(
            msg='something broke',
            type='',
            code='Client.Ibap.Some.Code',
            operation='create_object',
        )

    def test_wapi_handle_exception_no_response_falls_back_to_native(self):
        '''WapiModule must fall back to to_native(exc) when exc.response is None.'''
        self.module.params = {'provider': {}, 'state': 'present'}
        self.module.fail_json = Mock(name='fail_json')

        wapi = api.WapiModule(self.module)
        exc = Exception('no response attached')
        exc.response = None  # explicit None — was the original AttributeError trigger

        wapi.handle_exception('create_object', exc)

        # When response is None we end up in the else-branch with to_native(exc).
        self.module.fail_json.assert_called_once()
        call_kwargs = self.module.fail_json.call_args[1]
        self.assertEqual(call_kwargs.get('msg'), 'no response attached')

    def test_wapi_lookup_handle_exception_none_response_does_not_raise(self):
        '''WapiLookup must not raise AttributeError when exc.response is None.'''
        # WapiLookup.__init__ requires a provider dict — pass an empty one.
        lookup = api.WapiLookup({})
        exc = Exception('lookup boom')
        exc.response = None

        # Must raise plain Exception (wrapping exc), NOT AttributeError.
        with self.assertRaises(Exception) as cm:
            lookup.handle_exception('get_object', exc)
        self.assertNotIsInstance(cm.exception, AttributeError)
        self.assertIn('lookup boom', str(cm.exception))

    def test_wapi_lookup_handle_exception_text_path(self):
        '''WapiLookup should raise Exception(text) when response has text.'''
        lookup = api.WapiLookup({})
        exc = Exception('original')
        exc.response = {'text': 'wapi said no'}

        with self.assertRaises(Exception) as cm:
            lookup.handle_exception('get_object', exc)
        self.assertEqual(str(cm.exception), 'wapi said no')

    # ------------------------------------------------------------------
    # Issue #223 — WapiInventory must surface a meaningful error.
    #
    # WapiInventory historically lacked handle_exception. Because
    # WapiBase.__getattr__ returns a partial for any non-underscore
    # attribute, hasattr(self, 'handle_exception') in _invoke_method was
    # always True, so the call got dispatched to the Connector producing the
    # misleading "'Connector' object has no attribute 'handle_exception'"
    # error instead of the real cause (bad credentials, unreachable host).
    # ------------------------------------------------------------------
    def test_wapi_inventory_has_handle_exception(self):
        '''WapiInventory must define its own handle_exception (issue #223).'''
        self.assertIn('handle_exception', api.WapiInventory.__dict__)

    def test_wapi_inventory_handle_exception_text_path(self):
        '''WapiInventory should raise Exception(text) when response has text.'''
        inventory = api.WapiInventory({})
        exc = Exception('original')
        exc.response = {'text': 'authentication failure'}

        with self.assertRaises(Exception) as cm:
            inventory.handle_exception('get_object', exc)
        self.assertNotIsInstance(cm.exception, AttributeError)
        self.assertEqual(str(cm.exception), 'authentication failure')

    def test_wapi_inventory_handle_exception_no_response_falls_back(self):
        '''WapiInventory must wrap exc when response is missing/None.'''
        inventory = api.WapiInventory({})
        exc = Exception('host unreachable')
        exc.response = None

        with self.assertRaises(Exception) as cm:
            inventory.handle_exception('get_object', exc)
        self.assertNotIsInstance(cm.exception, AttributeError)
        self.assertIn('host unreachable', str(cm.exception))

    def test_wapi_inventory_invoke_method_uses_handle_exception(self):
        '''An InfobloxException from a WAPI call must route through
        WapiInventory.handle_exception, not the Connector (issue #223).'''
        inventory = api.WapiInventory({})

        exc = api.InfobloxException(response={'text': 'bad credentials'})

        connector = MagicMock(name='Connector')
        connector.get_object.side_effect = exc
        inventory.connector = connector

        with self.assertRaises(Exception) as cm:
            inventory.get_object('record:host', {})
        # Must be the meaningful WAPI message, NOT the confusing AttributeError
        # about the Connector lacking handle_exception.
        self.assertNotIsInstance(cm.exception, AttributeError)
        self.assertEqual(str(cm.exception), 'bad credentials')

    # ------------------------------------------------------------------
    # convert_vlans_to_struct — direct unit tests for the new helper.
    # ------------------------------------------------------------------

    def test_convert_vlans_to_struct_strips_id_and_name(self):
        spec = {'vlans': [{'vlan': 'vlan/abc:10/default', 'id': 10, 'name': 'v10'}]}
        result = api.convert_vlans_to_struct(spec)
        self.assertEqual(result['vlans'], [{'vlan': 'vlan/abc:10/default'}])

    def test_convert_vlans_to_struct_filters_entries_without_vlan_key(self):
        spec = {'vlans': [{'vlan': 'vlan/abc:10/default'}, {'id': 99, 'name': 'orphan'}]}
        result = api.convert_vlans_to_struct(spec)
        self.assertEqual(result['vlans'], [{'vlan': 'vlan/abc:10/default'}])

    def test_convert_vlans_to_struct_no_key_unchanged(self):
        spec = {'network': '192.0.2.0/24'}
        result = api.convert_vlans_to_struct(spec)
        self.assertEqual(result, {'network': '192.0.2.0/24'})
        self.assertNotIn('vlans', result)

    def test_convert_vlans_to_struct_empty_list_unchanged(self):
        spec = {'vlans': []}
        result = api.convert_vlans_to_struct(spec)
        self.assertEqual(result['vlans'], [])

    # ------------------------------------------------------------------
    # verify_list_content_equality — direct unit tests for the new method,
    # plus an end-to-end auth_zones reorder test via compare_objects.
    # ------------------------------------------------------------------

    def test_verify_list_content_equality_same_order_returns_true(self):
        wapi = api.WapiModule(self.module)
        self.assertTrue(wapi.verify_list_content_equality([1, 2, 3], [1, 2, 3]))

    def test_verify_list_content_equality_different_order_returns_true(self):
        wapi = api.WapiModule(self.module)
        self.assertTrue(wapi.verify_list_content_equality([3, 1, 2], [1, 2, 3]))

    def test_verify_list_content_equality_dict_subset_match(self):
        '''Proposed dict items match if all entries are present in current item.'''
        wapi = api.WapiModule(self.module)
        proposed = [{'name': 'a'}, {'name': 'b'}]
        current = [{'name': 'b', '_ref': 'x'}, {'name': 'a', '_ref': 'y'}]
        self.assertTrue(wapi.verify_list_content_equality(proposed, current))

    def test_verify_list_content_equality_missing_item_returns_false(self):
        wapi = api.WapiModule(self.module)
        self.assertFalse(wapi.verify_list_content_equality([1, 2, 4], [1, 2, 3]))

    def test_verify_list_content_equality_different_lengths_returns_false(self):
        wapi = api.WapiModule(self.module)
        self.assertFalse(wapi.verify_list_content_equality([1, 2], [1, 2, 3]))

    def test_compare_objects_auth_zones_reorder_returns_true(self):
        '''auth_zones reorder must NOT register as a change (covered by verify_list_content_equality).'''
        wapi = api.WapiModule(self.module)
        proposed = {'auth_zones': ['zone:a/default', 'zone:b/default']}
        current = {'auth_zones': ['zone:b/default', 'zone:a/default']}
        self.assertTrue(wapi.compare_objects(current, proposed, ib_obj_type=api.NIOS_DTC_LBDN))

    def test_compare_objects_auth_zones_content_change_returns_false(self):
        '''auth_zones with different content must register as a change.'''
        wapi = api.WapiModule(self.module)
        proposed = {'auth_zones': ['zone:a/default', 'zone:b/default']}
        current = {'auth_zones': ['zone:a/default', 'zone:c/default']}
        self.assertFalse(wapi.compare_objects(current, proposed, ib_obj_type=api.NIOS_DTC_LBDN))

    # ------------------------------------------------------------------
    # IPv6 viewless delete-by-CIDR fallback — mirror of the IPv4 test for
    # NIOS_IPV6_NETWORK so the fallback path is covered for both stacks.
    # ------------------------------------------------------------------

    def test_wapi_delete_ipv6_network_without_network_view_falls_back(self):
        self.module.params = {
            'provider': None,
            'state': 'absent',
            'network': '2001:db8::/64',
            'network_view': 'default',
        }

        ref = 'ipv6network/ZG5zLm5ldHdvcmtfdmlldyQw:issue135_v6_view/false'

        test_spec = {
            'network': {'ib_req': True},
            'network_view': {'ib_req': True},
            'template': {},
        }

        wapi = self._get_wapi(None)
        wapi.get_object.side_effect = [[], [{'_ref': ref, 'network': '2001:db8::/64'}]]

        res = wapi.run(api.NIOS_IPV6_NETWORK, test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)
        self.assertEqual(wapi.get_object.call_count, 2)
        first_filter = wapi.get_object.call_args_list[0][0][1]
        second_filter = wapi.get_object.call_args_list[1][0][1]
        self.assertIn('network_view', first_filter)
        self.assertNotIn('network_view', second_filter)

    def test_post_fetch_filters_password_for_adminuser(self):
        # Post-write re-fetch should never request password in return_fields
        # because WAPI rejects adminuser GETs with return_fields+=password.
        self.module.params = {
            'provider': {}, 'state': 'present',
            'name': 'api-user', 'password': 'secret',
        }
        test_spec = {
            'name': {'ib_req': True},
            'password': {},
        }

        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(return_value=None)
        wapi.create_object = Mock(return_value='adminuser/test-ref')
        wapi.update_object = Mock()
        wapi.delete_object = Mock()
        wapi.connector.get_object = Mock(return_value={'_ref': 'adminuser/test-ref', 'name': 'api-user'})

        res = wapi.run(api.NIOS_ADMINUSER, test_spec)

        self.assertTrue(res['changed'])
        self.assertIn('object', res)
        called_kwargs = wapi.connector.get_object.call_args.kwargs
        self.assertIn('return_fields', called_kwargs)
        self.assertNotIn('password', called_kwargs['return_fields'])

    def test_post_fetch_filters_members_and_vlans(self):
        # Post-write re-fetch must never include 'members' or 'vlans' in
        # return_fields because WAPI rejects network GETs with those fields.
        # Using a generic object type to avoid get_object_ref's network-specific
        # key manipulation; the exclusion is applied unconditionally by run().
        self.module.params = {
            'provider': {}, 'state': 'present',
            'network': '10.0.0.0/24', 'network_view': 'default',
            'members': [], 'vlans': [],
        }
        test_spec = {
            'network': {'ib_req': True},
            'network_view': {},
            'members': {},
            'vlans': {},
        }

        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(return_value=None)
        wapi.create_object = Mock(return_value='testnetwork/ZG5z:10.0.0.0/24/default')
        wapi.update_object = Mock()
        wapi.delete_object = Mock()
        wapi.connector.get_object = Mock(return_value={
            '_ref': 'testnetwork/ZG5z:10.0.0.0/24/default',
            'network': '10.0.0.0/24',
        })

        res = wapi.run('testnetwork', test_spec)

        self.assertTrue(res['changed'])
        self.assertIn('object', res)
        called_kwargs = wapi.connector.get_object.call_args.kwargs
        self.assertIn('return_fields', called_kwargs)
        self.assertNotIn('members', called_kwargs['return_fields'])
        self.assertNotIn('vlans', called_kwargs['return_fields'])

    def test_post_fetch_skipped_in_check_mode(self):
        # In check_mode the post-write re-fetch must never be attempted.
        self.module.check_mode = True
        self.module.params = {
            'provider': {}, 'state': 'present',
            'name': 'check-obj', 'comment': None, 'extattrs': None,
        }
        test_spec = {
            'name': {'ib_req': True},
            'comment': {},
            'extattrs': {},
        }

        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(return_value=None)
        wapi.create_object = Mock(return_value='testobject/check-ref')
        wapi.update_object = Mock()
        wapi.delete_object = Mock()
        wapi.connector.get_object = Mock()

        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.connector.get_object.assert_not_called()
        self.assertNotIn('object', res)

    def test_post_fetch_failure_emits_warning_not_exception(self):
        # When the post-fetch connector call raises, the module must emit a
        # warning instead of failing the task (the write already succeeded).
        self.module.params = {
            'provider': {}, 'state': 'present',
            'name': 'new-obj', 'comment': None, 'extattrs': None,
        }
        test_spec = {
            'name': {'ib_req': True},
            'comment': {},
            'extattrs': {},
        }

        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(return_value=None)
        wapi.create_object = Mock(return_value='testobject/new-ref')
        wapi.update_object = Mock()
        wapi.delete_object = Mock()
        wapi.connector.get_object = Mock(side_effect=Exception('connector error'))

        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        self.assertNotIn('object', res)
        self.module.warn.assert_called_once()
        warn_msg = self.module.warn.call_args[0][0]
        self.assertIn('post-fetch failed', warn_msg)
        self.assertIn('connector error', warn_msg)

    def test_check_mode_skips_update_in_add_ip_path(self):
        # In check_mode, the HOST_RECORD add-ip update_object call must be
        # suppressed, but result['changed'] must still be True.
        self.module.check_mode = True
        ref = 'record:host/ZG5z:myhost/default'
        self.module.params = {
            'provider': {}, 'state': 'present',
            'name': 'myhost', 'view': 'default',
            'configure_for_dns': True,
            'ipv4addrs': [{'ipv4addr': '10.0.0.2', 'add': True}],
            'comment': None, 'extattrs': None,
        }
        existing = [{
            '_ref': ref,
            'name': 'myhost', 'view': 'default',
            'configure_for_dns': True,
            'ipv4addrs': [{'ipv4addr': '10.0.0.1'}],
            'comment': None, 'extattrs': {},
        }]
        test_spec = {
            'name': {'ib_req': True},
            'view': {'ib_req': True},
            'configure_for_dns': {'ib_req': True},
            'ipv4addrs': {},
            'comment': {},
            'extattrs': {},
        }

        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(return_value=existing)
        wapi.create_object = Mock()
        wapi.update_object = Mock()
        wapi.delete_object = Mock()

        res = wapi.run(api.NIOS_HOST_RECORD, test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_not_called()

    def test_check_mode_skips_update_in_remove_ip_absent_path(self):
        # In check_mode, the HOST_RECORD remove-ip update_object call on
        # state=absent must be suppressed, but result['changed'] must be True.
        self.module.check_mode = True
        ref = 'record:host/ZG5z:myhost/default'
        self.module.params = {
            'provider': {}, 'state': 'absent',
            'name': 'myhost', 'view': 'default',
            'configure_for_dns': True,
            'ipv4addrs': [{'ipv4addr': '10.0.0.1', 'remove': True}],
            'comment': None, 'extattrs': None,
        }
        existing = [{
            '_ref': ref,
            'name': 'myhost', 'view': 'default',
            'configure_for_dns': True,
            'ipv4addrs': [{'ipv4addr': '10.0.0.1'}, {'ipv4addr': '10.0.0.2'}],
            'comment': None, 'extattrs': {},
        }]
        test_spec = {
            'name': {'ib_req': True},
            'view': {'ib_req': True},
            'configure_for_dns': {'ib_req': True},
            'ipv4addrs': {},
            'comment': {},
            'extattrs': {},
        }

        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(return_value=existing)
        wapi.create_object = Mock()
        wapi.update_object = Mock()
        wapi.delete_object = Mock()

        res = wapi.run(api.NIOS_HOST_RECORD, test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_not_called()
