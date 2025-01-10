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


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_extensible_attribute
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosExtensibleAttributeModule(TestNiosModule):

    module = nios_extensible_attribute

    def setUp(self):
        super(TestNiosExtensibleAttributeModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_extensible_attribute.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}
        self.mock_wapi = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_extensible_attribute.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_extensible_attribute.WapiModule.run')
        self.load_config = self.mock_wapi_run.start()
        self.mock_check_type_dict = patch('ansible.module_utils.common.validation.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosExtensibleAttributeModule, self).tearDown()
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

    def test_create_extensible_attribute(self):
        self.module.params = {
            'name': 'my_string',
            'type': 'STRING',
            'comment': 'Created by ansible',
            'state': 'present',
            'provider': None
        }

        test_object = None

        test_spec = {
            "name": {"ib_req": True},
            "type": {"ib_req": True},
            "comment": {},
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi.__dict__)
        res = wapi.run('testobject', test_spec)

        self.assertEqual(res['changed'], True)
        wapi.create_object.assert_called_once_with('testobject', {'name': 'my_string',
                                                                  'type': 'STRING',
                                                                  'comment': 'Created by ansible'})

    def test_nios_ea_update_comment(self):
        self.module.params = {
            'provider': None,
            'state': 'present',
            'name': 'testStringEA',
            'type': 'STRING',
            'flag': 'I',
            'default_value': 'test',
            'comment': 'Update comment'
        }

        ref = "extensibleattributedef/b25lLmV4dGVuc2libGVfYXR0cmlidXRlc19kZWYkLlRlcnJhZm9ybSBJbnRlcm5hbCBJRA:testStringEA"

        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "testStringEA",
                "flag": "I",
                "type": "STRING",
                "default_value": "test"
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "type": {"ib_req": True},
            "comment": {},
            "flag": {},
            "default_value": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)
        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(
            ref, {'comment': 'Update comment', 'type': 'STRING', 'name': 'testStringEA', 'flag': 'I', 'default_value': 'test'}
        )

    def test_remove_extensible_attribute(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'testStringEA', 'type': 'STRING',
                              'flag': None, 'default_value': None, 'comment': None}

        ref = "extensibleattributedef/b25lLmV4dGVuc2libGVfYXR0cmlidXRlc19kZWYkLlRlcnJhZm9ybSBJbnRlcm5hbCBJRA:testStringEA"

        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "testStringEA",
                "flag": "I",
                "type": "STRING",
                "default_value": "test"
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "type": {"ib_req": True},
            "comment": {},
            "flag": {},
            "default_value": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)
