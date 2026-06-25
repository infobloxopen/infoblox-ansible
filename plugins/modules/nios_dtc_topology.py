#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_dtc_topology
author: "Joachim Buyse (@jbisabel)"
short_description: Configure Infoblox NIOS DTC Topology
version_added: "1.6.0"
description:
  - Adds and/or removes instances of DTC Topology objects from
    Infoblox NIOS topologies. This module manages NIOS C(dtc:topology) objects
    using the Infoblox WAPI interface over REST.
requirements:
  - infoblox-client
extends_documentation_fragment: infoblox.nios_modules.nios
notes:
    - This module supports C(check_mode).
options:
  name:
    description:
      - Specifies the DTC Topology display name.
    required: true
    type: str
  rules:
    description:
      - Configures the topology rules
    type: list
    elements: dict
    suboptions:
      dest_type:
        description:
          - Configures the type of the destination for this DTC Topology Rule.
        type: str
        choices:
          - POOL
          - SERVER
        required: true
      destination_link:
        description:
          - Configures the name of the destination DTC pool or DTC server.
          - On NIOS 9.1.0 and later (WAPI 2.14+) the topology rule destination
            schema changed. Set C(wapi_version) to C(2.14) or later in the
            provider so the module sends the structured destination that
            NIOS 9.1.0 expects. The option name and value are unchanged.
          - Mutually exclusive with I(destination) within the same rule.
        type: str
        deprecated:
          why: The legacy scalar destination_link is replaced by destination
            on WAPI 2.14+, which also supports multiple prioritized
            destinations.
          alternative: destination
          removed_in: "2.0.0"
      destination:
        description:
          - Configures a list of prioritized destinations for this DTC Topology
            Rule. Each entry references a DTC pool or DTC server by name and
            assigns it a priority.
          - This option requires NIOS 9.1.0 or later (WAPI 2.14+); set
            C(wapi_version) to C(2.14) or later in the provider to use it. It is
            mutually exclusive with I(destination_link) within the same rule and
            is the only way to configure more than one destination per rule.
        type: list
        elements: dict
        suboptions:
          destination_link:
            description:
              - Configures the name of the destination DTC pool or DTC server.
            type: str
            required: true
          priority:
            description:
              - Configures the priority of this destination within the rule.
              - Lower values are preferred. Must be an unsigned integer.
            type: int
            default: 1
      return_type:
        description:
          - Configures the type of the DNS response for the rule.
        type: str
        choices:
          - NOERR
          - NXDOMAIN
          - REGULAR
        default: REGULAR
      sources:
        description:
          - Configures the conditions for matching sources. Should be empty to
            set the rule as default destination.
        type: list
        elements: dict
        suboptions:
          source_op:
            description:
              - Configures the operation used to match the value.
            type: str
            choices:
              - IS
              - IS_NOT
          source_type:
            description:
              - Configures the source type.
            type: str
            choices:
              - CITY
              - CONTINENT
              - COUNTRY
              - EA0
              - EA1
              - EA2
              - EA3
              - SUBDIVISION
              - SUBNET
            required: true
          source_value:
            description:
              - Configures the source value.
            type: str
            required: true
  extattrs:
    description:
      - Allows for the configuration of Extensible Attributes on the
        instance of the object.  This argument accepts a set of key / value
        pairs for configuration.
    type: dict
  comment:
    description:
      - Configures a text string comment to be associated with the instance
        of this object.  The provided text string will be configured on the
        object instance.
    type: str
  state:
    description:
      - Configures the intended state of the instance of the object on
        the NIOS topology.  When this value is set to C(present), the object
        is configured on the device and when this value is set to C(absent)
        the value is removed (if necessary) from the device.
    default: present
    choices:
      - present
      - absent
    type: str
'''

EXAMPLES = '''
- name: Configure a DTC Topology
  infoblox.nios_modules.nios_dtc_topology:
    name: a_topology
    rules:
      - dest_type: POOL
        destination_link: web_pool1
        return_type: REGULAR
        sources:
          - source_op: IS
            source_type: EA0
            source_value: DC1
      - dest_type: POOL
        destination_link: web_pool2
        return_type: REGULAR
        sources:
          - source_op: IS
            source_type: EA0
            source_value: DC2
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Configure a DTC Topology with prioritized multi-destination rules (WAPI 2.14+)
  infoblox.nios_modules.nios_dtc_topology:
    name: a_topology_structured
    rules:
      - dest_type: POOL
        return_type: REGULAR
        destination:
          - destination_link: web_pool_primary
            priority: 1
          - destination_link: web_pool_secondary
            priority: 2
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
      wapi_version: "2.14"
  connection: local

- name: Add a comment to a DTC topology
  infoblox.nios_modules.nios_dtc_topology:
    name: a_topology
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove a DTC Topology from the system
  infoblox.nios_modules.nios_dtc_topology:
    name: a_topology
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.api import WapiModule
from ..module_utils.api import NIOS_DTC_TOPOLOGY
from ..module_utils.api import normalize_ib_spec
from ..module_utils.api import dtc_topology_uses_structured_destination


def build_topology_rule(dest_type, return_type, dest_ref, structured_destination, sources=None, destinations=None):
    '''Build a single dtc:topology rule payload in the shape the negotiated
    WAPI version expects.

    When ``structured_destination`` is True (WAPI >= 2.14) the destination is
    emitted as a ``destination`` array of ``{destination_link, priority}``
    structs. A pre-resolved ``destinations`` list (from the public
    ``destination`` option) is emitted as-is, allowing multiple prioritized
    destinations per rule; otherwise a single ``dest_ref`` is wrapped in a
    one-entry array with priority 1. A rule with no destination (a NXDOMAIN/NOERR
    default rule, where both are empty) carries no destination at all. When
    ``structured_destination`` is False the legacy top-level ``destination_link``
    reference is used.
    '''
    tf_rule = dict(dest_type=dest_type, return_type=return_type)

    if structured_destination:
        if destinations:
            tf_rule['destination'] = destinations
        elif dest_ref:
            tf_rule['destination'] = [dict(destination_link=dest_ref, priority=1)]
    else:
        tf_rule['destination_link'] = dest_ref

    if sources:
        tf_rule['sources'] = sources

    return tf_rule


def sources_transform(sources, module):
    source_list = list()
    for source in sources:
        src = dict([(k, v) for k, v in source.items() if v is not None])
        if 'source_type' not in src or 'source_value' not in src:
            module.fail_json(msg='source_type and source_value are required for source')
        source_list.append(src)
    return source_list


def emit_destination_link_deprecation(module):
    '''Emit a deprecation warning for legacy rules[].destination_link.'''
    deprecation_msg = (
        'rules[].destination_link is deprecated and will be removed in '
        'infoblox.nios_modules 2.0.0; use rules[].destination instead'
    )
    if hasattr(module, 'deprecate'):
        module.deprecate(
            msg=deprecation_msg,
            version='2.0.0',
            collection_name='infoblox.nios_modules'
        )
    elif hasattr(module, 'warn'):
        module.warn(deprecation_msg)


def build_topology_rules(module, wapi, rules, wapi_version):
    '''Transform the user-supplied topology rules into WAPI payload rules.

    Handles both the legacy scalar ``destination_link`` and the structured
    ``destination`` list (WAPI 2.14+), enforcing per-rule that the two are
    mutually exclusive and that ``destination`` is only used on WAPI 2.14+.
    '''
    rule_list = list()
    destination_link_deprecation_emitted = False

    if not rules:
        return rule_list

    # WAPI 2.14 (NIOS 9.1.0) replaced the top-level destination_link string on a
    # topology rule with a structured destination array. Detect the negotiated
    # WAPI version so we emit the payload shape the appliance accepts.
    structured_destination = dtc_topology_uses_structured_destination(wapi_version)

    def resolve_link(dest_type, name):
        if dest_type == 'POOL':
            return wapi.get_object('dtc:pool', {'name': name})
        return wapi.get_object('dtc:server', {'name': name})

    for rule in rules:
        has_link = rule.get('destination_link') is not None
        has_dest = rule.get('destination') is not None

        if has_link and not destination_link_deprecation_emitted:
            emit_destination_link_deprecation(module)
            destination_link_deprecation_emitted = True

        if has_link and has_dest:
            module.fail_json(
                msg='destination_link and destination are mutually exclusive '
                    'within a topology rule; use destination (WAPI 2.14+), '
                    'destination_link is deprecated'
            )
        if has_dest and not structured_destination:
            module.fail_json(
                msg='destination requires NIOS 9.1.0 / WAPI 2.14 or later; the '
                    'provider negotiated %s. Use destination_link instead.'
                    % wapi_version
            )

        sources = sources_transform(rule['sources'], module) if rule['sources'] else None

        if has_dest:
            destinations = list()
            for entry in rule['destination']:
                dest_obj = resolve_link(rule['dest_type'], entry['destination_link'])
                if not dest_obj:
                    module.fail_json(msg='destination_link %s does not exist' % entry['destination_link'])
                destinations.append(dict(destination_link=dest_obj[0]['_ref'], priority=entry['priority']))

            # NIOS stores the destination array sorted by ascending priority
            # regardless of the order it is sent in, so sort here to mirror the
            # read-side normalization (normalize_dtc_topology_rules) and keep
            # re-applying an unchanged topology idempotent.
            destinations.sort(key=lambda item: item['priority'])

            tf_rule = build_topology_rule(
                rule['dest_type'], rule['return_type'], None, structured_destination,
                sources, destinations=destinations
            )
        else:
            dest_obj = resolve_link(rule['dest_type'], rule['destination_link'])
            if not dest_obj and rule['return_type'] == 'REGULAR':
                module.fail_json(msg='destination_link %s does not exist' % rule['destination_link'])

            dest_ref = dest_obj[0]['_ref'] if dest_obj else None

            tf_rule = build_topology_rule(
                rule['dest_type'], rule['return_type'], dest_ref, structured_destination, sources
            )

        rule_list.append(tf_rule)
    return rule_list


def main():
    ''' Main entry point for module execution
    '''

    def rules_transform(module):
        wapi_version = (module.params.get('provider') or {}).get('wapi_version') or '2.12.3'
        return build_topology_rules(module, wapi, module.params['rules'], wapi_version)

    source_spec = dict(
        source_op=dict(choices=['IS', 'IS_NOT']),
        source_type=dict(required=True, choices=['CITY', 'CONTINENT', 'COUNTRY', 'EA0', 'EA1', 'EA2', 'EA3', 'SUBDIVISION', 'SUBNET']),
        source_value=dict(required=True, type='str')
    )

    destination_spec = dict(
        destination_link=dict(type='str', required=True),
        priority=dict(type='int', default=1)
    )

    rule_spec = dict(
        dest_type=dict(required=True, choices=['POOL', 'SERVER']),
        destination_link=dict(type='str'),
        destination=dict(type='list', elements='dict', options=destination_spec),
        return_type=dict(default='REGULAR', choices=['NOERR', 'NXDOMAIN', 'REGULAR']),
        sources=dict(type='list', elements='dict', options=source_spec)
    )

    ib_spec = dict(
        name=dict(required=True, ib_req=True),

        rules=dict(type='list', elements='dict', options=rule_spec, transform=rules_transform),

        extattrs=dict(type='dict'),
        comment=dict(),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(normalize_ib_spec(ib_spec))
    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    wapi = WapiModule(module)
    result = wapi.run(NIOS_DTC_TOPOLOGY, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
