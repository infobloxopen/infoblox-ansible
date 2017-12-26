#!/usr/bin/env python
# Copyright (c) 2017 Philip Bove <pgbson@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
---
module: infoblox_host_record
description: 
	- Manage Infoblox Host Records with infoblox-client
version_added: "2.4"
author: "Philip Bove (https://github.com/bandit145)"
options:
	host:
		description:
			- FQDN of Infoblox gridmanager
		required: true
	username:
		description:
			- Username to use for API access
		required: true
	password:
		description:
			- Password to use for API access
		required: true
	validate_certs:
		description:
			- Attempt to validate SSL certs on API endpoint
		required: false
		default: yes
		choices: ['yes','no']
	wapi_version:
		description:
			- WAPI version for NIOS
		required: false
		default: '2.2'
	name:
		description:
			- FQDN of Host Record
		required: true
	mac:
		description:
			- MAC Addresses to use when assigning an IP Address to the Host Record
		required: false
	ip_address:
		description:
			- IP Address to assign to Host Record. Only required if next_avail_ip is not being used Note: IP Addresses can not be updated in place
		required: false
	dns_view:
		description:
			- NIOS DNS view
		required: true
	network_view:
		description:
			- NIOS network view, only required if using next_avail_ip
		required: false
	state:
		description:
			- Desired state of Host Object
		required: false
		choices: ['present','absent']
		default: 'present'
	comment:
		description:
			- Comment of Host Record
		required: false
	ttl:
		description:
			- TTL of Host Record
		required: false
	configure_for_dns:
		description:
			- Configure Host Record for DNS
		required: false
		choices: ['yes','no']
		default: yes
	configure_for_dhcp:
		description:
			- Configure Host Record IP Address for DHCP
		required: false
		choices: ['yes','no']
		default: no
	next_avail_ip:
		description:
			- Use next available IP in a subnet. Note: Requires cidr to be used with
		required: false
	cidr:
		description:
			- CIDR notation of subnet to use next available IP from
		required: false
	extattrs:
		description
			- Extra Attributes for the Host Record (A dict of key value pairs)
			- Example: {"Site":"MySite"}
		required: false
"""

EXAMPLES = """
- name: create host_record
  host: "{{grid_manager}}"
  name: server.test.com
  dns_view: Public
  ip_address: 10.1.10.50
  state: present
  username: test
  password: test
- name: create host_record with next available IP
  host: "{{grid_manager}}"
  name: server.test.com
  next_avail_ip: yes
  cidr: 10.1.10.0/24
  network_view: My_org
  state: present
  username: test
  password: test
- name: remove host_record
  host: "{{grid_manager}}"
  name: server.test.com
  next_avail_ip: yes
  cidr: 10.1.10.0/24
  network_view: My_org
  state: absent
  username: test
  password: test
"""
from ansible.module_utils.basic import *

try:
	from infoblox_client import objects, connector, exceptions
	HAS_INFOBLOX_CLIENT = True
except ImportError:
	HAS_INFOBLOX_CLIENT = False

#determins if address is v4 or v6
def ipv4_or_v6(host_record):
	if hasattr(host_record,'ipv4addr'):
		return host_record.ipv4addr
	else:
		return host_record.ipv6addr

def ea_to_dict(extattrs):
	if extattrs:
		return extattrs.__dict__['_ea_dict']
	else:
		return {}

def is_different(module, host_record, extattrs):
	#if ip address different, fail and inform user
	if module.params['ip_address']:
		if  hasattr(host_record,'ipv4addr') and host_record.ipv4addr != module.params['ip_address']:
			module.fail_json(msg='IP address of a Host Record object cannot be changed')
		elif hasattr(host_record,'ipv6addr') and host_record.ipv6addr != module.params['ip_address']: 
			module.fail_json(msg='IP address of a Host Record object cannot be changed')
	elif module.params['next_avail_ip']:
		module.fail_json(msg='IP address of a Host Record object cannot be changed')
	#if these are different then update
	elif host_record.extattrs != extattrs:
		return True
	else:
		return False


def ensure(module):
	try:
		conn = connector.Connector({'host':module.params['host'],'username':module.params['username'],'password':module.params['password'],
			'ssl_verify':module.params['validate_certs'],'wapi_version':module.params['wapi_version']})
		ip_addr = ip_gen(module)
		host_record = objects.HostRecord.search(conn, name=module.params['name'], view=module.params['dns_view'])
		if module.params['state'] == 'present':
			create_host_record(conn, host_record, module, ip_addr)
		elif module.params['state'] == 'absent':
			delete_host_record(conn, host_record, module)
	except exceptions.InfobloxException as error:
		module.fail_json(msg=str(error))

def delete_host_record(conn, host_record, module):
	try:
		if host_record:
			host_record.delete()
			module.exit_json(changed=True,ip_addr=ipv4_or_v6(host_record), extattrs=ea_to_dict(host_record.extattrs))
		module.exit_json(changed=False)
	except exceptions.InfobloxException as error:
		module.fail_json(msg=str(error))

def create_host_record(conn,host_record, module, ip_addr):
	try:
		if module.params['extattrs']:
			extattrs = objects.EA(module.params['extattrs'])
		else:
			extattrs = None
		if host_record:
			if is_different(module, host_record, extattrs):
				#uncomment to verify that this is indeed making it's way to this
				#module.fail_json(msg='updating...')
				host_record.create(conn, ip=ip_addr, view=module.params['dns_view'], name=module.params['name'],
			configure_for_dns=module.params['configure_for_dns'], ttl=module.params['ttl'], comment=module.params['comment'],
			extattrs=extattrs, update_if_exists=True)

				module.exit_json(changed=True, ip_addr=ipv4_or_v6(host_record),extattrs=ea_to_dict(host_record.extattrs))
			else:
				module.exit_json(changed=False, ip_addr=ipv4_or_v6(host_record),extattrs=ea_to_dict(host_record.extattrs))
		#If host doesn not exist, create
		host_record = objects.HostRecord.create(conn, ip=ip_addr, view=module.params['dns_view'], name=module.params['name'],
			configure_for_dns=module.params['configure_for_dns'], ttl=module.params['ttl'], comment=module.params['comment'],
			extattrs=extattrs)
		module.exit_json(changed=True, ip_addr=ipv4_or_v6(host_record),extattrs=ea_to_dict(host_record.extattrs))
	except exceptions.InfobloxException as error:
		module.fail_json(msg=str(error))

def ip_gen(module):
	if module.params['mac']:
		if module.params['next_avail_ip']:
			next_ip = objects.IPAllocation.next_available_ip_from_cidr(module.params['network_view'],module.params['cidr'])
			ip_addr = objects.IP.create(ip=next_ip, configure_for_dhcp=module.params['configure_for_dhcp'], mac=module.params['mac'])
		else:
			ip_addr = objects.IP.create(ip=module.params['ip_address'], mac=module.params['mac'])
	else:
		if module.params['next_avail_ip']:
			next_ip = objects.IPAllocation.next_available_ip_from_cidr(module.params['network_view'],module.params['cidr'])
			ip_addr = objects.IP.create(ip=next_ip, configure_for_dhcp=module.params['configure_for_dhcp'])
		else:
			ip_addr = objects.IP.create(ip=module.params['ip_address'])
	return ip_addr

def main():
	module = AnsibleModule (
		argument_spec = dict(
			host = dict(type='str' ,required=True),
			name = dict(type='str', required=True),
			mac = dict(type='str', default=None, required=False),
			#required if not using next_avail_ip
			ip_address = dict(type='str',required=False),
			username = dict(type='str', required=True),
			password = dict(type='str', required=True, no_log=True),
			validate_certs = dict(type='bool', default=True,choices=[True,False],required=False),
			dns_view = dict(type='str', required=True),
			network_view = dict(type='str',required=False),
			wapi_version = dict(type='str', default='2.2', required=False),
			state = dict(type='str', default='present',choices = ['present','absent'],required=False),
			comment = dict(type='str', default=None,required=False),
			ttl = dict(default=None, required=False,type='str'),
			configure_for_dns = dict(type='bool', default=True, choices=[True,False],required=False),
			configure_for_dhcp = dict(type='bool',default=False, choices=[True,False], required=False),
			next_avail_ip = dict(type='bool',default=False, choices=[True,False], required=False),
			#required if using next_avail_ip
			cidr = dict(type='str', default=None, required=False),
			extattrs = dict(type='dict',default=None,required=False)
		),
		supports_check_mode=False,
		required_one_of=(['ip_address','next_avail_ip'],)

	)

	if not HAS_INFOBLOX_CLIENT:
		module.fail_json(msg='infoblox-client is not installed.  Please see details here: https://github.com/infobloxopen/infoblox-client')

	if module.params['next_avail_ip']:
		if not module.params['cidr'] or not module.params['network_view']:
			module.fail_json(msg='"cidr" and "network_view" are required when using "next_avail_ip"')

	ensure(module)


if __name__ == '__main__':
	main()