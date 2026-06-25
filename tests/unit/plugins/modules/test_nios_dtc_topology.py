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
from ansible_collections.infoblox.nios_modules.tests.unit.plugins.modules.utils import AnsibleFailJson
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

    def _mock_module(self):
        """A lightweight AnsibleModule double whose fail_json raises, so the
        rule-transform validation can be exercised directly."""
        module = MagicMock(name='ansible_module')
        module.fail_json = Mock(side_effect=AnsibleFailJson)
        module.deprecate = Mock(name='deprecate')
        module.warn = Mock(name='warn')
        return module

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
        ref = "dtc:topology/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                '_ref': ref,
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
        wapi.update_object.assert_called_once_with(ref, {'comment': 'updated comment', 'name': 'a_topology'})

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

    def test_uses_structured_rule_destination_version_gate(self):
        """NPA-1840: the topology rule destination became a structured array in
        WAPI 2.14 (NIOS 9.1.0). The gate must be False up to 2.13.x and True
        from 2.14 onward, treating a missing patch component as 0."""
        gate = api.dtc_topology_uses_structured_destination
        # Pre-2.14: legacy top-level destination_link string.
        self.assertFalse(gate('2.12.3'))
        self.assertFalse(gate('2.13'))
        self.assertFalse(gate('2.13.7'))
        # 2.14 and later: structured destination array.
        self.assertTrue(gate('2.14'))
        self.assertTrue(gate('2.14.0'))
        self.assertTrue(gate('2.15'))
        # Any future major version is assumed to support it.
        self.assertTrue(gate('3.0'))
        # Malformed versions degrade safely to the legacy behavior.
        self.assertFalse(gate('garbage'))

    def test_normalize_dtc_topology_rules_structured(self):
        """NPA-1840: a WAPI 2.14 fetch returns expanded destination links and
        server-side _ref/uuid bookkeeping; normalization must flatten the link
        to its bare reference and drop the bookkeeping so the idempotency
        comparison matches the module's payload."""
        fetched = {
            'name': 'topo1',
            'rules': [{
                '_ref': 'dtc:topology:rule/abc:topo1/web_pool',
                'uuid': 'deadbeef',
                'dest_type': 'POOL',
                'destination': [{
                    'destination_link': {
                        '_ref': 'dtc:pool/xyz:web_pool',
                        'name': 'web_pool',
                        'uuid': 'cafef00d',
                    },
                    'priority': 1,
                }],
                'return_type': 'REGULAR',
                'sources': [],
            }],
        }
        api.normalize_dtc_topology_rules(fetched)
        self.assertEqual(fetched['rules'], [{
            'dest_type': 'POOL',
            'destination': [{'destination_link': 'dtc:pool/xyz:web_pool', 'priority': 1}],
            'return_type': 'REGULAR',
        }])

    def test_normalize_dtc_topology_rules_sorts_by_priority(self):
        """NPA-1840: NIOS stores and returns the destination array sorted by
        ascending priority regardless of the order it was sent in. Normalization
        must produce that same priority order so a topology supplied with
        out-of-priority destinations still compares equal on re-apply."""
        fetched = {
            'name': 'topo1',
            'rules': [{
                '_ref': 'dtc:topology:rule/abc:topo1/a_b',
                'uuid': 'deadbeef',
                'dest_type': 'POOL',
                'destination': [
                    {'destination_link': {'_ref': 'dtc:pool/xyz:pool_b', 'name': 'pool_b'},
                     'priority': 2},
                    {'destination_link': {'_ref': 'dtc:pool/xyz:pool_a', 'name': 'pool_a'},
                     'priority': 1},
                ],
                'return_type': 'REGULAR',
                'sources': [],
            }],
        }
        api.normalize_dtc_topology_rules(fetched)
        self.assertEqual(fetched['rules'], [{
            'dest_type': 'POOL',
            'destination': [
                {'destination_link': 'dtc:pool/xyz:pool_a', 'priority': 1},
                {'destination_link': 'dtc:pool/xyz:pool_b', 'priority': 2},
            ],
            'return_type': 'REGULAR',
        }])

    def test_normalize_dtc_topology_rules_legacy(self):
        """WAPI <= 2.13: the rule carries a top-level destination_link that NIOS
        returns expanded; normalization must flatten it to the bare reference."""
        fetched = {
            'name': 'topo1',
            'rules': [{
                '_ref': 'dtc:topology:rule/abc:topo1/web_pool',
                'uuid': 'deadbeef',
                'dest_type': 'POOL',
                'destination_link': {'_ref': 'dtc:pool/xyz:web_pool', 'name': 'web_pool'},
                'return_type': 'REGULAR',
                'sources': [],
            }],
        }
        api.normalize_dtc_topology_rules(fetched)
        self.assertEqual(fetched['rules'], [{
            'dest_type': 'POOL',
            'destination_link': 'dtc:pool/xyz:web_pool',
            'return_type': 'REGULAR',
        }])

    def test_build_topology_rule_legacy_destination_link(self):
        """WAPI <= 2.13: rule carries a top-level destination_link reference."""
        rule = nios_dtc_topology.build_topology_rule(
            'POOL', 'REGULAR', 'dtc:pool/abc:web_pool', structured_destination=False
        )
        self.assertEqual(rule, {
            'dest_type': 'POOL',
            'return_type': 'REGULAR',
            'destination_link': 'dtc:pool/abc:web_pool',
        })

    def test_build_topology_rule_structured_destination(self):
        """NPA-1840 / WAPI >= 2.14: destination is an array of
        {destination_link, priority} and the legacy field is absent."""
        rule = nios_dtc_topology.build_topology_rule(
            'SERVER', 'REGULAR', 'dtc:server/abc:srv1', structured_destination=True
        )
        self.assertEqual(rule, {
            'dest_type': 'SERVER',
            'return_type': 'REGULAR',
            'destination': [{'destination_link': 'dtc:server/abc:srv1', 'priority': 1}],
        })
        self.assertNotIn('destination_link', rule)

    def test_build_topology_rule_structured_default_rule_has_no_destination(self):
        """A NXDOMAIN/NOERR default rule (no destination) carries no destination
        key under the structured schema."""
        rule = nios_dtc_topology.build_topology_rule(
            'POOL', 'NXDOMAIN', None, structured_destination=True
        )
        self.assertEqual(rule, {'dest_type': 'POOL', 'return_type': 'NXDOMAIN'})
        self.assertNotIn('destination', rule)
        self.assertNotIn('destination_link', rule)

    def test_build_topology_rule_includes_sources(self):
        """Sources are passed through unchanged in both schema variants."""
        sources = [{'source_type': 'SUBNET', 'source_value': '10.0.0.0/8'}]
        rule = nios_dtc_topology.build_topology_rule(
            'POOL', 'REGULAR', 'dtc:pool/abc:web_pool', structured_destination=True, sources=sources
        )
        self.assertEqual(rule['sources'], sources)

    def test_build_topology_rule_structured_multi_destination(self):
        """ADR-0002 / WAPI >= 2.14: a pre-resolved destinations list is emitted
        as the destination array verbatim, allowing multiple prioritized
        destinations per rule."""
        destinations = [
            {'destination_link': 'dtc:pool/abc:pool_a', 'priority': 1},
            {'destination_link': 'dtc:pool/abc:pool_b', 'priority': 2},
        ]
        rule = nios_dtc_topology.build_topology_rule(
            'POOL', 'REGULAR', None, structured_destination=True, destinations=destinations
        )
        self.assertEqual(rule, {
            'dest_type': 'POOL',
            'return_type': 'REGULAR',
            'destination': [
                {'destination_link': 'dtc:pool/abc:pool_a', 'priority': 1},
                {'destination_link': 'dtc:pool/abc:pool_b', 'priority': 2},
            ],
        })
        self.assertNotIn('destination_link', rule)

    def test_nios_dtc_topology_create_multi_destination(self):
        """ADR-0002: the new destination list resolves each entry's name to a
        ref and emits a structured multi-destination array on WAPI 2.14+."""
        module = self._mock_module()
        wapi = Mock(name='wapi')
        wapi.get_object = Mock(side_effect=[
            [{'_ref': 'dtc:pool/abc:pool_a', 'name': 'pool_a'}],
            [{'_ref': 'dtc:pool/abc:pool_b', 'name': 'pool_b'}],
        ])
        rules = [{
            'dest_type': 'POOL',
            'destination_link': None,
            'destination': [
                {'destination_link': 'pool_a', 'priority': 1},
                {'destination_link': 'pool_b', 'priority': 2},
            ],
            'return_type': 'REGULAR',
            'sources': None,
        }]

        result = nios_dtc_topology.build_topology_rules(module, wapi, rules, '2.14')

        self.assertEqual(result, [{
            'dest_type': 'POOL',
            'return_type': 'REGULAR',
            'destination': [
                {'destination_link': 'dtc:pool/abc:pool_a', 'priority': 1},
                {'destination_link': 'dtc:pool/abc:pool_b', 'priority': 2},
            ],
        }])
        self.assertFalse(module.fail_json.called)

    def test_nios_dtc_topology_multi_destination_sorted_by_priority(self):
        """NPA-1840: NIOS reorders the destination array by ascending priority on
        readback, so the module must emit it priority-sorted to stay idempotent
        when the user supplies destinations out of priority order."""
        module = self._mock_module()
        wapi = Mock(name='wapi')
        # User lists the higher-priority (2) pool first, lower (1) second.
        wapi.get_object = Mock(side_effect=[
            [{'_ref': 'dtc:pool/abc:pool_b', 'name': 'pool_b'}],
            [{'_ref': 'dtc:pool/abc:pool_a', 'name': 'pool_a'}],
        ])
        rules = [{
            'dest_type': 'POOL',
            'destination_link': None,
            'destination': [
                {'destination_link': 'pool_b', 'priority': 2},
                {'destination_link': 'pool_a', 'priority': 1},
            ],
            'return_type': 'REGULAR',
            'sources': None,
        }]

        result = nios_dtc_topology.build_topology_rules(module, wapi, rules, '2.14')

        self.assertEqual(result, [{
            'dest_type': 'POOL',
            'return_type': 'REGULAR',
            'destination': [
                {'destination_link': 'dtc:pool/abc:pool_a', 'priority': 1},
                {'destination_link': 'dtc:pool/abc:pool_b', 'priority': 2},
            ],
        }])
        self.assertFalse(module.fail_json.called)

    def test_nios_dtc_topology_scalar_link_still_works(self):
        """The legacy scalar destination_link path is unchanged: on 2.14 it is
        wrapped into a single-entry structured destination."""
        module = self._mock_module()
        wapi = Mock(name='wapi')
        wapi.get_object = Mock(return_value=[{'_ref': 'dtc:pool/abc:web_pool', 'name': 'web_pool'}])
        rules = [{
            'dest_type': 'POOL',
            'destination_link': 'web_pool',
            'destination': None,
            'return_type': 'REGULAR',
            'sources': None,
        }]

        result = nios_dtc_topology.build_topology_rules(module, wapi, rules, '2.14')

        self.assertEqual(result, [{
            'dest_type': 'POOL',
            'return_type': 'REGULAR',
            'destination': [{'destination_link': 'dtc:pool/abc:web_pool', 'priority': 1}],
        }])
        self.assertFalse(module.fail_json.called)
        module.deprecate.assert_called_once()

    def test_nios_dtc_topology_destination_link_deprecates_once_per_run(self):
        """When multiple rules use destination_link, emit one deprecation
        warning for the task run instead of one per rule."""
        module = self._mock_module()
        wapi = Mock(name='wapi')
        wapi.get_object = Mock(side_effect=[
            [{'_ref': 'dtc:pool/abc:web_pool1', 'name': 'web_pool1'}],
            [{'_ref': 'dtc:pool/abc:web_pool2', 'name': 'web_pool2'}],
        ])
        rules = [{
            'dest_type': 'POOL',
            'destination_link': 'web_pool1',
            'destination': None,
            'return_type': 'REGULAR',
            'sources': None,
        }, {
            'dest_type': 'POOL',
            'destination_link': 'web_pool2',
            'destination': None,
            'return_type': 'REGULAR',
            'sources': None,
        }]

        result = nios_dtc_topology.build_topology_rules(module, wapi, rules, '2.14')

        self.assertEqual(result, [{
            'dest_type': 'POOL',
            'return_type': 'REGULAR',
            'destination': [{'destination_link': 'dtc:pool/abc:web_pool1', 'priority': 1}],
        }, {
            'dest_type': 'POOL',
            'return_type': 'REGULAR',
            'destination': [{'destination_link': 'dtc:pool/abc:web_pool2', 'priority': 1}],
        }])
        module.deprecate.assert_called_once()
        self.assertFalse(module.warn.called)

    def test_nios_dtc_topology_destination_only_no_deprecation(self):
        """Do not emit destination_link deprecation when only destination is
        used."""
        module = self._mock_module()
        wapi = Mock(name='wapi')
        wapi.get_object = Mock(side_effect=[
            [{'_ref': 'dtc:pool/abc:pool_a', 'name': 'pool_a'}],
            [{'_ref': 'dtc:pool/abc:pool_b', 'name': 'pool_b'}],
        ])
        rules = [{
            'dest_type': 'POOL',
            'destination_link': None,
            'destination': [
                {'destination_link': 'pool_a', 'priority': 1},
                {'destination_link': 'pool_b', 'priority': 2},
            ],
            'return_type': 'REGULAR',
            'sources': None,
        }]

        nios_dtc_topology.build_topology_rules(module, wapi, rules, '2.14')

        self.assertFalse(module.deprecate.called)
        self.assertFalse(module.warn.called)

    def test_nios_dtc_topology_destination_and_link_mutually_exclusive(self):
        """ADR-0002: defining both destination_link and destination on a rule
        must fail."""
        module = self._mock_module()
        wapi = Mock(name='wapi')
        rules = [{
            'dest_type': 'POOL',
            'destination_link': 'pool_a',
            'destination': [{'destination_link': 'pool_b', 'priority': 1}],
            'return_type': 'REGULAR',
            'sources': None,
        }]

        with self.assertRaises(AnsibleFailJson):
            nios_dtc_topology.build_topology_rules(module, wapi, rules, '2.14')
        _, kwargs = module.fail_json.call_args
        self.assertIn('mutually exclusive', kwargs['msg'])

    def test_nios_dtc_topology_destination_requires_214(self):
        """ADR-0002: the destination list is rejected when the negotiated WAPI
        version is below 2.14."""
        module = self._mock_module()
        wapi = Mock(name='wapi')
        rules = [{
            'dest_type': 'POOL',
            'destination_link': None,
            'destination': [{'destination_link': 'pool_a', 'priority': 1}],
            'return_type': 'REGULAR',
            'sources': None,
        }]

        with self.assertRaises(AnsibleFailJson):
            nios_dtc_topology.build_topology_rules(module, wapi, rules, '2.12.3')
        _, kwargs = module.fail_json.call_args
        self.assertIn('2.14', kwargs['msg'])

    def test_nios_dtc_topology_destination_unresolved_name_fails(self):
        """ADR-0002: a destination entry whose pool/server name does not exist
        must fail with a clear message."""
        module = self._mock_module()
        wapi = Mock(name='wapi')
        wapi.get_object = Mock(return_value=[])
        rules = [{
            'dest_type': 'POOL',
            'destination_link': None,
            'destination': [{'destination_link': 'missing_pool', 'priority': 1}],
            'return_type': 'REGULAR',
            'sources': None,
        }]

        with self.assertRaises(AnsibleFailJson):
            nios_dtc_topology.build_topology_rules(module, wapi, rules, '2.14')
        _, kwargs = module.fail_json.call_args
        self.assertIn('missing_pool', kwargs['msg'])
