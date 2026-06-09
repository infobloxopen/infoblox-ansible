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
version_added: "1.10.0"
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
    elements: str
  access_method:
    description:
      - Allows for the configuration of how members of the group are allowed to
        access the NIOS appliance. Valid values are C(API), C(CLI), C(CLOUD_API),
        C(GUI), and C(TAXII). When not specified, all access methods are enabled by default.
    type: list
    elements: str
  email_addresses:
    description:
      - List of email addresses for the admin group members.
    type: list
    elements: str
  enable_restricted_user_access:
    description:
      - Determines whether restricted user access is enabled for the admin group.
        When enabled, users in this group have restricted access to specific features.
    type: bool
    default: false
  superuser:
    description:
      - Determines whether the admin group has superuser privileges. Superuser groups
        have unrestricted access to all NIOS features and settings.
    type: bool
    default: false
  disable_concurrent_login:
    description:
      - Determines whether concurrent login is disabled for members of this admin group.
        When set to True, only one session per user is allowed.
    type: bool
    default: false
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
- name: Create a new admin group with basic settings
  infoblox.nios_modules.nios_admingroup:
    name: ansible_group
    comment: "Group created by Ansible"
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create an admin group with roles and access methods
  infoblox.nios_modules.nios_admingroup:
    name: api_admin_group
    roles:
      - "DNS Admin"
      - "DHCP Admin"
    access_method:
      - GUI
      - API
    email_addresses:
      - admin@example.com
      - support@example.com
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create a superuser admin group
  infoblox.nios_modules.nios_admingroup:
    name: superuser_group
    superuser: true
    disable_concurrent_login: true
    comment: "Superuser group with no concurrent logins"
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create a disabled admin group with extensible attributes
  infoblox.nios_modules.nios_admingroup:
    name: disabled_group
    disable: true
    enable_restricted_user_access: true
    extattrs:
      Site: "Branch Office"
      Department: "Operations"
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

RETURN = '''
obj_ref:
  description: The object reference of the admin group
  returned: always
  type: str
  sample: "admingroup/ZG5zLm5ldHdvcmskMTAuMC4wLjAvMTYvMA:ansible_group/false"
name:
  description: The name of the admin group
  returned: always
  type: str
  sample: "ansible_group"
disable:
  description: Whether the admin group is disabled
  returned: always
  type: bool
  sample: false
comment:
  description: The comment associated with the admin group
  returned: when comment is set
  type: str
  sample: "Group created by Ansible"
roles:
  description: List of roles assigned to the admin group
  returned: when roles are assigned
  type: list
  elements: str
  sample: ["DNS Admin", "DHCP Admin"]
access_method:
  description: List of access methods allowed for the admin group
  returned: always
  type: list
  elements: str
  sample: ["GUI", "API"]
email_addresses:
  description: List of email addresses for the admin group
  returned: when email addresses are set
  type: list
  elements: str
  sample: ["admin@example.com", "support@example.com"]
superuser:
  description: Whether the admin group has superuser privileges
  returned: always
  type: bool
  sample: false
enable_restricted_user_access:
  description: Whether restricted user access is enabled
  returned: always
  type: bool
  sample: false
disable_concurrent_login:
  description: Whether concurrent login is disabled
  returned: always
  type: bool
  sample: false
extattrs:
  description: Extensible attributes associated with the admin group
  returned: when extattrs are set
  type: dict
  sample: {"Site": "Branch Office", "Department": "Operations"}
'''

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
        access_method=dict(type='list'),
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
