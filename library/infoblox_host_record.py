#!/usr/bin/env python

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
  ipaddresses: 10.1.10.50
  username: test
  password: test
"""
from ansible.module_utils.basic import *

try:
	from infoblox_client import objects
	from infoblox_client import connector
except ImportError:
	module.fail_json(msg="infoblox-client is required to use infoblox_ modules")

def create_host_record(module):
	try:
		conn = connector.Connector({'host':module.params['host'],'username':module.params['username'],'password':module.params['password'],
			'ssl_verify':module.params['validate_certs'],'wapi_version':module.params['wapi_version']})
		if module.params['mac']:
			ip_addr = objects.IP(ip=module.params['ip_address'], mac=module.params['mac'])
		else:
			ip_addr = objects.IP(ip=module.params['ip_address'])

		check_host_record = objects.HostRecord.search(conn, ip=ip_addr, view=module.params['view'])
		if module.params['state'] == 'present':
			if check_host_record:
				module.exit_json(changed=False)
			host_record = objects.HostRecord.create(conn, ip=ip_addr, view=module.params['view'], name=module.params['name'],
				configure_for_dns=module.params['configure_for_dns'], comment=module.params['comment'])
			module.exit_json(changed=True)
		elif module.params['state'] == 'absent':
			if not check_host_record:
				module.exit_json(changed=False)
			host_record = objects.HostRecord.search(conn, ip=ip_addr, view=module.params['view'])
			host_record.delete()
			module.exit_json(changed=True)




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
			configure_for_dns = dict(default=True, choices[True,False])
		)

	)


if __name__ == '__main__':
	main()