# (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

try:
    from ansible_collections.infoblox.nios_modules.tests.unit.compat import unittest
except ImportError:
    import unittest
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock
from ansible.errors import AnsibleError
from infoblox_client.exceptions import InfobloxException, InfobloxConnectionError
from ansible_collections.infoblox.nios_modules.plugins.inventory import nios_inventory


class TestNiosInventoryParse(unittest.TestCase):
    # ------------------------------------------------------------------
    # Issue #223: parse() must distinguish connection/WAPI failures from
    # other unexpected errors so unrelated problems are not mislabeled as
    # connectivity issues.
    # ------------------------------------------------------------------

    def setUp(self):
        super(TestNiosInventoryParse, self).setUp()
        self.plugin = nios_inventory.InventoryModule()
        self.plugin._read_config_data = MagicMock(name='_read_config_data')
        self.plugin.inventory = MagicMock(name='inventory')
        self._options = {
            'host': 'blox.example.com',
            'username': 'admin',
            'password': 'secret',
            'hostfilter': {},
            'extattrs': {},
        }
        self.plugin.get_option = lambda name: self._options[name]

    def _run_parse(self, get_object_side_effect):
        wapi = MagicMock(name='WapiInventory')
        wapi.get_object.side_effect = get_object_side_effect
        with patch.object(nios_inventory.BaseInventoryPlugin, 'parse'), \
                patch.object(nios_inventory, 'WapiInventory', return_value=wapi):
            self.plugin.parse(MagicMock(), MagicMock(), '/path/to/inventory.yml')

    def test_connection_error_reports_unable_to_connect(self):
        '''InfobloxConnectionError must surface as an "Unable to connect" error.'''
        exc = InfobloxConnectionError(reason='Connection refused')
        with self.assertRaises(AnsibleError) as cm:
            self._run_parse(exc)
        msg = str(cm.exception)
        self.assertIn("Unable to connect to Infoblox NIOS host 'blox.example.com'", msg)
        self.assertIn('Connection refused', msg)

    def test_infoblox_exception_reports_unable_to_connect(self):
        '''A raw InfobloxException must also map to the connect message.'''
        exc = InfobloxException(response={'text': 'bad credentials'})
        with self.assertRaises(AnsibleError) as cm:
            self._run_parse(exc)
        self.assertIn(
            "Unable to connect to Infoblox NIOS host 'blox.example.com'",
            str(cm.exception),
        )

    def test_wrapped_wapi_error_reports_failed_to_query(self):
        '''handle_exception surfaces WAPI text as a plain Exception, which must
        be reported as a query failure, not a connectivity issue.'''
        exc = Exception('authentication failure')
        with self.assertRaises(AnsibleError) as cm:
            self._run_parse(exc)
        msg = str(cm.exception)
        self.assertIn("Failed to query Infoblox NIOS host 'blox.example.com'", msg)
        self.assertIn('authentication failure', msg)

    def test_unexpected_error_reports_failed_to_query(self):
        '''An unrelated runtime error must use the generic query message.'''
        exc = KeyError('boom')
        with self.assertRaises(AnsibleError) as cm:
            self._run_parse(exc)
        self.assertIn(
            "Failed to query Infoblox NIOS host 'blox.example.com'",
            str(cm.exception),
        )

    def test_ansible_error_is_propagated_unchanged(self):
        '''An AnsibleError raised inside the try block must propagate as-is.'''
        exc = AnsibleError('original ansible error')
        with self.assertRaises(AnsibleError) as cm:
            self._run_parse(exc)
        self.assertIn('original ansible error', str(cm.exception))
