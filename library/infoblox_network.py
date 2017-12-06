#!/usr/bin/env python

# Copyright 2017 Ken Celenza <ken@networktocode.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    from infoblox_client import objects
    from infoblox_client import connector
    HAS_INFOBLOX_CLIENT = True
except ImportError:
    HAS_INFOBLOX_CLIENT = False


DOCUMENTATION = """
module: infoblox_network
short_description: Manage Infoblox Networks
description:
     - Manage InfoBlox Networks using infblox-client Python library
version_added: "2.4"
author: "Ken Celenza (https://github.com/itdependsnetworks)"
options:
    provider:
      description:
        - A dict object containing connection details.
      default: null
      suboptions:
        host:
            description:
              - Specifies the DNS host name or address for connecting to the remote
                device over the specified transport.  The value of host is used as
                the destination address for the transport.
            required: true
        username:
            description:
              - Configures the username to use to authenticate the connection to
                the remote device.  This value is used to authenticate
                to NIOS
            required: true
        password:
            description:
              - Specifies the password to use to authenticate the connection to
                the remote device.
            required: true
        validate_certs:
            description:
              - Validate SSL certs.  Note, if running on python without SSLContext
                support (typically, python < 2.7.9) you will have to set this to C(no)
                as pysphere does not support validating certificates on older python.
                Prior to 2.1, this module would always validate on python >= 2.7.9 and
                never validate on python <= 2.7.8.
            required: false
            default: no
            choices: ['yes', 'no']
        wapi_version:
            description:
              - The wapi version using to connect to NIOS
            required: false
            default: '2.2'
    network_view:
        description:
          - The network view where the network object exists
        required: false
        default: default
    state:
        description:
          - If the object should be added, removed or found.
        required: true
        default: present
        choices: [ "present", "absent", "get" ]
    comment:
        description:
          - NIOS default network view
        required: false
    extattrs:
        description:
          - A dict of key Value pairs that define the extensible attributes configured
            for the object
          - Example: {"Building": "Empire", "Country": "USA"}
        required: false
    members:
        description:
          - Not yet implemented
        required: false
    dhcp_options:
        description:
          - A list of dict representing the dhcp options of the subnet
          - Example: [{"name": "dhcp-lease-time", "num": 52,"use_option":
            False,"value": "43200", "vendor_class": "DHCP"} ]
        required: false
"""

EXAMPLES = '''
vars:
  provider:
    host: "{{ inventory_hostname }}"
    username: "ntc"
    password: "ntc123"
    validate_certs: False
    wapi: "2.2.2"
- name: CONFIGURE NETWORK OF 10.10.0.0/24 AND UPDATE IF EXIST"
  infoblox_network:
    provider: "{{ provider }}"
    state: "present"
    network: "10.10.0.0/24"
    network_view: "default"
    comment: "Last Verified 08/2017"
- name: "ENSURE NETWORK 10.10.1.0/24 DOES NOT EXIST"
  infoblox_network:
    provider: "{{ provider }}"
    state: "absent"
    network: "10.10.0.0/24"
    network_view: "default"
'''

from ansible.module_utils.basic import AnsibleModule, return_values
STATE = ['get', 'present', 'absent']
BASE_WAPI = '2.2'


def get_network(module, conn, network_view, **kwargs):
    network = kwargs.get('network')
    return_fields = objects.Network._return_fields
    obj = conn.get_object('network', {'network': network, 'network_view': network_view}, return_fields)
    return obj


def compare_fields(module, conn, param, obj):
    fields = ['dhcp_options', 'members', 'extattrs', 'comment']
    build_fields = {}
    for field in fields:
        if param.get(field) is None:
            pass
        elif param.get(field) != obj.get(field):
            return False
    return True


def build_extattrs(module, conn, extattrs):
    out_extattrs = {}
    if extattrs is None:
        return None
    if isinstance(extattrs, dict):
        for key, value in extattrs.items():
            #is one of these supposed to be "key"?
            if isinstance(value, str) and isinstance(value, str):
                out_extattrs[key] = {"value": value}
            else:
                module.fail_json(msg="A propter key/value pair was not a string {}.".format(str(key), str(value)))
        return out_extattrs
    module.fail_json(msg="A propter extattrs dict was not found {}.".format(str(extattrs)))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            provider=dict(type='dict', required=True),
            state=dict(type='str', required=True),
            network_view=dict(type='str', required=True),
            network=dict(type='str', required=False),
            extattrs=dict(type='dict', required=False),
            comment=dict(type='str', required=False),
            filters=dict(type='str', required=False),
            dhcp_options=dict(type='list', required=False),
            members=dict(type='list', required=False),
        ),
        required_one_of=(
            ['network', 'filters'],
        ),
        supports_check_mode=False
    )

    if not HAS_INFOBLOX_CLIENT:
        raise Exception('infoblox-client is not installed.  Please see details here: https://github.com/infobloxopen/infoblox-client')

    provider = module.params['provider'] or {}
    no_log = ['password']
    for param in no_log:
        if provider.get(param):
            module.no_log_values.update(return_values(provider[param]))
        else:
            module.fail_json(msg="Invalid item found in provider.")

    valid_provider = ['host', 'username', 'password', 'validate_certs', 'wapi_version']
    for param, pvalue in provider.items():
        if param in valid_provider:
            module.params[param] = module.params.get(param) or pvalue

    required_params = ['host', 'username', 'password']
    for param in required_params:
        if not module.params.get(param):
            module.fail_json(msg="Provider option {} is required.".format(provider))

    host = module.params['host']
    username = module.params['username']
    password = module.params['password']
    validate_certs = module.params.get('validate_certs', False)
    wapi_version = module.params.get('wapi_version', BASE_WAPI)
    state = module.params['state']
    network_view = module.params.get('network_view', 'default')
    network = module.params['network']
    extattrs = module.params['extattrs']
    comment = module.params['comment']
    filters = module.params['filters']
    dhcp_options = module.params.get('dhcp_options', None)
    members = module.params['members']

    if members is not None:
        module.fail_json(msg="Members has not yet been implemented.")

    opts = {'host': host, 'username': username, 'password': password, 'ssl_verify': validate_certs,
            'silent_ssl_warnings': validate_certs is False, wapi_version: wapi_version}
    conn = connector.Connector(opts)

    extattrs = build_extattrs(module, conn, extattrs)

    if state == 'get':
        if network:
            obj = get_network(module, conn, network_view, network=network)
            if isinstance(obj, list):
                module.exit_json(changed=False, results=obj)
            else:
                module.fail_json(msg="Network {} was not found".format(network))
        elif filters:
            # TODO
            pass
            get_network(module, conn, network_view, filters=filters)
    elif state == 'present':
        return_fields = objects.Network._return_fields
        obj = get_network(module, conn, network_view, network=network)
        if isinstance(obj, list):
            if compare_fields(module, conn, module.params, obj[0]) is False:
                results = objects.Network.create(conn, update_if_exists=True,
                                                 network_view=network_view, cidr=network,
                                                 comment=comment, options=dhcp_options, extattrs=extattrs)
                obj = get_network(module, conn, network_view, network=network)
                module.exit_json(changed=True, results=str(obj))
            else:
                module.exit_json(changed=False, results=obj)
        else:
            results = objects.Network.create(conn,
                                             network_view=network_view, cidr=network,
                                             comment=comment, options=dhcp_options, extattrs=extattrs)
            obj = get_network(module, conn, network_view, network=network)
            module.exit_json(changed=True, results=str(obj))
    elif state == 'absent':
        find_network = objects.Network.search(conn, network_view=network_view, cidr=network)
        if find_network is None:
            module.exit_json(changed=False, results="Network {} did not exit".format(network))
        find_network.delete()
        module.exit_json(changed=True, results="Network {} has been deleted".format(network))


if __name__ == "__main__":
    main()
