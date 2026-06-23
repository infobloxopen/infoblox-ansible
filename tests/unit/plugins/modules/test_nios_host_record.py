# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_host_record
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture
from .utils import set_module_args
from ansible_collections.infoblox.nios_modules.tests.unit.plugins.modules.utils import AnsibleExitJson


class TestNiosHostRecordModule(TestNiosModule):

    module = nios_host_record

    def setUp(self):

        super(TestNiosHostRecordModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_host_record.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}

        self.mock_wapi = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_host_record.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_host_record.WapiModule.run')

        self.load_config = self.mock_wapi_run.start()
        self.mock_check_type_dict = patch('ansible.module_utils.common.validation.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosHostRecordModule, self).tearDown()
        self.mock_wapi.stop()
        self.mock_check_type_dict.stop()

    def _get_wapi(self, test_object):
        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(name='get_object', return_value=test_object)
        wapi.create_object = Mock(name='create_object')
        wapi.update_object = Mock(name='update_object')
        wapi.delete_object = Mock(name='delete_object')
        return wapi

    def load_fixtures(self, commands=None):
        self.exec_command.return_value = (0, load_fixture('nios_result.txt').strip(), None)
        self.load_config.return_value = dict(diff=None, session='session')

    def test_nios_host_record_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible',
                              'comment': None, 'extattrs': None}

        test_object = None
        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'name': 'ansible'})

    def test_nios_host_record_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'ansible',
                              'comment': None, 'extattrs': None}

        ref = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

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

    def test_nios_host_record_update_comment(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'default',
                              'comment': 'updated comment', 'extattrs': None}

        ref = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
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
        wapi.update_object.assert_called_once_with(
            ref, {'comment': 'updated comment', 'name': 'default'}
        )

    def test_nios_host_record_update_record_name(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': {'new_name': 'default', 'old_name': 'old_default'},
                              'comment': 'comment', 'extattrs': None}

        ref = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "old_default",
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
        wapi.update_object.assert_called_once_with(
            ref, {'comment': 'comment', 'name': 'default'}
        )

    def test_main_excludes_dns_ea_inheritance_for_unsupported_wapi(self):
        """main() must strip use_dns_ea_inheritance from the spec passed to
        wapi.run when the provider WAPI version does not support it."""
        from ansible_collections.infoblox.nios_modules.plugins.module_utils.api import WapiModule as RealWapiModule
        self.exec_command.provider_spec = RealWapiModule.provider_spec
        set_module_args({
            'name': 'host.ansible.com',
            'state': 'present',
            'provider': {'host': '192.168.1.1', 'username': 'admin', 'password': 'admin',
                         'wapi_version': '2.12'},
        })
        with self.assertRaises(AnsibleExitJson):
            nios_host_record.main()
        called_spec = self.exec_command.return_value.run.call_args[0][1]
        self.assertNotIn('use_dns_ea_inheritance', called_spec)

    def test_main_includes_dns_ea_inheritance_for_supported_wapi(self):
        """main() must keep use_dns_ea_inheritance in the spec passed to
        wapi.run when the provider WAPI version supports it."""
        from ansible_collections.infoblox.nios_modules.plugins.module_utils.api import WapiModule as RealWapiModule
        self.exec_command.provider_spec = RealWapiModule.provider_spec
        set_module_args({
            'name': 'host.ansible.com',
            'state': 'present',
            'provider': {'host': '192.168.1.1', 'username': 'admin', 'password': 'admin',
                         'wapi_version': '2.12.3'},
        })
        with self.assertRaises(AnsibleExitJson):
            nios_host_record.main()
        called_spec = self.exec_command.return_value.run.call_args[0][1]
        self.assertIn('use_dns_ea_inheritance', called_spec)

    def test_supports_dns_ea_inheritance_version_rules(self):
        # 3-part versions
        self.assertFalse(nios_host_record.supports_dns_ea_inheritance('2.12.2'))
        self.assertFalse(nios_host_record.supports_dns_ea_inheritance('2.13.3'))
        self.assertTrue(nios_host_record.supports_dns_ea_inheritance('2.12.3'))
        self.assertTrue(nios_host_record.supports_dns_ea_inheritance('2.13.4'))
        self.assertTrue(nios_host_record.supports_dns_ea_inheritance('2.14.0'))
        self.assertTrue(nios_host_record.supports_dns_ea_inheritance('3.0.0'))
        # 2-part versions — patch defaults to 0 (main fix for this comment)
        self.assertFalse(nios_host_record.supports_dns_ea_inheritance('2.12'))   # 2.12.0 < 2.12.3
        self.assertFalse(nios_host_record.supports_dns_ea_inheritance('2.13'))   # 2.13.0 < 2.13.4
        self.assertTrue(nios_host_record.supports_dns_ea_inheritance('2.14'))    # minor > 13
        self.assertTrue(nios_host_record.supports_dns_ea_inheritance('3.0'))     # major > 2
        # edge cases
        self.assertFalse(nios_host_record.supports_dns_ea_inheritance('2'))      # only 1 part
        self.assertFalse(nios_host_record.supports_dns_ea_inheritance('bad'))    # non-numeric

    def test_warn_ignored_dns_ea_inheritance_on_unsupported_wapi(self):
        self.assertTrue(nios_host_record.should_warn_ignored_dns_ea_inheritance('2.12', True))
        self.assertFalse(nios_host_record.should_warn_ignored_dns_ea_inheritance('2.12', False))
        self.assertFalse(nios_host_record.should_warn_ignored_dns_ea_inheritance('2.12.3', True))

    # ------------------------------------------------------------------
    # Tests for issue #115: exclude parameter in inline nios_next_ip
    # ------------------------------------------------------------------

    def _get_wapi_with_connector(self):
        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(name='get_object', return_value=None)
        wapi.create_object = Mock(name='create_object')
        wapi.update_object = Mock(name='update_object')
        wapi.delete_object = Mock(name='delete_object')
        wapi.connector = MagicMock()
        # Make fail_json raise so execution stops after the first error, matching
        # real Ansible module behaviour.
        self.module.fail_json.side_effect = SystemExit(1)
        return wapi

    def test_allocate_next_ip_with_exclude_list(self):
        """_allocate_next_ip_with_exclude returns first IP from WAPI result."""
        network_ref = 'network/ZG5z:192.168.1.0/24/default'
        wapi = self._get_wapi_with_connector()
        wapi.connector.get_object.return_value = [{'_ref': network_ref}]
        wapi.connector.call_func.return_value = {'ips': ['192.168.1.5']}

        result = wapi._allocate_next_ip_with_exclude(
            '192.168.1.0/24', 'default', ['192.168.1.1', '192.168.1.2'], 'ipv4'
        )

        self.assertEqual(result, '192.168.1.5')
        wapi.connector.call_func.assert_called_once_with(
            'next_available_ip',
            network_ref,
            {'num': 1, 'exclude': ['192.168.1.1', '192.168.1.2']}
        )

    def test_allocate_next_ip_with_exclude_string_normalised_to_list(self):
        """A single IP string passed as exclude is normalised to a list."""
        network_ref = 'network/ZG5z:192.168.1.0/24/default'
        wapi = self._get_wapi_with_connector()
        wapi.connector.get_object.return_value = [{'_ref': network_ref}]
        wapi.connector.call_func.return_value = {'ips': ['192.168.1.2']}

        result = wapi._allocate_next_ip_with_exclude(
            '192.168.1.0/24', 'default', '192.168.1.1', 'ipv4'
        )

        self.assertEqual(result, '192.168.1.2')
        wapi.connector.call_func.assert_called_once_with(
            'next_available_ip',
            network_ref,
            {'num': 1, 'exclude': ['192.168.1.1']}
        )

    def test_allocate_next_ip_with_exclude_invalid_type_fails(self):
        """A non-string, non-list exclude value causes fail_json."""
        wapi = self._get_wapi_with_connector()

        with self.assertRaises(SystemExit):
            wapi._allocate_next_ip_with_exclude(
                '192.168.1.0/24', 'default', 12345, 'ipv4'
            )

        self.assertTrue(self.module.fail_json.called)
        self.assertIn('exclude', self.module.fail_json.call_args[1]['msg'])

    def test_allocate_next_ip_network_not_found_fails(self):
        """fail_json is called when the network does not exist."""
        wapi = self._get_wapi_with_connector()
        wapi.connector.get_object.return_value = None

        with self.assertRaises(SystemExit):
            wapi._allocate_next_ip_with_exclude(
                '10.0.0.0/24', 'default', ['10.0.0.1'], 'ipv4'
            )

        self.assertTrue(self.module.fail_json.called)
        self.assertIn('not found', self.module.fail_json.call_args[1]['msg'])

    def test_check_if_nios_next_ip_exists_with_exclude_replaces_addr(self):
        """check_if_nios_next_ip_exists replaces nios_next_ip dict with concrete IP
        when exclude is present."""
        network_ref = 'network/ZG5z:192.168.10.0/24/default'
        wapi = self._get_wapi_with_connector()
        wapi.connector.get_object.return_value = [{'_ref': network_ref}]
        wapi.connector.call_func.return_value = {'ips': ['192.168.10.6']}

        proposed = {
            'ipv4addrs': [{
                'ipv4addr': "{'nios_next_ip': '192.168.10.0/24', 'exclude': ['192.168.10.1']}",
                'configure_for_dhcp': False,
            }],
            'view': 'default',
        }

        from ansible.module_utils.common.validation import check_type_dict as real_ctd
        self.mock_check_type_dict_obj.side_effect = real_ctd

        result = wapi.check_if_nios_next_ip_exists(proposed)

        self.assertEqual(result['ipv4addrs'][0]['ipv4addr'], '192.168.10.6')

    def test_check_if_nios_next_ip_exists_without_exclude_uses_func_string(self):
        """check_if_nios_next_ip_exists keeps func:nextavailableip string path
        when no exclude is given (backward compatibility)."""
        wapi = self._get_wapi_with_connector()

        proposed = {
            'ipv4addrs': [{
                'ipv4addr': "{'nios_next_ip': '192.168.10.0/24'}",
                'configure_for_dhcp': False,
            }],
            'view': 'default',
        }

        from ansible.module_utils.common.validation import check_type_dict as real_ctd
        self.mock_check_type_dict_obj.side_effect = real_ctd

        result = wapi.check_if_nios_next_ip_exists(proposed)

        addr = result['ipv4addrs'][0]['ipv4addr']
        self.assertTrue(addr.startswith('func:nextavailableip:'),
                        msg='Expected func:nextavailableip prefix, got: %s' % addr)
