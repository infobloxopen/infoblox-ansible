#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_dtc_lbdn
author: "Mauricio Teixeira (@badnetmask)"
short_description: Configure Infoblox NIOS DTC LBDN
description:
  - Adds and/or removes instances of DTC Load Balanced Domain Name (LBDN)
    objects from Infoblox NIOS servers. This module manages NIOS
    C(dtc:lbdn) objects using the Infoblox WAPI interface over REST.
requirements:
  - infoblox-client
extends_documentation_fragment: infoblox.nios_modules.nios
options:
  name:
    description:
      - Specifies the display name of the DTC LBDN, not DNS related.
    required: true
    type: str
  lb_method:
    description:
      - Configures the load balancing method. Used to select pool.
    required: true
    choices:
      - GLOBAL_AVAILABILITY
      - RATIO
      - ROUND_ROBIN
      - TOPOLOGY
  pools:
    description:
      - The pools used for load balancing.
    required: false
    type: list
    elements: dict
    suboptions:
      pool:
        description:
          - Provide the name of the pool to link with
        required: true
        type: str
      ratio:
        description:
          - Provide the weight of the pool
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
- name: configure a DTC Server
  infoblox.nios_modules.nios_dtc_server:
    name: a.ansible.com
    host: 192.168.10.1
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: add a comment to a DTC server
  infoblox.nios_modules.nios_dtc_server:
    name: a.ansible.com
    host: 192.168.10.1
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: remove a DTC Server from the system
  infoblox.nios_modules.nios_dtc_server:
    name: a.ansible.com
    host: 192.168.10.1
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
from ..module_utils.api import NIOS_DTC_LBDN


def main():
    ''' Main entry point for module execution
    '''

    def pools_transform(module):
      pool_list = list()
      if module.params['pools']:
        for pool in module.params['pools']:
          pool_obj = wapi.get_object('dtc:pool',
            {'name': pool['pool']})
          if not 'ratio' in pool:
            pool['ratio'] = 1
          if pool_obj is not None:
            pool_list.append({'pool': pool_obj[0]['_ref'],
              'ratio': pool['ratio']})
      return pool_list

    pools_spec=dict(
      pool=dict(),
      ratio=dict(type='int')
    )

    ib_spec = dict(
        name=dict(required=True, ib_req=True),
        lb_method=dict(required=True, choices=['GLOBAL_AVAILABILITY',
          'RATIO', 'ROUND_ROBIN', 'TOPOLOGY']),

        pools=dict(type='list', options=pools_spec, transform=pools_transform),

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
    result = wapi.run(NIOS_DTC_LBDN, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
