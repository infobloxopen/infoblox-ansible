#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_host_record
author: "Peter Sprygada (@privateip)"
short_description: Configure Infoblox NIOS host records
version_added: "1.0.0"
description:
  - Adds and/or removes instances of host record objects from
    Infoblox NIOS servers.  This module manages NIOS C(record:host) objects
    using the Infoblox WAPI interface over REST.
  - Updates instances of host record object from Infoblox NIOS servers.
requirements:
  - infoblox-client
extends_documentation_fragment: infoblox.nios_modules.nios
notes:
    - This module supports C(check_mode).
    - >
      In collection versions that include PR #329 (fixes issue #108), re-running
      a task with the same hostname and a different IP updates the matching host
      record without creating, displacing, or modifying unrelated records.
    - >
      In collection versions that include PR #329 (fixes issue #160), aliases
      supplied as short (relative) names are normalized to FQDNs before
      comparison on DNS-enabled hosts, preventing false C(changed=True) on
      re-runs.
    - >
      In collection versions that include PR #329 (fixes issue #63), host
      records using C(nios_next_ip) for dynamic IP allocation are idempotent on
      re-runs; when the desired IP is already allocated, no additional
      allocation call is made.
    - >
      In collection versions that include PR #329 (fixes issue #108),
      C(use_for_ea_inheritance) defaults are excluded from idempotency
      comparison to prevent spurious C(changed=True) on re-runs.
options:
  name:
    description:
      - Specifies the fully qualified hostname to add or remove from
        the system. User can also update the hostname as it is possible
        to pass a dict containing I(new_name), I(old_name). See examples.
    type: str
    required: true
  view:
    description:
      - Sets the DNS view to associate this host record with.  The DNS
        view must already be configured on the system.
    type: str
    default: default
    aliases:
      - dns_view
  configure_for_dns:
    description:
      - Sets the DNS to particular parent. If user needs to bypass DNS
        user can make the value to false.
    type: bool
    default: true
    aliases:
      - dns
  use_dns_ea_inheritance:
    version_added: "1.7.0"
    description:
      - When use_dns_ea_inheritance is true, the EA is inherited from associated zone. The default value is false.
    type: bool
    default: false
  ipv4addrs:
    description:
      - Configures the IPv4 addresses for this host record.  This argument
        accepts a list of values (see suboptions).
    type: list
    elements: dict
    aliases:
      - ipv4
    suboptions:
      use_for_ea_inheritance:
        version_added: "1.7.0"
        description:
            - When use_for_ea_inheritance is true, the EA is inherited from Host address. The default value is false.
        type: bool
        default: false
        required: false
      ipv4addr:
        description:
          - Configures the IPv4 address for the host record. Users can dynamically
            allocate ipv4 address to host record by passing dictionary containing,
            I(nios_next_ip) and I(CIDR network range). It supports _object_function
            calls to dynamic select an ipv4address from a network/dhcp-range and
            exclude a list of IPs from the selection. If user wants to add or
            remove the ipv4 address from existing record, I(add/remove)
            params need to be used. See examples.
        type: str
        required: true
        aliases:
          - address
      configure_for_dhcp:
        description:
          - Configure the host_record over DHCP instead of DNS, if user
            changes it to true, user need to mention MAC address to configure.
        type: bool
        required: false
        aliases:
          - dhcp
      mac:
        description:
          - Configures the hardware MAC address for the host record. If user makes
            DHCP to true, user need to mention MAC address.
        type: str
        required: false
        aliases:
          - mac
      add:
        version_added: "1.0.0"
        description:
          - If user wants to add the ipv4 address to an existing host record.
            Note that with I(add) user will have to keep the I(state) as I(present),
            as new IP address is allocated to existing host record. See examples.
        type: bool
        required: false
        aliases:
          - add
      use_nextserver:
        version_added: "1.0.0"
        description:
          - Enable the use of the nextserver option
        type: bool
        required: false
        aliases:
          - use_pxe
      nextserver:
        version_added: "1.0.0"
        description:
          - Takes as input the name in FQDN format and/or IPv4 Address of
            the next server that the host needs to boot from.
        type: str
        required: false
        aliases:
          - pxe
      remove:
        version_added: "1.0.0"
        description:
          - If user wants to remove the ipv4 address from an existing host record.
            Note that with I(remove) user will have to change the I(state) to I(absent),
            as IP address is de-allocated from an existing host record. See examples.
        type: bool
        required: false
        aliases:
          - remove
  ipv6addrs:
    description:
      - Configures the IPv6 addresses for the host record.  This argument
        accepts a list of values (see options).
    type: list
    elements: dict
    aliases:
      - ipv6
    suboptions:
      ipv6addr:
        description:
          - Configures the IPv6 address for the host record.
        type: str
        required: true
        aliases:
          - address
      configure_for_dhcp:
        description:
          - Configure the host_record over DHCP instead of DNS, if user
            changes it to true, user need to mention DUID address to configure.
        type: bool
        required: false
        aliases:
          - dhcp
      duid:
        description:
          - Configures the hardware DUID address for the host record. If user makes
            DHCP to true, user need to mention DUID address.
        type: str
        required: false
        aliases:
          - duid
  aliases:
    description:
      - Configures an optional list of additional aliases to add to the host
        record. These are equivalent to CNAMEs but held within a host
        record. Must be in list format.
      - >
        In collection versions that include PR #329 (fixes issue #160), short
        (relative) alias names are normalized to FQDNs on DNS-enabled hosts
        before idempotency comparison, so short and FQDN forms produce the
        same result on re-runs.
    type: list
    elements: str
  ttl:
    description:
      - Configures the TTL to be associated with this host record.
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
    type: str
    default: present
    choices:
      - present
      - absent
'''

EXAMPLES = '''
- name: Configure an ipv4 host record
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    ipv4:
      - address: 192.168.10.1
    aliases:
      - cname.ansible.com
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Add a comment to an existing host record
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    ipv4:
      - address: 192.168.10.1
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove a host record from the system
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Update an ipv4 host record
  infoblox.nios_modules.nios_host_record:
    name: {new_name: host-new.ansible.com, old_name: host.ansible.com}
    ipv4:
      - address: 192.168.10.1
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create an ipv4 host record bypassing DNS
  infoblox.nios_modules.nios_host_record:
    name: new_host
    ipv4:
      - address: 192.168.10.1
    dns: false
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create an ipv4 host record over DHCP
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    ipv4:
      - address: 192.168.10.1
        dhcp: true
        mac: 00-80-C8-E3-4C-BD
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create an ipv4 host record with DNS EA inheritance enabled
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    configure_for_dns: true
    use_dns_ea_inheritance: true
    ipv4:
      - address: 192.168.10.1
        dhcp: true
        mac: 00-80-C8-E3-4C-BD
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create an ipv4 host record with host address EA inheritance enabled
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    configure_for_dns: true
    ipv4:
      - address: 192.168.10.1
        dhcp: true
        mac: 00-80-C8-E3-4C-BD
        use_for_ea_inheritance: true
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create an ipv4 host record over DHCP with PXE server
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    ipv4:
      - address: 192.168.10.1
        dhcp: true
        mac: 00-80-C8-E3-4C-BD
        use_nextserver: true
        nextserver: pxe-server.com
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local


- name: Dynamically add host record to next available ip
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    ipv4:
      - address: {nios_next_ip: 192.168.10.0/24}
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: >
    Dynamically add host record to next available ip in
    a network and excluding a list of IPs
    see https://ipam.illinois.edu/wapidoc/objects/record.host_ipv4addr.html
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    ipv4:
      - address:
        _object_function: next_available_ip
        _parameters:
          exclude: ['192.168.10.1', '192.168.10.2', '192.168.10.3'],
        _result_fields: ips
        _object: network
        _object_parameters:
          network: 192.168.10.0/24
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Add ip to host record
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    ipv4:
      - address: 192.168.10.2
        add: true
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove ip from host record
  infoblox.nios_modules.nios_host_record:
    name: host.ansible.com
    ipv4:
      - address: 192.168.10.1
        remove: true
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Create host record with IPv4 and IPv6 addresses
  infoblox.nios_modules.nios_host_record:
    name: hostrec.ansible.com
    ipv4:
      - address: 192.168.10.7
        mac: 12:80:C8:E3:4C:AB
    ipv6:
      - address: fe80::10
        duid: 12:80:C8:E3:4C:B4
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
    connection: local
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.api import WapiModule
from ..module_utils.api import NIOS_HOST_RECORD
from ..module_utils.api import normalize_ib_spec


def ipaddr(module, key, filtered_keys=None):
    ''' Transforms the input value into a struct supported by WAPI
    This function will transform the input from the playbook into a struct
    that is valid for WAPI in the form of:
        {
            ipv4addr: <value>,
            mac: <value>
        }
    This function does not validate the values are properly formatted or in
    the acceptable range, that is left to WAPI.
    '''
    if module.params.get(key) is None:
        return None
    filtered_keys = filtered_keys or list()
    objects = list()
    for item in module.params[key]:
        objects.append(dict([(k, v) for k, v in item.items() if v is not None and k not in filtered_keys]))
    return objects


def ipv4addrs(module):
    return ipaddr(module, 'ipv4addrs', filtered_keys=['address', 'dhcp', 'pxe', 'use_pxe'])


def ipv6addrs(module):
    return ipaddr(module, 'ipv6addrs', filtered_keys=['address', 'dhcp'])


def normalize_aliases(module):
    '''Normalize host record aliases to FQDNs.

    NIOS/WAPI expands short (relative) aliases to FQDNs **only on DNS-enabled
    hosts** (``configure_for_dns=True``). For example, ``myalias`` becomes
    ``myalias.example.com`` on a DNS host, but is stored as-is on a DNS-disabled
    (IPAM-only) host.

    Without this normalization, the idempotency check in ``compare_objects()``
    compares the user-supplied short name against the FQDN returned by WAPI
    and always reports ``changed=True`` (issue #160).

    Short names (those containing no dots) on DNS-enabled hosts are expanded by
    appending the zone extracted from the host ``name`` parameter. Aliases that
    already contain at least one dot, or those on DNS-disabled hosts, are
    returned unchanged.
    '''
    aliases = module.params.get('aliases')
    if not aliases:
        return None

    # WAPI only expands aliases on DNS-enabled hosts.
    configure_for_dns = module.params.get('configure_for_dns', True)
    if not configure_for_dns:
        return aliases

    host_name = module.params.get('name', '')
    dot_idx = host_name.find('.')
    zone = host_name[dot_idx + 1:] if dot_idx != -1 else ''

    normalized = []
    for alias in aliases:
        if zone and '.' not in alias:
            normalized.append('{}.{}'.format(alias, zone))
        else:
            normalized.append(alias)
    return normalized


def supports_dns_ea_inheritance(wapi_version):
    '''Return True if the given WAPI version supports the use_dns_ea_inheritance field.

    The field was introduced in WAPI 2.12.3 and 2.13.4 (patch releases).
    Any WAPI major version > 2 is assumed to support the feature.
    A missing patch component is treated as 0 (e.g. ``'2.14'`` → ``2.14.0``),
    so users who specify wapi_version as MAJOR.MINOR are handled correctly.
    '''
    parts = wapi_version.split('.')
    try:
        major, minor = int(parts[0]), int(parts[1])
        patch = int(parts[2]) if len(parts) >= 3 else 0
    except (IndexError, ValueError):
        return False
    if major != 2:
        return major > 2
    min_patch = {12: 3, 13: 4}.get(minor, 0 if minor > 13 else None)
    return min_patch is not None and patch >= min_patch


def should_warn_ignored_dns_ea_inheritance(wapi_version, use_dns_ea_inheritance):
    '''Return True if use_dns_ea_inheritance was explicitly enabled but the
    WAPI version does not support it, meaning the field will be silently ignored.
    '''
    return not supports_dns_ea_inheritance(wapi_version) and bool(use_dns_ea_inheritance)


def main():
    ''' Main entry point for module execution
    '''
    ipv4addr_spec = dict(
        ipv4addr=dict(required=True, aliases=['address']),
        configure_for_dhcp=dict(type='bool', required=False, aliases=['dhcp']),
        mac=dict(required=False),
        add=dict(type='bool', required=False),
        use_nextserver=dict(type='bool', required=False, aliases=['use_pxe']),
        nextserver=dict(required=False, aliases=['pxe']),
        use_for_ea_inheritance=dict(type='bool', required=False, default=False),
        remove=dict(type='bool', required=False)
    )

    ipv6addr_spec = dict(
        ipv6addr=dict(required=True, aliases=['address']),
        configure_for_dhcp=dict(type='bool', required=False, aliases=['dhcp']),
        duid=dict(required=False)
    )

    ib_spec = dict(
        name=dict(required=True, ib_req=True),
        view=dict(default='default', aliases=['dns_view'], ib_req=True),

        ipv4addrs=dict(type='list', aliases=['ipv4'], elements='dict', options=ipv4addr_spec, transform=ipv4addrs),
        ipv6addrs=dict(type='list', aliases=['ipv6'], elements='dict', options=ipv6addr_spec, transform=ipv6addrs),
        configure_for_dns=dict(type='bool', default=True, required=False, aliases=['dns'], ib_req=True),
        use_dns_ea_inheritance=dict(type='bool', default=False, required=False),
        aliases=dict(type='list', elements='str', transform=normalize_aliases),

        ttl=dict(type='int'),

        extattrs=dict(type='dict'),
        comment=dict(),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(normalize_ib_spec(ib_spec))
    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    effective_ib_spec = ib_spec.copy()
    # Default WAPI version matches the lowest version where use_dns_ea_inheritance
    # is supported (2.12.3). If provider.wapi_version is omitted we assume the
    # field is available; users running older WAPI must set wapi_version
    # explicitly to receive the warn-and-strip behavior below.
    provider_wapi_version = (module.params.get('provider') or {}).get('wapi_version', '2.12.3')
    if not supports_dns_ea_inheritance(provider_wapi_version):
        if should_warn_ignored_dns_ea_inheritance(provider_wapi_version,
                                                  module.params.get('use_dns_ea_inheritance')):
            module.warn(
                'use_dns_ea_inheritance is not supported for WAPI version %s. '
                'Minimum supported versions are 2.12.3 and 2.13.4. '
                'The field will be ignored.' % provider_wapi_version
            )
        effective_ib_spec.pop('use_dns_ea_inheritance', None)

    wapi = WapiModule(module)
    result = wapi.run(NIOS_HOST_RECORD, effective_ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
