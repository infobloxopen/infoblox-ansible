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

from ansible_collections.infoblox.nios_modules.plugins.modules import nios_range
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import MagicMock
from .test_nios_module import TestNiosModule


class TestNiosRangeModule(TestNiosModule):

    module = nios_range

    def _make_module_for_options(self, options):
        m = MagicMock()
        m.params = {'options': options}
        return m

    def test_check_vendor_specific_strips_router_by_num(self):
        opts = [{'num': 3, 'value': '192.168.10.1', 'use_option': True}]
        module = self._make_module_for_options(opts)
        nios_range.check_vendor_specific_dhcp_option(module, {'options': {}})
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_strips_ntp_servers_by_num(self):
        opts = [{'num': 42, 'value': '10.0.0.1', 'use_option': True}]
        module = self._make_module_for_options(opts)
        nios_range.check_vendor_specific_dhcp_option(module, {'options': {}})
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_strips_subnet_mask_by_num(self):
        opts = [{'num': 1, 'value': '255.255.255.0', 'use_option': True}]
        module = self._make_module_for_options(opts)
        nios_range.check_vendor_specific_dhcp_option(module, {'options': {}})
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_preserves_router_by_name(self):
        opts = [{'name': 'router', 'value': '192.168.10.1', 'use_option': True}]
        module = self._make_module_for_options(opts)
        nios_range.check_vendor_specific_dhcp_option(module, {'options': {}})
        self.assertIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_strips_routers_by_name(self):
        opts = [{'name': 'routers', 'value': '192.168.10.1', 'use_option': True}]
        module = self._make_module_for_options(opts)
        nios_range.check_vendor_specific_dhcp_option(module, {'options': {}})
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_strips_ntp_servers_by_name(self):
        opts = [{'name': 'ntp-servers', 'value': '10.0.0.1', 'use_option': True}]
        module = self._make_module_for_options(opts)
        nios_range.check_vendor_specific_dhcp_option(module, {'options': {}})
        self.assertNotIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_preserves_use_option_for_domain_name_servers(self):
        opts = [{'name': 'domain-name-servers', 'value': '8.8.8.8', 'use_option': True}]
        module = self._make_module_for_options(opts)
        nios_range.check_vendor_specific_dhcp_option(module, {'options': {}})
        self.assertIn('use_option', module.params['options'][0])

    def test_check_vendor_specific_mixed_options(self):
        opts = [
            {'name': 'routers', 'value': '192.168.10.1', 'use_option': True},
            {'name': 'domain-name-servers', 'value': '8.8.8.8', 'use_option': True},
        ]
        module = self._make_module_for_options(opts)
        nios_range.check_vendor_specific_dhcp_option(module, {'options': {}})
        self.assertNotIn('use_option', module.params['options'][0])
        self.assertIn('use_option', module.params['options'][1])
