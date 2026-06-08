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


import unittest

from ansible.errors import AnsibleError
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.infoblox.nios_modules.plugins.lookup import nios_next_network


class TestNiosNextNetworkLookup(unittest.TestCase):

    def setUp(self):
        self.lookup = nios_next_network.LookupModule()

    def _run(self, terms, **kwargs):
        return self.lookup.run(terms, **kwargs)

    # ---- network argument validation -------------------------------------

    def test_missing_network_raises(self):
        with self.assertRaises(AnsibleError) as ctx:
            self._run([], cidr=25)
        self.assertIn('network argument is missing', str(ctx.exception))

    def test_invalid_network_raises(self):
        with self.assertRaises(AnsibleError) as ctx:
            self._run(['not-a-network'], cidr=25)
        self.assertIn('network argument is invalid', str(ctx.exception))

    # ---- cidr argument validation ----------------------------------------

    def test_missing_cidr_raises(self):
        with self.assertRaises(AnsibleError) as ctx:
            self._run(['192.168.10.0/24'])
        self.assertIn('missing required argument: cidr', str(ctx.exception))

    def test_bool_cidr_rejected(self):
        with self.assertRaises(AnsibleError) as ctx:
            self._run(['192.168.10.0/24'], cidr=True)
        self.assertIn('cidr must be an integer', str(ctx.exception))

    def test_float_cidr_rejected(self):
        # int(25.7) would silently truncate to 25; ensure we reject instead.
        with self.assertRaises(AnsibleError) as ctx:
            self._run(['192.168.10.0/24'], cidr=25.7)
        self.assertIn('cidr must be an integer', str(ctx.exception))

    def test_non_numeric_string_cidr_rejected(self):
        with self.assertRaises(AnsibleError) as ctx:
            self._run(['192.168.10.0/24'], cidr='twenty-five')
        self.assertIn('cidr must be an integer', str(ctx.exception))

    def test_ipv4_cidr_out_of_range(self):
        with self.assertRaises(AnsibleError) as ctx:
            self._run(['192.168.10.0/24'], cidr=33)
        self.assertIn('must be in range 1 to 32', str(ctx.exception))

    def test_ipv6_cidr_out_of_range(self):
        with self.assertRaises(AnsibleError) as ctx:
            self._run(['2001:1:111:1::0/64'], cidr=129)
        self.assertIn('must be in range 1 to 128', str(ctx.exception))

    def test_cidr_not_greater_than_parent(self):
        with self.assertRaises(AnsibleError) as ctx:
            self._run(['192.168.10.0/24'], cidr=24)
        self.assertIn('must be greater than parent network cidr', str(ctx.exception))

    # ---- successful lookup paths -----------------------------------------

    @patch.object(nios_next_network, 'WapiLookup')
    def test_numeric_string_cidr_accepted(self, mock_wapi_cls):
        wapi = MagicMock()
        wapi.get_object.return_value = [{'_ref': 'ref1', 'network_view': 'default'}]
        wapi.call_func.return_value = {'networks': ['192.168.10.0/25']}
        mock_wapi_cls.return_value = wapi

        result = self._run(['192.168.10.0/24'], cidr='25')

        self.assertEqual(result, [['192.168.10.0/25']])
        # cidr passed to WAPI must be a real int, not the original string.
        _, called_kwargs = wapi.call_func.call_args
        self.assertEqual(called_kwargs, {})
        called_args = wapi.call_func.call_args[0]
        self.assertEqual(called_args[2]['cidr'], 25)
        self.assertIsInstance(called_args[2]['cidr'], int)

    @patch.object(nios_next_network, 'WapiLookup')
    def test_int_cidr_success(self, mock_wapi_cls):
        wapi = MagicMock()
        wapi.get_object.return_value = [{'_ref': 'ref1', 'network_view': 'default'}]
        wapi.call_func.return_value = {'networks': ['192.168.10.0/25']}
        mock_wapi_cls.return_value = wapi

        result = self._run(['192.168.10.0/24'], cidr=25)

        self.assertEqual(result, [['192.168.10.0/25']])

    @patch.object(nios_next_network, 'WapiLookup')
    def test_container_not_found_raises(self, mock_wapi_cls):
        wapi = MagicMock()
        wapi.get_object.return_value = None
        mock_wapi_cls.return_value = wapi

        with self.assertRaises(AnsibleError) as ctx:
            self._run(['192.168.10.0/24'], cidr=25)
        self.assertIn('unable to find network-container object', str(ctx.exception))

    @patch.object(nios_next_network, 'WapiLookup')
    def test_no_records_for_network_view(self, mock_wapi_cls):
        wapi = MagicMock()
        wapi.get_object.return_value = [{'_ref': 'ref1', 'network_view': 'default'}]
        mock_wapi_cls.return_value = wapi

        with self.assertRaises(AnsibleError) as ctx:
            self._run(['192.168.10.0/24'], cidr=25, network_view='other')
        self.assertIn('no records found', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
