# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
---
name: nios_next_ip
short_description: Return the next available IP address for a network
version_added: "1.0.0"
description:
  - Uses the Infoblox WAPI API to return the next available IP addresses
    for a given network CIDR
requirements:
  - infoblox-client

options:
    _terms:
      description: The CIDR network to retrieve the next address(es) from.
      required: True
      type: str
    num:
      description: The number of IP address(es) to return.
      required: false
      default: 1
      type: int
    exclude:
      description: List of IP's that need to be excluded from returned IP addresses.
      required: false
      type: list
      elements: str
'''

EXAMPLES = """
- name: return next available IP address for network 192.168.10.0/24
  ansible.builtin.set_fact:
    ipaddr: "{{ lookup('infoblox.nios_modules.nios_next_ip', '192.168.10.0/24', provider={'host': 'nios01', 'username': 'admin', 'password': 'password'}) }}"

- name: return the next 3 available IP addresses for network 192.168.10.0/24
  ansible.builtin.set_fact:
    ipaddr: "{{ lookup('infoblox.nios_modules.nios_next_ip', '192.168.10.0/24', num=3,
                provider={'host': 'nios01', 'username': 'admin', 'password': 'password'}) }}"

- name: return the next 3 available IP addresses for network 192.168.10.0/24 excluding ip addresses - ['192.168.10.1', '192.168.10.2']
  ansible.builtin.set_fact:
    ipaddr: "{{ lookup('infoblox.nios_modules.nios_next_ip', '192.168.10.0/24', num=3, exclude=['192.168.10.1', '192.168.10.2'],
                provider={'host': 'nios01', 'username': 'admin', 'password': 'password'}) }}"

- name: return next available IP address for network fd30:f52:2:12::/64
  ansible.builtin.set_fact:
    ipaddr: "{{ lookup('infoblox.nios_modules.nios_next_ip', 'fd30:f52:2:12::/64', provider={'host': 'nios01', 'username': 'admin', 'password': 'password'}) }}"
"""

RETURN = """
_list:
  description:
    - The list of next IP addresses available
  returned: always
  type: list
"""

from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_text
from ansible.errors import AnsibleError
from ..module_utils.api import WapiLookup
import ipaddress


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        try:
            network = terms[0]
        except IndexError:
            raise AnsibleError('missing argument in the form of A.B.C.D/E')

        provider = kwargs.pop('provider', {})
        wapi = WapiLookup(provider)

        if isinstance(ipaddress.ip_network(network), ipaddress.IPv6Network):
            network_obj = wapi.get_object('ipv6network', {'network': network})
        else:
            network_obj = wapi.get_object('network', {'network': network})

        if network_obj is None:
            raise AnsibleError('unable to find network object %s' % network)

        num = kwargs.get('num', 1)
        exclude_ip = kwargs.get('exclude', [])

        try:
            ref = network_obj[0]['_ref']
            avail_ips = wapi.call_func('next_available_ip', ref, {'num': num, 'exclude': exclude_ip})
            return [avail_ips['ips']]
        except Exception as exc:
            raise AnsibleError(to_text(exc))
