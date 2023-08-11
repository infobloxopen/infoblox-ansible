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


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_dtc_topology
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosDtcTopologyModule(TestNiosModule):

    module = nios_dtc_topology

    def setUp(self):
        super(TestNiosDtcTopologyModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_dtc_topology.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}
        self.mock_wapi = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_dtc_topology.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_dtc_topology.WapiModule.run')
        self.mock_wapi_run.start()
        self.load_config = self.mock_wapi_run.start()
        self.mock_check_type_dict = patch('ansible.module_utils.common.validation.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosDtcTopologyModule, self).tearDown()
        self.mock_wapi.stop()
        self.mock_wapi_run.stop()
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

    def test_nios_dtc_topology_create(self):
        self.module.params = {
            'provider': None,
            'state': 'present',
            'name': 'a_topology',
            'rules': [{
                'dest_type': 'POOL',
                'destination_link': 'web_pool',
                'return_type': 'REGULAR'
            }],
            'comment': None,
            'extattrs': None
        }

        test_object = None

        test_spec = {
            "name": {"ib_req": True},
            "rules": {},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with(
            'testobject',
            {
                'name': 'a_topology',
                'rules': [{
                    'dest_type': 'POOL',
                    'destination_link': 'web_pool',
                    'return_type': 'REGULAR'
                }]
            }
        )

    def test_nios_dtc_topology_update_comment(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'a_topology',
                              'comment': 'updated comment', 'extattrs': None}

        test_object = [
            {
                '_ref': 'dtc:topology/ZG5zLm5ldHdvcmtfdmlldyQw:default/true',
                'name': 'a_topology',
                'rules': [{
                    '_ref': 'dtc:topology:rule/ZG5zLm5ldHdvcmtfdmlldyQw:a_topology/web_pool'
                }],
                'comment': "test comment",
                'extattrs': {}
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

    def test_nios_dtc_topology_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'a_topology',
                              'comment': None, 'extattrs': None}

        ref = "dtc:topology/ZG5zLm5ldHdvcmtfdmlldyQw:default/false"

        test_object = [
            {
                "comment": {},
                "_ref": ref,
                "name": "a_topology",
                'rules': [{
                    '_ref': 'dtc:topology:rule/ZG5zLm5ldHdvcmtfdmlldyQw:a_topology/web_pool'
                }],
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
        wapi.delete_object.assert_called_once_with(ref)
