#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: nios_permission
author: "Andrew Heath (@aheath1992)"
short_description: Configure Infoblox NIOS Permissions
version_added: "1.10.0"
description:
  - Adds and/or removes instances of permission objects from
    Infoblox NIOS servers. This module manages NIOS C(permission) objects
    using the Infoblox WAPI interface over REST.
  - The permission object controls access for limited-access admin groups or roles to DHCP/DNS resources.
  - By default, access is denied without defined permissions.
requirements:
  - infoblox-client
extends_documentation_fragment: infoblox.nios_modules.nios
notes:
  - This module supports C(check_mode).
  - At least one of I(group) or I(role) must be specified.
  - At least one of I(object) or I(resource_type) must be specified.
  - Permission objects do not support global search, so idempotency is achieved by catching duplicate creation errors.
options:
  group:
    description:
      - Specifies the admin group name this permission applies to.
      - Mutually exclusive with I(role). At least one of I(group) or I(role) is required.
    type: str
  role:
    description:
      - Specifies the role name this permission applies to.
      - Mutually exclusive with I(group). At least one of I(group) or I(role) is required.
    type: str
  permission:
    description:
      - Specifies the permission level to grant.
    required: true
    type: str
    choices:
      - DENY
      - READ
      - WRITE
  object:
    description:
      - Full WAPI reference to the object for this permission (e.g., C(zone_auth/ZG5z...)).
      - Can be specified directly OR constructed using I(object_type), I(object_name), and optionally I(object_view).
      - At least one of I(object) or I(resource_type) is required.
      - When specified with I(resource_type), applies to child objects of the specified type.
    type: str
  object_type:
    description:
      - The WAPI object type (e.g., C(zone_auth), C(network), C(record:host)).
      - Used with I(object_name) to look up the object reference automatically.
      - Ignored if I(object) is directly provided.
      - Common values include C(zone_auth), C(network), C(ipv6network), C(networkcontainer), C(record:host).
    type: str
  object_name:
    description:
      - The name or identifier of the object.
      - For zones use the zone name (e.g., C(example.com)).
      - For networks use CIDR notation (e.g., C(192.168.1.0/24)).
      - For host records use the FQDN (e.g., C(server01.example.com)).
      - Ignored if I(object) is directly provided.
    type: str
  object_view:
    description:
      - The DNS view or network view for the object.
      - Used with I(object_type) and I(object_name).
      - Defaults to C(default) if not specified.
    type: str
    default: default
  resource_type:
    description:
      - Specifies the resource type this permission applies to.
      - When I(object) is set, this applies to child objects of the specified type.
      - When I(object) is not set, this creates a global permission for the resource type.
      - At least one of I(object) or I(resource_type) is required.
    type: str
    choices:
      - A
      - AAAA
      - CAA
      - CNAME
      - DNAME
      - DEVICE
      - FIXED_ADDRESS
      - GRID
      - HOST
      - IPV6_FIXED_ADDRESS
      - IPV6_NETWORK
      - IPV6_NETWORK_CONTAINER
      - IPV6_RANGE
      - MEMBER
      - MX
      - NAPTR
      - NETWORK
      - NETWORK_CONTAINER
      - PTR
      - RANGE
      - ROAMING_HOST
      - SHARED_NETWORK
      - SRV
      - TENANT
      - TLSA
      - TXT
      - VIEW
      - VLAN_OBJECTS
      - ZONE
  state:
    description:
      - Configures the intended state of the instance of the object on
        the NIOS server.  When this value is set to C(present), the object
        is configured on the device and when this value is set to C(absent)
        the value is removed (if necessary) from the device.
    default: present
    choices:
      - present
      - absent
    type: str
'''

EXAMPLES = r'''
- name: Grant read permission to a group for a specific zone (simple way)
  infoblox.nios_modules.nios_permission:
    group: dns_admins
    permission: READ
    object_type: zone_auth
    object_name: example.com
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Grant permission for a network using CIDR notation
  infoblox.nios_modules.nios_permission:
    group: network_admins
    permission: WRITE
    object_type: network
    object_name: 192.168.1.0/24
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Grant permission using full WAPI reference (if you already have it)
  infoblox.nios_modules.nios_permission:
    group: dns_admins
    permission: READ
    object: "zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmV4YW1wbGU:example.com/default"
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Grant write permission to a role for all IPv6 networks (global)
  infoblox.nios_modules.nios_permission:
    role: network_admin
    permission: WRITE
    resource_type: IPV6_NETWORK
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Grant permission for ranges within a network container
  infoblox.nios_modules.nios_permission:
    role: dhcp_manager
    permission: WRITE
    object_type: networkcontainer
    object_name: 10.0.0.0/8
    resource_type: RANGE
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Permission for a zone in a non-default view
  infoblox.nios_modules.nios_permission:
    group: internal_dns
    permission: WRITE
    object_type: zone_auth
    object_name: internal.example.com
    object_view: internal
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove a permission
  infoblox.nios_modules.nios_permission:
    group: dns_admins
    permission: READ
    object_type: zone_auth
    object_name: example.com
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = '''
obj_ref:
  description: The object reference of the permission
  returned: when created successfully
  type: str
  sample: "permission/ZG5zLmJpbmRfY25hbWU:dns_admins/READ"
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.api import WapiModule
from ..module_utils.api import NIOS_PERMISSION
from ..module_utils.api import normalize_ib_spec

try:
    from infoblox_client.exceptions import InfobloxException
except ImportError:
    InfobloxException = None


def main():
    ''' Main entry point for module execution
    '''

    resource_type_choices = [
        'A', 'AAAA', 'CAA', 'CNAME', 'DNAME', 'DEVICE', 'FIXED_ADDRESS',
        'GRID', 'HOST', 'IPV6_FIXED_ADDRESS', 'IPV6_NETWORK',
        'IPV6_NETWORK_CONTAINER', 'IPV6_RANGE', 'MEMBER', 'MX', 'NAPTR',
        'NETWORK', 'NETWORK_CONTAINER', 'PTR', 'RANGE', 'ROAMING_HOST',
        'SHARED_NETWORK', 'SRV', 'TENANT', 'TLSA', 'TXT', 'VIEW',
        'VLAN_OBJECTS', 'ZONE'
    ]

    ib_spec = dict(
        group=dict(),
        role=dict(),
        permission=dict(required=True, choices=['DENY', 'READ', 'WRITE']),
        object=dict(),
        resource_type=dict(choices=resource_type_choices)
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent']),
        object_type=dict(type='str'),
        object_name=dict(type='str'),
        object_view=dict(type='str', default='default')
    )

    argument_spec.update(normalize_ib_spec(ib_spec))
    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[
            ['group', 'role'],
            ['object', 'resource_type', 'object_type']
        ],
        mutually_exclusive=[
            ['group', 'role']
        ],
        required_together=[
            ['object_type', 'object_name']
        ]
    )

    wapi = WapiModule(module)
    state = module.params['state']
    result = {'changed': False}

    # If object_type and object_name provided, look up the object reference
    if module.params.get('object_type') and module.params.get('object_name') and not module.params.get('object'):
        object_type = module.params['object_type']
        object_name = module.params['object_name']
        object_view = module.params['object_view']

        # Build query based on object type
        query = {}
        if object_type in ['zone_auth', 'zone_forward', 'zone_delegated']:
            query['fqdn'] = object_name
            query['view'] = object_view
        elif object_type in ['network', 'ipv6network', 'networkcontainer', 'ipv6networkcontainer']:
            query['network'] = object_name
            query['network_view'] = object_view
        elif object_type.startswith('record:'):
            query['name'] = object_name
            query['view'] = object_view
        else:
            # Generic fallback
            query['name'] = object_name

        try:
            obj_result = wapi.get_object(object_type, query)
            if not obj_result:
                module.fail_json(msg=f"Object '{object_name}' of type '{object_type}' not found in view '{object_view}'")
            module.params['object'] = obj_result[0]['_ref']
        except Exception as e:
            module.fail_json(msg=f"Error looking up object: {str(e)}")

    # Build payload with only provided values
    payload = {}
    for key in ['group', 'role', 'permission', 'object', 'resource_type']:
        if module.params.get(key) is not None:
            payload[key] = module.params[key]

    if state == 'present':
        # Attempt to create the permission
        if not module.check_mode:
            try:
                # Call create_object directly on the connector to bypass WapiModule's exception handler
                new_ref = wapi.connector.create_object(NIOS_PERMISSION, payload)
                result['obj_ref'] = new_ref
                result['changed'] = True
            except InfobloxException as e:
                # Check if this is a duplicate permission error - treat as idempotent
                if hasattr(e, 'response') and 'text' in e.response:
                    error_msg = e.response['text']
                    error_code = e.response.get('code', '')
                else:
                    error_msg = str(e)
                    error_code = ''

                if 'Duplicate permissions' in error_msg or 'already exist' in error_msg or 'Client.Ibap.Data.Conflict' in error_code:
                    # Permission already exists - this is idempotent
                    result['changed'] = False
                else:
                    # Re-raise for WapiModule.handle_exception to process
                    module.fail_json(
                        msg=error_msg,
                        code=error_code,
                        type=e.response.get('Error', '').split(':')[0] if hasattr(e, 'response') and 'Error' in e.response else 'UnknownError'
                    )
            except Exception as e:
                module.fail_json(msg=f"Failed to create permission: {str(e)}")
        else:
            result['changed'] = True

    elif state == 'absent':
        # For deletion, search for matching permission and delete if found
        # Build search filter with only provided values
        search_filter = {}
        for key in ['group', 'role', 'permission', 'object', 'resource_type']:
            if module.params.get(key) is not None:
                search_filter[key] = module.params[key]

        try:
            existing = wapi.get_object(NIOS_PERMISSION, search_filter)
            if existing:
                if not module.check_mode:
                    wapi.delete_object(existing[0]['_ref'])
                result['changed'] = True
        except Exception as e:
            # If search fails (404 or other), permission may not exist - that's okay for deletion
            error_msg = str(e)
            if '404' not in error_msg:
                module.fail_json(msg=f"Error searching for permission: {error_msg}")

    module.exit_json(**result)


if __name__ == '__main__':
    main()
