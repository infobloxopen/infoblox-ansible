#!/usr/bin/env python
# Copyright (c) 2017 Philip Bove
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
module: infoblox_host_record
description: manage infoblox host records with infoblox-client
version_added: "2.4"
"""

EXAMPLES = """
- name: create host_record
  host: "{{grid_manager}}"
  name: server.test.com
  mac: macaddr
  ip_address: 10.1.10.50
  username: test
  password: test
"""
from ansible.module_utils.basic import *

try:
	from infoblox_client import objects, connector, exceptions
except ImportError:
	raise Exception('infoblox-client is not installed.  Please see details here: https://github.com/infobloxopen/infoblox-client')

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
			module.exit_json(changed=True)
		module.exit_json(changed=False)
	except exceptions.InfobloxException as error:
		module.fail_json(msg=str(error))

def create_host_record(conn,host_record, module, ip_addr):
	try:
		#If host record exists check if there is a difference between what is specified in ansible
		#and what is in the host record, if their is an update use .create with update_if_exists=True
		if host_record:
			#_ipv4addrs contains a list (of seeming;y duplicate info) that prevents casting to set
			if module.params['ip_address'] != host_record.ipv4addr:
				host_record.delete()
			else:
				module.exit_json(changed=False, ip_addr=host_record.ipv4addr)
		#If host doesn not exist, create
	
		host_record = objects.HostRecord.create(conn, ip=ip_addr, view=module.params['dns_view'], name=module.params['name'],
			configure_for_dns=module.params['configure_for_dns'], ttl=module.params['ttl'], comment=module.params['comment'])
		module.exit_json(changed=True, ip_addr=host_record.ipv4addr, ref=host_record.ref)
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
			mac = dict(type='str', default=None),
			#required if not using next_avail_ip
			ip_address = dict(type='str'),
			username = dict(type='str', required=True),
			password = dict(type='str', required=True, no_log=True),
			validate_certs = dict(type='bool', default=True,choices=[True,False]),
			dns_view = dict(type='str', required=True),
			network_view = dict(type='str'),
			wapi_version = dict(type='str', default='2.2'),
			state = dict(type='str', default='present',choices = ['present','absent']),
			comment = dict(type='str', default=''),
			ttl = dict(default=None),
			configure_for_dns = dict(type='bool', default=True, choices=[True,False]),
			configure_for_dhcp = dict(type='bool',default=False, choices=[True,False]),
			next_avail_ip = dict(type='bool',default=False, choices=[True,False]),
			#required if using next_avail_ip
			cidr = dict(type='str')
		),
		supports_check_mode=False

	)
	if module.params['next_avail_ip']:
		if not module.params['cidr'] or not module.params['network_view']:
			module.fail_json(msg='"cidr" is required when using "next_avail_ip"')
	else:
		
		if not module.params['ip_address']:
			module.fail_json(msg='"ip_address" is required when not using "next_avail_ip"')

	ensure(module)


if __name__ == '__main__':
	main()