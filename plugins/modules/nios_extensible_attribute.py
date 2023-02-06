#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_extensible_attribute
author: "Matthew Dennett (@matthewdennett)"
short_description: Configure Infoblox NIOS extensible attribute definition
version_added: "1.5.0"
description:
  - Adds and/or removes a extensible attribute definition objects from
    Infoblox NIOS servers.  This module manages NIOS C(extensibleattributedef) 
    objects using the Infoblox WAPI interface over REST.
requirements:
  - infoblox-client
extends_documentation_fragment: infoblox.nios_modules.nios
notes:
    - This module supports C(check_mode).
options:

  comment:
    description:
      - Configures a text string comment to be associated with the instance
        of this object.  The provided text string will be configured on the
        object instance.
    type: str


  default_value:
    description:
      - Configures the default value which is prepopulated in the GUI when 
        this attribute is used. Email, URL and string types the value is a 
        with a maximum of 256 characters. 
    type: str


  list_values:
    description: #TODO


  max:#TODO 
  min:#TODO 
  
  name:
    description: 
      - Configures the intended name of the instance of the object on the 
        NIOS server. 
    type: str
    required: true

  type:
    description: 
      - Configures the type for this attribute object definition. 
    type: str
    required: true
    default: STRING
    choices:
      - DATE
      - EMAIL
      - ENUM
      - INTEGER
      - STRING
      - URL

  state:
    description:
      - Configures the intended state of the instance of the object on
        the NIOS server.  When this value is set to C(present), the object
        is configured on the device and when this value is set to C(absent)
        the value is removed (if necessary) from the device.
    type: str
    default: present
    choices:
      - present
      - absent
'''
# TODO - Create examples of the task
EXAMPLES = '''
- name: Configure a network ipv4
  infoblox.nios_modules.nios_network:
    network: 192.168.10.0/24
    comment: this is a test comment
    state: present
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
from ..module_utils.api import NIOS_IPV4_NETWORK, NIOS_IPV6_NETWORK
from ..module_utils.api import NIOS_IPV4_NETWORK_CONTAINER, NIOS_IPV6_NETWORK_CONTAINER
from ..module_utils.api import normalize_ib_spec
from ..module_utils.network import validate_ip_address, validate_ip_v6_address


def options(module):
    ''' Transforms the module argument into a valid WAPI struct
    This function will transform the options argument into a structure that
    is a valid WAPI structure in the format of:
        {
            name: <value>,
            num: <value>,
            value: <value>,
            use_option: <value>,
            vendor_class: <value>
        }
    It will remove any options that are set to None since WAPI will error on
    that condition.  It will also verify that either `name` or `num` is
    set in the structure but does not validate the values are equal.
    The remainder of the value validation is performed by WAPI
    '''
    options = list()
    for item in module.params['options']:
        opt = dict([(k, v) for k, v in iteritems(item) if v is not None])
        if 'name' not in opt and 'num' not in opt:
            module.fail_json(msg='one of `name` or `num` is required for option value')
        options.append(opt)
    return options


def main():
    ''' Main entry point for module execution
    '''

    ib_spec = dict(
        comment=dict(type='str'),
        default_value=dict(type='str'),
        list_values=dict(type='dict'),
        max=dict(type='int'),
        min=dict(type='int'),
        name=dict(type='list', ib_req=True),
        type=dict(type='list', ib_req=True)
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

    result = wapi.run('extensibleattributedef', ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
