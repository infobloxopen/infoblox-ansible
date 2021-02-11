#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_dtc_server
author: "Mauricio Teixeira (@badnetmask)"
short_description: Configure Infoblox NIOS DTC Pool
description:
  - Adds and/or removes instances of DTC Pool objects from
    Infoblox NIOS servers. This module manages NIOS C(dtc:pool) objects
    using the Infoblox WAPI interface over REST. A DTC pool is a collection
    of IDNS resources (virtual servers).
requirements:
  - infoblox-client
extends_documentation_fragment: infoblox.nios_modules.nios
options:
  name:
    description:
      - Specifies the DTC Pool display name
    required: true
    type: str
  lb_preferred_method:
    description:
      - Configures the preferred load balancing method.
      - Use this to select a method type from the pool.
    choices:
      - ALL_AVAILABLE
      - DYNAMIC_RATIO
      - GLOBAL_AVAILABILITY
      - RATIO
      - ROUND_ROBIN
      - TOPOLOGY
    required: true
    type: str
  servers:
    description:
      - Configure the DTC Servers related to the pool
    required: false
    type: list
    elements: dict
    suboptions:
      server:
        description:
          - Provide the name of the DTC Server
        required: true
        type: str
      ratio:
        description:
          - Provide the weight of the server
        default: 1
        required: false
        type: int
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

EXAMPLES = '''
- name: configure a DTC Pool
  infoblox.nios_modules.nios_dtc_pool:
    name: web_pool
    lb_preferred_method: ROUND_ROBIN
    servers:
      - server: a.ansible.com
      - server: b.ansible.com
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: add a comment to a DTC Pool
  infoblox.nios_modules.nios_dtc_pool:
    name: web_pool
    lb_preferred_method: ROUND_ROBIN
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: remove a DTC Pool from the system
  infoblox.nios_modules.nios_dtc_pool:
    name: web_pool
    lb_preferred_method: ROUND_ROBIN
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from ..module_utils.api import WapiModule
from ..module_utils.api import NIOS_DTC_POOL
from ..module_utils.api import NIOS_DTC_SERVER

def main():
    ''' Main entry point for module execution
    '''

    def servers_transform(module):
      server_list = list()
      if module.params['servers']:
        for server in module.params['servers']:
          server_obj = wapi.get_object('dtc:server',
            {'name': server['server']})
          if not 'ratio' in server:
            server['ratio'] = 1
          if server_obj is not None:
            server_list.append({'server': server_obj[0]['_ref'],
              'ratio': server['ratio']})
      return server_list

    servers_spec=dict(
      server=dict(),
      ratio=dict(type='int')
    )

    ib_spec = dict(
        name=dict(required=True, ib_req=True),
        lb_preferred_method=dict(required=True, choices=['ALL_AVAILABLE',
          'DYNAMIC_RATIO', 'GLOBAL_AVAILABILITY', 'RATIO', 'ROUND_ROBIN',
          'TOPOLOGY']),

        servers=dict(type='list', options=servers_spec, transform=servers_transform),

        extattrs=dict(type='dict'),
        comment=dict(),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(ib_spec)
    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    wapi = WapiModule(module)
    result = wapi.run(NIOS_DTC_POOL, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
