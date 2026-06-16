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


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_network
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosNetworkModule(TestNiosModule):

    module = nios_network

    def setUp(self):
        super(TestNiosNetworkModule, self).setUp()
        self.module = MagicMock(
            name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_network.WapiModule'
        )
        self.module.check_mode = False
        self.module.params = {'provider': None}
        self.mock_wapi = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_network.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch(
            'ansible_collections.infoblox.nios_modules.plugins.modules.nios_network.WapiModule.run'
        )
        self.load_config = self.mock_wapi_run.start()

    def tearDown(self):
        super(TestNiosNetworkModule, self).tearDown()
        self.mock_wapi.stop()
        self.mock_wapi_run.stop()

    def load_fixtures(self, commands=None):
        self.exec_command.return_value = (0, load_fixture('nios_result.txt').strip(), None)
        self.load_config.return_value = dict(diff=None, session='session')

    def _get_wapi(self, test_object):
        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(name='get_object', return_value=test_object)
        wapi.create_object = Mock(name='create_object')
        wapi.update_object = Mock(name='update_object')
        wapi.delete_object = Mock(name='delete_object')
        return wapi

    def test_nios_network_ipv4_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'network': '192.168.10.0/24',
                              'comment': None, 'extattrs': None, 'use_logic_filter_rules': False,
                              'logic_filter_rules': []}

        test_object = None
        test_spec = {
            "network": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'network': '192.168.10.0/24'})

    def test_nios_network_ipv4_dhcp_update(self):
        self.module.params = {'provider': None, 'state': 'present', 'network': '192.168.10.0/24',
                              'comment': 'updated comment', 'extattrs': None}

        ref = "network/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "network": "192.168.10.0/24",
                "extattrs": {'options': {'name': 'test', 'value': 'ansible.com'}}
            }
        ]

        test_spec = {
            "network": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(ref, {'comment': 'updated comment', 'network': '192.168.10.0/24'})

    def test_nios_network_ipv6_dhcp_update(self):
        self.module.params = {'provider': None, 'state': 'present', 'ipv6network': 'fe80::/64',
                              'comment': 'updated comment', 'extattrs': None}

        ref = "ipv6network/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "ipv6network": "fe80::/64",
                "extattrs": {'options': {'name': 'test', 'value': 'ansible.com'}}
            }
        ]

        test_spec = {
            "ipv6network": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)
        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(ref, {'comment': 'updated comment', 'ipv6network': 'fe80::/64'})

    def test_nios_network_ipv4_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'network': '192.168.10.0/24',
                              'comment': None, 'extattrs': None}

        ref = "network/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "network": "192.168.10.0/24",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "network": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_network_ipv6_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'ipv6network': 'fe80::/64',
                              'comment': None, 'extattrs': None}

        test_object = None

        test_spec = {
            "ipv6network": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'ipv6network': 'fe80::/64'})

    def test_nios_network_ipv6_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'ipv6network': 'fe80::/64',
                              'comment': None, 'extattrs': None}

        ref = "ipv6network/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "ipv6network": "fe80::/64",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "ipv6network": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_networkcontainer_ipv4_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'networkcontainer': '192.168.10.0/24',
                              'comment': None, 'extattrs': None}

        test_object = None
        test_spec = {
            "networkcontainer": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'networkcontainer': '192.168.10.0/24'})

    def test_nios_networkcontainer_ipv4_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'networkcontainer': '192.168.10.0/24',
                              'comment': None, 'extattrs': None}

        ref = "networkcontainer/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "networkcontainer": "192.168.10.0/24"
        }]

        test_spec = {
            "networkcontainer": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_networkcontainer_ipv6_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'ipv6networkcontainer': 'fe80::/64',
                              'comment': None, 'extattrs': None}

        test_object = None
        test_spec = {
            "ipv6networkcontainer": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'ipv6networkcontainer': 'fe80::/64'})

    def test_nios_network_ipv4_create_with_use_logic_filter_rules(self):
        self.module.params = {'provider': None, 'state': 'present', 'network': '192.168.10.0/24',
                              'comment': None, 'extattrs': None, 'use_logic_filter_rules': True,
                              'logic_filter_rules': []}

        test_object = None
        test_spec = {
            "network": {"ib_req": True},
            "comment": {},
            "extattrs": {},
            "use_logic_filter_rules": {},
            "logic_filter_rules": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'network': '192.168.10.0/24',
                                                                  'use_logic_filter_rules': True,
                                                                  'logic_filter_rules': []
                                                                  }
                                                   )

    def test_nios_network_ipv4_update_with_use_logic_filter_rules(self):
        self.module.params = {'provider': None, 'state': 'present', 'network': '192.168.10.0/24',
                              'comment': 'updated comment', 'extattrs': None, 'use_logic_filter_rules': True,
                              'logic_filter_rules': []}

        ref = "network/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "network": "192.168.10.0/24",
                "extattrs": {'options': {'name': 'test', 'value': 'ansible.com'}},
                "use_logic_filter_rules": False,
                "logic_filter_rules": []
            }
        ]

        test_spec = {
            "network": {"ib_req": True},
            "comment": {},
            "extattrs": {},
            "use_logic_filter_rules": {},
            "logic_filter_rules": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(ref, {'network': '192.168.10.0/24',
                                                         'comment': 'updated comment',
                                                         'use_logic_filter_rules': True,
                                                         'logic_filter_rules': []}
                                                   )

    def test_nios_network_ipv4_create_with_vlan(self):
        self.module.params = {'provider': None, 'state': 'present', 'network': '192.168.10.0/24',
                              'comment': None, 'extattrs': None, 'vlans': [{'name': 'ansible_vlan',
                                                                            'parent': 'default', 'id': '10'}]}

        test_object = None
        test_spec = {
            "network": {"ib_req": True},
            "comment": {},
            "extattrs": {},
            "vlans": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('NIOS_IPV4_NETWORK', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with(
            'NIOS_IPV4_NETWORK',
            {
                'network': '192.168.10.0/24',
                'vlans': [
                    {
                        'name': 'ansible_vlan',
                        'parent': 'default',
                        'id': '10'
                    }
                ]
            }
        )

    def test_nios_network_ipv4_update_vlan(self):
        self.module.params = {'provider': None, 'state': 'present', 'network': '192.168.10.0/24',
                              'comment': None, 'extattrs': None, 'vlans': [{'name': 'ansible_vlan1',
                                                                            'parent': 'default', 'id': '10'},
                                                                           {'name': 'ansible_vlan2',
                                                                            'parent': 'default', 'id': '20'}]}
        ref = "network/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"

        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "network": "192.168.10.0/24",
                "vlans": [{'name': 'ansible_vlan1', 'parent': 'default', 'id': '10'}]
            }
        ]
        test_spec = {
            "network": {"ib_req": True},
            "comment": {},
            "extattrs": {},
            "vlans": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('NIOS_IPV4_NETWORK', test_spec)

        self.assertTrue(res['changed'])

        wapi.update_object.assert_called_once_with(
            ref,
            {
                'network': '192.168.10.0/24',
                'vlans': [
                    {
                        'name': 'ansible_vlan1',
                        'parent': 'default',
                        'id': '10'
                    },
                    {
                        'name': 'ansible_vlan2',
                        'parent': 'default',
                        'id': '20'
                    }
                ]
            }
        )

    def test_nios_network_ipv4_remove_vlan(self):
        self.module.params = {'provider': None, 'state': 'present', 'network': '192.168.10.0/24',
                              'comment': None, 'extattrs': None, 'vlans': []}
        ref = "network/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"

        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "network": "192.168.10.0/24",
                "vlans": [{'name': 'ansible_vlan1', 'parent': 'default', 'id': '10'},
                          {'name': 'ansible_vlan2', 'parent': 'default', 'id': '20'}
                          ]
            }
        ]
        test_spec = {
            "network": {"ib_req": True},
            "comment": {},
            "extattrs": {},
            "vlans": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('NIOS_IPV4_NETWORK', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(
            ref,
            {
                'network': '192.168.10.0/24',
                'vlans': []
            }
        )

    # ------------------------------------------------------------------
    # Issue #221: structural DHCP options (router/3, ntp-servers/42,
    # subnet-mask/1) must have use_option stripped before WAPI call.
    # ------------------------------------------------------------------

    def _make_module_for_options(self, options):
        """Return a MagicMock module whose params contains the given options list."""
        m = MagicMock()
        m.params = {'options': options}
        return m

    def test_check_vendor_specific_strips_router_by_num(self):
        # option num=3 (router) must have use_option removed
        opts = [{'num': 3, 'value': '192.168.10.1', 'use_option': True}]
        module = self._make_module_for_options(opts)
        ib_spec = {'options': {}}
        nios_network.check_vendor_specific_dhcp_option(module, ib_spec)
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_strips_ntp_servers_by_num(self):
        # option num=42 (ntp-servers) must have use_option removed
        opts = [{'num': 42, 'value': '10.0.0.1', 'use_option': True}]
        module = self._make_module_for_options(opts)
        ib_spec = {'options': {}}
        nios_network.check_vendor_specific_dhcp_option(module, ib_spec)
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_strips_subnet_mask_by_num(self):
        # option num=1 (subnet-mask) must have use_option removed
        opts = [{'num': 1, 'value': '255.255.255.0', 'use_option': True}]
        module = self._make_module_for_options(opts)
        ib_spec = {'options': {}}
        nios_network.check_vendor_specific_dhcp_option(module, ib_spec)
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_strips_router_by_name(self):
        # option name='router' must have use_option removed (no num supplied)
        opts = [{'name': 'router', 'value': '192.168.10.1', 'use_option': True}]
        module = self._make_module_for_options(opts)
        ib_spec = {'options': {}}
        nios_network.check_vendor_specific_dhcp_option(module, ib_spec)
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_strips_ntp_servers_by_name(self):
        # option name='ntp-servers' must have use_option removed
        opts = [{'name': 'ntp-servers', 'value': '10.0.0.1', 'use_option': True}]
        module = self._make_module_for_options(opts)
        ib_spec = {'options': {}}
        nios_network.check_vendor_specific_dhcp_option(module, ib_spec)
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_strips_subnet_mask_by_name(self):
        # option name='subnet-mask' must have use_option removed
        opts = [{'name': 'subnet-mask', 'value': '255.255.255.0', 'use_option': True}]
        module = self._make_module_for_options(opts)
        ib_spec = {'options': {}}
        nios_network.check_vendor_specific_dhcp_option(module, ib_spec)
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_preserves_use_option_for_domain_name_servers(self):
        # domain-name-servers (option 6) supports use_option; it must NOT be removed
        opts = [{'name': 'domain-name-servers', 'value': '8.8.8.8', 'use_option': True}]
        module = self._make_module_for_options(opts)
        ib_spec = {'options': {}}
        nios_network.check_vendor_specific_dhcp_option(module, ib_spec)
        self.assertIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_mixed_options(self):
        # router (stripped) and domain-name-servers (kept) in the same call
        opts = [
            {'name': 'router', 'value': '192.168.10.1', 'use_option': True},
            {'name': 'domain-name-servers', 'value': '8.8.8.8', 'use_option': True},
        ]
        module = self._make_module_for_options(opts)
        ib_spec = {'options': {}}
        nios_network.check_vendor_specific_dhcp_option(module, ib_spec)
        self.assertNotIn('use_option', module.params['options'][0])
        self.assertIn('use_option', module.params['options'][1])
