#!/usr/bin/env python
# Copyright (c) 2017 Philip Bove
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import *

try:
	from infoblox_client import objects
	from infoblox_client import connector
except ImportError:
	raise Exception('infoblox-client is not installed.  Please see details here: https://github.com/infobloxopen/infoblox-client')

def parse_exattrs(module):

def ensure(module):
	conn = connector.Connector({'host':module.params['host'],'username':module.params['username'],'password':module.params['password'],
			'ssl_verify':module.params['validate_certs'],'wapi_version':module.params['wapi_version']})
	a_record = objects.ARecord.search(conn,name=module.params['name'], view=module.params['view'])

def create_a_record(module, conn, a_record):


def delete_a_record(module, conn,a_record):


def main():
	module = AnsibleModules(
			argument_spec(
				host=dict(required=True),
				name=dict(required=True),
				ip_address=dict(required=True),
				view=dict(required=True),
				extattrs=dict(type='dict'),
				validate_certs=dict(type='boolean', default=True,choices=[True,False]),
				wapi_version=dict(type='str', default='2.2')
			),
			supports_check_mode=False
		)
	ensure(module)

if __name__ == '__main__':
	main()