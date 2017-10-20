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

def create_host_record(module):
	try:
		conn = connector.Connector({'host':module.params['host'],'username':module.params['username'],'password':module.params['password'],
			'ssl_verify':module.params['validate_certs'],'wapi_version':module.params['wapi_version']})
		if module.params['mac']:
			ip_addr = objects.IP(ip=module.params['ip_address'], mac=module.params['mac'])
		else:
			ip_addr = objects.IP(ip=module.params['ip_address'])

		check_host_record = objects.HostRecord.search(conn, ip=ip_addr, view=module.params['view'])
		print(check_host_record)
		if module.params['state'] == 'present':
			#If host record exists check if there is a difference between what is specified in ansible
			#and what is in the host record, if their is an update use .create with update_if_exists=True
			if check_host_record:
				#_ipv4addrs contains a list (of seeminlg duplicate info) that prevents casting to set
				del host_record_info['_ipv4addrs']
				specified_info = set(module.params.values())
				host_record_info = set(check_host_record.__dict__.values())
				print(host_record_info)
				resultant_set = specified_info - host_record_info
				if len(resultant_set) > 0:
					host_record = objects.HostRecord.create(conn, ip=ip_addr, view=module.params['view'], name=module.params['name'],
					configure_for_dns=module.params['configure_for_dns'], comment=module.params['comment'], ttl=module.params['ttl'], update_if_exists=True)
				else:
					module.exit_json(changed=False)
			#If host doesn not exist, create
			else:
				host_record = objects.HostRecord.create(conn, ip=ip_addr, view=module.params['view'], name=module.params['name'],
					configure_for_dns=module.params['configure_for_dns'], ttl=module.params['ttl'], comment=module.params['comment'])
			module.exit_json(changed=True)
		#If absent is speciefed remove if record exists
		elif module.params['state'] == 'absent':
			if not check_host_record:
				module.exit_json(changed=False)
			else:
				host_record = objects.HostRecord.search(conn, ip=ip_addr, view=module.params['view'])
				host_record.delete()
				module.exit_json(changed=True)
	except exceptions.InfobloxException as error:
		module.fail_json(msg=str(error))



def main():
	module = AnsibleModules (
		argument_spec = dict(
			host = dict(required=True),
			name = dict(required=True),
			mac = dict(default=None),
			ip_address = dict(required=True),
			username = dict(required=True),
			password = dict(required=True),
			validate_certs = dict(default=True,choices=[True,False]),
			view = dict(required=True),
			wapi_version = dict(default='2.2'),
			state = dict(default='present',choices = ['present','absent']),
			comment = dict(default=''),
			ttl = dict(default=None),
			configure_for_dns = dict(default=True, choices[True,False])
		)

	)
	create_host_record(module)


if __name__ == '__main__':
	main()