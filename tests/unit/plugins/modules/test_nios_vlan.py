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


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_vlan
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosVlanModule(TestNiosModule):

    module = nios_vlan

    def setUp(self):
        super(TestNiosVlanModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_vlan.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}
        self.mock_wapi = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_vlan.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_vlan.WapiModule.run')
        self.load_config = self.mock_wapi_run.start()
        self.mock_check_type_dict = patch('ansible.module_utils.common.validation.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosVlanModule, self).tearDown()
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

    def test_nios_vlan_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible_vlan',
                              'parent': 'default', 'id': '10', 'comment': None, 'extattrs': None}

        test_object = None

        test_spec = {
            "name": {"ib_req": True},
            "parent": {"ib_req": True},
            "id": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi.__dict__)
        res = wapi.run('NIOS_VLAN', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with(
            'NIOS_VLAN',
            {
                'name': 'ansible_vlan',
                'parent': 'default',
                'id': '10'
            }
        )

    def test_nios_vlan_update_comment(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible_vlan',
                              'parent': 'default', 'id': '10', 'comment': 'updated comment',
                              'contact': 'contact@email.com', 'department': 'IT', 'description': 'test',
                              'reserved': True, 'extattrs': None}

        ref = "vlan/ZG5zLm5ldHdvcmtfdmlldyQw:ansible_vlan"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "ansible_vlan",
                "parent": "default",
                "id": "10",
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "parent": {"ib_req": True},
            "id": {"ib_req": True},
            "comment": {},
            "contact": {},
            "department": {},
            "description": {},
            "reserved": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('NIOS_VLAN', test_spec)
        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(
            ref, {'comment': 'updated comment', 'parent': 'default', 'id': '10', 'name': 'ansible_vlan',
                  'contact': 'contact@email.com', 'department': 'IT', 'description': 'test', 'reserved': True}
        )

    def test_nios_vlan_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'ansible_vlan',
                              'parent': 'default', 'id': '10', 'comment': None, 'extattrs': None}

        ref = "vlan/ZG5zLm5ldHdvcmtfdmlldyQw:ansible_vlan"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "name": "ansible_vlan",
            "parent": "default",
            "id": "10",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "name": {"ib_req": True},
            "parent": {"ib_req": True},
            "id": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('NIOS_VLAN', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_vlan_update_record_name(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': {'new_name': 'ansible_new_vlan', 'old_name': 'ansible_vlan'},
                              'parent': 'default', 'id': '10', 'comment': 'comment', 'extattrs': None}

        ref = "vlan/ZG5zLm5ldHdvcmtfdmlldyQw:ansible_new_vlan"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "ansible_vlan",
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "parent": {"ib_req": True},
            "id": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('NIOS_VLAN', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(ref, {'name': 'ansible_new_vlan', 'parent': 'default', 'id': '10',
                                                         'comment': 'comment'})
