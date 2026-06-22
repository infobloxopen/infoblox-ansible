#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: nios_authpolicy
author: "Andrew Heath (@aheath1992)"
short_description: Configure Infoblox NIOS Authentication Policy
version_added: "1.10.0"
description:
  - Manages the Authentication Policy on Infoblox NIOS servers.
  - The authentication policy is a singleton object that controls the ordered
    list of admin groups used for LDAP authentication mapping.
  - The order of I(admin_groups) determines authentication priority.
  - This module only updates the existing policy; it cannot be created or deleted.
requirements:
  - infoblox-client
extends_documentation_fragment: infoblox.nios_modules.nios
notes:
  - This module supports C(check_mode).
  - The authentication policy is a singleton object that always exists on the NIOS appliance.
  - The order of groups in I(admin_groups) is significant and will be preserved exactly as specified.
options:
  admin_groups:
    description:
      - An ordered list of admin group names for the authentication policy.
      - The order determines the priority of LDAP group mappings under
        "Authentication Server Groups is the authority for".
      - The list will be applied exactly as specified, including order.
    required: true
    type: list
    elements: str
'''

EXAMPLES = r'''
- name: Set authentication policy group order
  infoblox.nios_modules.nios_authpolicy:
    admin_groups:
      - admin-group
      - network-admins
      - dns-admins
      - read-only-group
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Update authentication policy group order from inventory
  infoblox.nios_modules.nios_authpolicy:
    admin_groups: "{{ ordered_auth_groups }}"
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = r'''
current_groups:
  description: The admin group order before the change
  returned: always
  type: list
  elements: str
  sample: ["admin-group", "dns-admins", "network-admins"]
desired_groups:
  description: The desired admin group order
  returned: always
  type: list
  elements: str
  sample: ["admin-group", "network-admins", "dns-admins"]
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.api import WapiModule
from ..module_utils.api import NIOS_AUTHPOLICY
from ..module_utils.api import normalize_ib_spec


def main():
    argument_spec = dict(
        provider=dict(required=True),
        admin_groups=dict(required=True, type='list', elements='str')
    )

    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    wapi = WapiModule(module)
    desired_groups = module.params['admin_groups']
    result = {'changed': False}

    try:
        existing = wapi.get_object(NIOS_AUTHPOLICY, {}, return_fields=['admin_groups'])
    except Exception as e:
        module.fail_json(msg=f"Failed to fetch authentication policy: {str(e)}")

    if not existing:
        module.fail_json(msg="Authentication policy object not found on the NIOS appliance")

    policy_ref = existing[0]['_ref']
    current_groups = existing[0].get('admin_groups', [])

    result['current_groups'] = current_groups
    result['desired_groups'] = desired_groups

    if current_groups != desired_groups:
        if not module.check_mode:
            try:
                wapi.update_object(policy_ref, {'admin_groups': desired_groups})
            except Exception as e:
                module.fail_json(msg=f"Failed to update authentication policy: {str(e)}")
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
