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
	HAS_INFOBLOX_CLIENT = True
except ImportError:
	HAS_INFOBLOX_CLIENT = False

def is_different(module, host_record):
	#checking easiest flags
	host_record_info = host_record.__dict__
	if  'ipv4addr' in host_record_info and host_record_info['ipv4addr'] != module.params['ip_address']:
		return True
	elif 'ipv6addr' in host_record_info and host_record_info['ipv6addr'] != module.params['ip_address']: 
		return True
	elif host_record_info['comment'] != module.params['comment']:
		return	True
	elif host_record_info['extattrs'] != host_record_info['extattrs']:
		return True
	elif host_record_info['ttl'] != module.params['ttl']:
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
			module.exit_json(changed=True)
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
			if is_different(module, host_record):
				#uncomment to verify that this is indeed making it's way to this
				#module.fail_json(msg='updating...')
				host_record.create(conn, ip=ip_addr, view=module.params['dns_view'], name=module.params['name'],
			configure_for_dns=module.params['configure_for_dns'], ttl=module.params['ttl'], comment=module.params['comment'],
			extattrs=extattrs, update_if_exists=True)

				module.exit_json(changed=True, ip_addr=host_record.ipv4addr,
					mac=host_record.mac,ttl=host_record.ttl,comment=host_record.comment, extattrs=host_record.extattrs,
					configure_for_dns=host_record.configure_for_dns)
			else:
				module.exit_json(changed=False, ip_addr=host_record.ipv4addr,
					mac=host_record.mac,ttl=host_record.ttl,comment=host_record.comment, extattrs=host_record.extattrs,
					configure_for_dns=host_record.configure_for_dns)
		#If host doesn not exist, create
		host_record = objects.HostRecord.create(conn, ip=ip_addr, view=module.params['dns_view'], name=module.params['name'],
			configure_for_dns=module.params['configure_for_dns'], ttl=module.params['ttl'], comment=module.params['comment'],
			extattrs=extattrs)
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
			ip_address = dict(type='str',required=False),
			username = dict(type='str', required=True),
			password = dict(type='str', required=True, no_log=True),
			validate_certs = dict(type='bool', default=True,choices=[True,False]),
			dns_view = dict(type='str', required=True),
			network_view = dict(type='str',required=False),
			wapi_version = dict(type='str', default='2.2'),
			state = dict(type='str', default='present',choices = ['present','absent']),
			comment = dict(type='str', default=None,required=False),
			ttl = dict(default=None, required=False,type='str'),
			configure_for_dns = dict(type='bool', default=True, choices=[True,False]),
			configure_for_dhcp = dict(type='bool',default=False, choices=[True,False]),
			next_avail_ip = dict(type='bool',default=False, choices=[True,False]),
			#required if using next_avail_ip
			cidr = dict(type='str', default=None),
			extattrs = dict(type='dict',default=None)
		),
		supports_check_mode=False,
		required_one_of=(['ip_address','next_avail_ip'],)

	)

	if not HAS_INFOBLOX_CLIENT:
		module.fail_json(msg='infoblox-client is not installed.  Please see details here: https://github.com/infobloxopen/infoblox-client')

	if module.params['next_avail_ip']:
		if not module.params['cidr'] or not module.params['network_view']:
			module.fail_json(msg='"cidr" is required when using "next_avail_ip"')

	ensure(module)


if __name__ == '__main__':
	main()