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


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_dtc_monitor_tcp
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosDtcTcpMonitorModule(TestNiosModule):

    module = nios_dtc_monitor_tcp

    def setUp(self):
        super(TestNiosDtcTcpMonitorModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_dtc_monitor_tcp.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}
        self.mock_wapi = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_dtc_monitor_tcp.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_dtc_monitor_tcp.WapiModule.run')
        self.load_config = self.mock_wapi_run.start()
        self.mock_check_type_dict = patch('ansible.module_utils.common.validation.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosDtcTcpMonitorModule, self).tearDown()
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

    def test_nios_dtc_monitor_tcp_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'tcp_monitor',
                              'port': 8080, 'comment': None, 'extattrs': None}

        test_object = None

        test_spec = {
            "name": {"ib_req": True},
            "port": {},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'name': 'tcp_monitor',
                                                                  'port': 8080})

    def test_nios_dtc_monitor_tcp_update_comment(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'tcp_monitor',
                              'comment': 'updated comment', 'extattrs': None}

        ref = "dtc:monitor:tcp/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "tcp_monitor",
                "port": 8080,
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
        wapi.update_object.assert_called_once_with(ref, {'comment': 'updated comment', 'name': 'tcp_monitor'})

    def test_nios_dtc_monitor_tcp_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'tcp_monitor',
                              'comment': None, 'extattrs': None}

        ref = "dtc:monitor:tcp/ZG5zLm5ldHdvcmtfdmlldyQw:default/false"

        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "tcp_monitor",
                "port": 8080,
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
