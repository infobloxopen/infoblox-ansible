#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: nios_admingroup
author: "Andrew Heath (@aheath1992)"
short_description: Configure Infoblox NIOS Group
version_added: 
description:
  - Adds and/or removes instances of admingroup objects from
    Infoblox NIOS servers. This module manages NIOS C(admingroup) objects
    using the Infoblox WAPI interface over REST.
requirements:
  - infoblox-client
extends_documentation_fragment: infoblox.nios_modules.nios
notes:
  - This module supports C(check_mode).
options:
  name:
    description:
      - Specifies the admingroup name to add or remove from the system.
        Users can also update the name as it is possible
        to pass a dict containing I(new_name), I(old_name). See examples.
    required: true
    type: str
  disable:
    description:
      - Determines whether the admin group is disabled or not. When this is set
        to False, the admin group is enabled.
    default: false
    type: bool
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
  roles:
    description:
      - Allows for the assignment of existing NIOS roles on the instance of the
        object. This argument accepts a list for configuration.
    type: list
  access_method:
    description:
      - Allows for the configuration of how members of the group are allowed to
        access the NIOS appliance.
    type: list
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
- name: Create a new admin group
  infoblox.nios_modules.nios_admingroup:
    name: ansible_group
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Update admin group name
  infoblox.nios_modules.nios_admingroup:
    name: {new_name: new_group, old_name: ansible_group}
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove admin group
  infoblox.nios_modules.nios_admingroup:
    name: new_group
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
from ..module_utils.api import NIOS_ADMINGROUP
from ..module_utils.api import normalize_ib_spec


def main():
    ''' Main entry point for module execution
    '''
    ib_spec = dict(
        name=dict(required=True, ib_req=True),
        comment=dict(),
        email_addresses=dict(type='list'),
        disable=dict(type='bool', default=False),
        extattrs=dict(type='dict'),
        enable_restricted_user_access=dict(type='bool', default=False),
        roles=dict(type='list'),
        access_method=dict(type='list', default=['GUI']),
        superuser=dict(type='bool', default=False), 
        disable_concurrent_login=dict(type='bool', default=False)
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
    result = wapi.run(NIOS_ADMINGROUP, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
