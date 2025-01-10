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


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_adminuser
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosAdminUserModule(TestNiosModule):

    module = nios_adminuser

    def setUp(self):
        super(TestNiosAdminUserModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_adminuser.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}
        self.mock_wapi = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_adminuser.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_adminuser.WapiModule.run')
        self.load_config = self.mock_wapi_run.start()
        self.mock_check_type_dict = patch('ansible.module_utils.common.validation.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosAdminUserModule, self).tearDown()
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

    def test_nios_adminuser_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible_user',
                              'admin_groups': ['admin-group'], 'password': 'Pwd@1234',
                              'comment': None, 'extattrs': None}

        test_object = None

        test_spec = {
            "name": {"ib_req": True},
            "admin_groups": {"ib_req": True},
            "password": {},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi.__dict__)
        res = wapi.run('NIOS_ADMINUSER', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with(
            'NIOS_ADMINUSER',
            {
                'name': 'ansible_user',
                'admin_groups': ['admin-group'],
                'password': 'Pwd@1234'
            }
        )

    def test_nios_adminuser_update_comment(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible_user',
                              'admin_groups': ['admin-group'], 'comment': 'updated comment',
                              'extattrs': None}

        ref = "adminuser/ZG5zLm5ldHdvcmtfdmlldyQw:ansible_user"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "ansible_user",
                'admin_groups': ['admin-group'],
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "admin_groups": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('NIOS_ADMINUSER', test_spec)
        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(
            ref, {'comment': 'updated comment', 'admin_groups': ['admin-group'], 'name': 'ansible_user'}
        )

    def test_nios_adminuser_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'ansible_user',
                              'admin_groups': ['admin-group'], 'comment': None, 'extattrs': None}

        ref = "adminuser/ZG5zLm5ldHdvcmtfdmlldyQw:ansible_user"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "name": "ansible_user",
            "admin_groups": ['admin-group'],
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "name": {"ib_req": True},
            "admin_groups": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('NIOS_ADMINUSER', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_adminuser_update_record_name(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': {'new_name': 'ansible_new_user', 'old_name': 'ansible_user'},
                              'admin_groups': ['admin-group'], 'comment': 'comment', 'extattrs': None}

        ref = "adminuser/ZG5zLm5ldHdvcmtfdmlldyQw:ansible_new_user"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "ansible_user",
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "admin_groups": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('NIOS_ADMINUSER', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(ref, {'name': 'ansible_new_user', 'admin_groups': ['admin-group'],
                                                         'comment': 'comment'})

    def test_nios_adminuser_create_with_ssh_keys(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible_user', 'admin_groups': ['admin-group'],
                              'password': 'Pwd@1234', 'auth_method': 'KEYPAIR_PASSWORD', 'use_ssh_keys': True,
                              'ssh_keys': [{"key_name": "ansiblekey1", "key_type": "RSA", "key_value": "ssh-rsa AAAAB"}],
                              'comment': None, 'extattrs': None, 'disable': False, 'email': 'example@email.com'}

        test_object = None

        test_spec = {
            "name": {"ib_req": True},
            "admin_groups": {"ib_req": True},
            "password": {},
            "auth_method": {},
            "ssh_keys": {},
            "use_ssh_keys": {},
            "comment": {},
            "extattrs": {},
            "disable": {},
            "email": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi.__dict__)
        res = wapi.run('NIOS_ADMINUSER', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with(
            'NIOS_ADMINUSER',
            {
                'name': 'ansible_user',
                'admin_groups': ['admin-group'],
                'password': 'Pwd@1234',
                'auth_method': 'KEYPAIR_PASSWORD',
                'use_ssh_keys': True,
                'ssh_keys': [
                    {
                        'key_name': 'ansiblekey1',
                        'key_type': 'RSA',
                        'key_value': 'ssh-rsa AAAAB'
                    }
                ],
                'email': 'example@email.com',
                'disable': False
            }
        )

    def test_nios_adminuser_create_with_ca_cert(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible_user', 'admin_groups': ['admin-group'],
                              'password': 'Pwd@1234', 'enable_certificate_authentication': True, 'ca_certificate_issuer': 'CN="ib-root-ca"',
                              'client_certificate_serial_number': '123456789', 'use_time_zone': True, 'time_zone': 'UTC', 'comment': None,
                              'extattrs': None}

        test_object = None

        test_spec = {
            "name": {"ib_req": True},
            "admin_groups": {"ib_req": True},
            "password": {},
            "enable_certificate_authentication": {},
            "ca_certificate_issuer": {},
            "client_certificate_serial_number": {},
            "use_time_zone": {},
            "time_zone": {},
            "comment": {},
            "extattrs": {},
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi.__dict__)
        res = wapi.run('NIOS_ADMINUSER', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with(
            'NIOS_ADMINUSER',
            {
                'name': 'ansible_user',
                'admin_groups': ['admin-group'],
                'password': 'Pwd@1234',
                'enable_certificate_authentication': True,
                'ca_certificate_issuer': 'CN="ib-root-ca"',
                'client_certificate_serial_number': '123456789',
                'use_time_zone': True,
                'time_zone': 'UTC'
            }
        )
