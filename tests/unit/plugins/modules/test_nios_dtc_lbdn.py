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


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_dtc_lbdn
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosDtcLbdnModule(TestNiosModule):
    """Regression coverage for DTC LBDN pool ordering.

    Pool order is semantically significant for DTC LBDNs (determines priority/weight)
    so api.WapiModule.compare_objects must treat 'pools' as order-sensitive via
    verify_list_order — NOT as a set-equality check.
    """

    module = nios_dtc_lbdn

    def setUp(self):
        super(TestNiosDtcLbdnModule, self).setUp()
        self.module = MagicMock(
            name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_dtc_lbdn.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}
        self.mock_wapi = patch(
            'ansible_collections.infoblox.nios_modules.plugins.modules.nios_dtc_lbdn.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch(
            'ansible_collections.infoblox.nios_modules.plugins.modules.nios_dtc_lbdn.WapiModule.run')
        self.load_config = self.mock_wapi_run.start()

    def tearDown(self):
        super(TestNiosDtcLbdnModule, self).tearDown()
        self.mock_wapi.stop()
        self.mock_wapi_run.stop()

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

    def test_nios_dtc_lbdn_pools_same_order_no_change(self):
        """Re-run with pools in the same order MUST be idempotent (changed=False)."""
        self.module.params = {
            'provider': None, 'state': 'present', 'name': 'test_lbdn',
            'pools': [
                {'pool': 'pool1', 'ratio': 1},
                {'pool': 'pool2', 'ratio': 2},
            ],
            'comment': None, 'extattrs': None,
        }
        ref = "dtc:lbdn/ZG5zLm5ldHdvcmtfdmlld:test_lbdn"
        test_object = [{
            "_ref": ref,
            "name": "test_lbdn",
            "pools": [
                {'pool': 'pool1', 'ratio': 1},
                {'pool': 'pool2', 'ratio': 2},
            ],
            "extattrs": {},
        }]
        test_spec = {
            "name": {"ib_req": True},
            "pools": {},
            "comment": {},
            "extattrs": {},
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run(api.NIOS_DTC_LBDN, test_spec)

        self.assertFalse(res['changed'],
                         'Same pool order must not register a change')
        wapi.update_object.assert_not_called()
        wapi.create_object.assert_not_called()

    def test_nios_dtc_lbdn_pools_reorder_registers_change(self):
        """Re-run with pools reordered MUST register changed=True and trigger update."""
        self.module.params = {
            'provider': None, 'state': 'present', 'name': 'test_lbdn',
            'pools': [
                {'pool': 'pool2', 'ratio': 2},
                {'pool': 'pool1', 'ratio': 1},
            ],
            'comment': None, 'extattrs': None,
        }
        ref = "dtc:lbdn/ZG5zLm5ldHdvcmtfdmlld:test_lbdn"
        test_object = [{
            "_ref": ref,
            "name": "test_lbdn",
            "pools": [
                {'pool': 'pool1', 'ratio': 1},
                {'pool': 'pool2', 'ratio': 2},
            ],
            "extattrs": {},
        }]
        test_spec = {
            "name": {"ib_req": True},
            "pools": {},
            "comment": {},
            "extattrs": {},
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run(api.NIOS_DTC_LBDN, test_spec)

        self.assertTrue(res['changed'],
                        'Reordered pools must register a change (pool order is semantic)')
        wapi.update_object.assert_called_once()
