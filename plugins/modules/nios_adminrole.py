#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: nios_adminrole
author: "Andrew Heath (@aheath1992)"
short_description: Configure Infoblox NIOS Roles
version_added: "1.10.0"
description:
  - Adds and/or removes instances of adminrole objects from
    Infoblox NIOS servers. This module manages NIOS C(adminrole) objects
    using the Infoblox WAPI interface over REST.
requirements:
  - infoblox-client
extends_documentation_fragment: infoblox.nios_modules.nios
notes:
  - This module supports C(check_mode).
options:
  name:
    description:
      - Specifies the adminrole name to add or remove from the system.
        Users can also update the name as it is possible
        to pass a dict containing I(new_name), I(old_name). See examples.
    required: true
    type: str
  disable:
    description:
      - Determines whether the admin role is disabled or not. When this is set
        to False, the admin role is enabled.
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
- name: Create a new admin role
  infoblox.nios_modules.nios_adminrole:
    name: ansible_role
    comment: "Role created by Ansible"
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create a disabled admin role with extensible attributes
  infoblox.nios_modules.nios_adminrole:
    name: disabled_role
    disable: true
    comment: "Temporarily disabled role"
    extattrs:
      Site: "Main Office"
      Department: "IT"
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Update admin role name
  infoblox.nios_modules.nios_adminrole:
    name: {new_name: new_role, old_name: ansible_role}
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove admin role
  infoblox.nios_modules.nios_adminrole:
    name: new_role
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = '''
obj_ref:
  description: The object reference of the admin role
  returned: always
  type: str
  sample: "adminrole/ZG5zLm5ldHdvcmskMTAuMC4wLjAvMTYvMA:ansible_role/false"
name:
  description: The name of the admin role
  returned: always
  type: str
  sample: "ansible_role"
disable:
  description: Whether the admin role is disabled
  returned: always
  type: bool
  sample: false
comment:
  description: The comment associated with the admin role
  returned: when comment is set
  type: str
  sample: "Role created by Ansible"
extattrs:
  description: Extensible attributes associated with the admin role
  returned: when extattrs are set
  type: dict
  sample: {"Site": "Main Office", "Department": "IT"}
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.api import WapiModule
from ..module_utils.api import NIOS_ADMINROLE
from ..module_utils.api import normalize_ib_spec


def main():
    ''' Main entry point for module execution
    '''

    ib_spec = dict(
            name=dict(required=True, ib_req=True),
            comment=dict(),
            disable=dict(type='bool', default=False),
            extattrs=dict(type='dict')
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
    result = wapi.run(NIOS_ADMINROLE, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
