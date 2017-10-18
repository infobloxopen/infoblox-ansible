#!/usr/bin/env python


from ansible.module_utils.basic import *

try:
	from infoblox_client import objects
	from infoblox_client import connector
except ImportError:
	raise Exception('infoblox-client is not installed.  Please see details here: https://github.com/infobloxopen/infoblox-client')


def create_a_record(module):


def main():

if __name__ == '__main__':
	main()