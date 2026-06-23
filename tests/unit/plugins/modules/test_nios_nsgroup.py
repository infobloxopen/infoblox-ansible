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


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_nsgroup
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosNSGroupModule(TestNiosModule):

    module = nios_nsgroup

    def setUp(self):

        super(TestNiosNSGroupModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_nsgroup.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}

        self.mock_wapi = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_nsgroup.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_nsgroup.WapiModule.run')

        self.load_config = self.mock_wapi_run.start()

        self.mock_check_type_dict = patch('ansible.module_utils.common.validation.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosNSGroupModule, self).tearDown()
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

    def test_nios_nsgroup_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'my-simple-group',
                              'comment': None, 'grid_primary': None}

        test_object = None
        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "grid_primary": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'name': 'my-simple-group'})

    def test_nios_nsgroup_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'my-simple-group',
                              'comment': None, 'grid_primary': None}

        ref = "nsgroup/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "name": "my-simple-group",
            "grid_primary": {'name': 'infoblox-test.example.com'}
        }]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "grid_primary": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)
        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_nsgroup_update_comment(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'default',
                              'comment': 'updated comment', 'grid_primary': None}

        ref = "nsgroup/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "default",
                "grid_primary": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "grid_primary": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(
            ref, {'comment': 'updated comment', 'name': 'default'}
        )

    # ------------------------------------------------------------------
    # Issue #59: removal from external_secondaries / external_primaries /
    # grid_primary / grid_secondaries must be detected as a change.
    # Also verifies that grid_primary/grid_secondaries transforms handle None.
    # ------------------------------------------------------------------

    def test_nios_nsgroup_external_secondaries_removal_detected(self):
        '''Removing one server from external_secondaries must trigger an update (issue #59).'''
        ref = "nsgroup/ZG5zLm5ldHdvcmtfdmlldyQw:test-group/false"
        self.module.params = {
            'provider': None, 'state': 'present', 'name': 'test-group',
            'comment': None, 'grid_primary': None, 'grid_secondaries': None,
            'external_primaries': None,
            'external_secondaries': [
                {'address': '1.1.1.1', 'name': 'server1.example.com', 'stealth': False},
            ],
            'is_grid_default': False, 'use_external_primary': False,
            'extattrs': None,
        }
        test_object = [{
            '_ref': ref,
            'name': 'test-group',
            'external_secondaries': [
                {'address': '1.1.1.1', 'name': 'server1.example.com', 'stealth': False},
                {'address': '9.9.9.9', 'name': 'server2.example.com', 'stealth': False},
            ],
        }]
        test_spec = {
            'name': {'ib_req': True},
            'comment': {},
            'external_secondaries': {'type': 'list'},
        }
        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)
        self.assertTrue(res['changed'])

    def test_nios_nsgroup_external_secondaries_no_change_not_updated(self):
        '''Identical external_secondaries (different order) must NOT trigger an update (issue #59).'''
        ref = "nsgroup/ZG5zLm5ldHdvcmtfdmlldyQw:test-group/false"
        self.module.params = {
            'provider': None, 'state': 'present', 'name': 'test-group',
            'comment': None, 'grid_primary': None, 'grid_secondaries': None,
            'external_primaries': None,
            'external_secondaries': [
                {'address': '9.9.9.9', 'name': 'server2.example.com', 'stealth': False},
                {'address': '1.1.1.1', 'name': 'server1.example.com', 'stealth': False},
            ],
            'is_grid_default': False, 'use_external_primary': False,
            'extattrs': None,
        }
        test_object = [{
            '_ref': ref,
            'name': 'test-group',
            'external_secondaries': [
                {'address': '1.1.1.1', 'name': 'server1.example.com', 'stealth': False},
                {'address': '9.9.9.9', 'name': 'server2.example.com', 'stealth': False},
            ],
        }]
        test_spec = {
            'name': {'ib_req': True},
            'comment': {},
            'external_secondaries': {'type': 'list'},
        }
        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)
        self.assertFalse(res['changed'])
        wapi.update_object.assert_not_called()

    def test_nios_nsgroup_grid_primary_transform_with_none_does_not_crash(self):
        '''grid_primary_preferred_transform must not crash when grid_primary is None (issue #59).'''
        self.module.params = {
            'provider': None, 'state': 'present', 'name': 'test-group',
            'comment': None, 'grid_primary': None, 'grid_secondaries': None,
            'external_primaries': None, 'external_secondaries': None,
            'is_grid_default': False, 'use_external_primary': False,
            'extattrs': None,
        }
        test_object = None
        test_spec = {
            'name': {'ib_req': True},
            'comment': {},
        }
        wapi = self._get_wapi(test_object)
        # Must not raise TypeError: 'NoneType' object is not iterable
        res = wapi.run('testobject', test_spec)
        self.assertTrue(res['changed'])
