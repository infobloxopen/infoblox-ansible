===================================
Infoblox.Nios_Modules Release Notes
===================================

.. contents:: Topics


v1.1.0
======

Release Summary
---------------

This release provides plugins for NIOS DTC

New Modules
-----------

- infoblox.nios_modules.nios_dtc_lbdn - Configure Infoblox NIOS DTC LBDN
- infoblox.nios_modules.nios_dtc_pool - Configure Infoblox NIOS DTC Pool
- infoblox.nios_modules.nios_dtc_server - Configure Infoblox NIOS DTC Server
- infoblox.nios_modules.nios_restartservices - Restart grid services.

v1.0.2
======

Release Summary
---------------

This release provides compatibilty for Ansible v3.0.0

Minor Changes
-------------

- Fixed the ignored sanity errors required for Ansible 3.0.0 collection
- Made it compatible for Ansible v3.0.0

v1.0.1
======

Release Summary
---------------

This release provides compatibilty for Ansible v3.0.0

Minor Changes
-------------

- Made it compatible for Ansible v3.0.0

v1.0.0
======

Release Summary
---------------

First release of the `nios_modules` collection! This release includes multiple plugins:- an `api` plugin, a `network` plugin, a `nios` plugin, a `nios_inventory` plugin, a `lookup plugin`, a `nios_next_ip` plugin, a `nios_next_network` plugin 

New Plugins
-----------

Lookup
~~~~~~

- infoblox.nios_modules.nios - Query Infoblox NIOS objects
- infoblox.nios_modules.nios_next_ip - Return the next available IP address for a network
- infoblox.nios_modules.nios_next_network - Return the next available network range for a network-container

New Modules
-----------

- infoblox.nios_modules.nios_a_record - Configure Infoblox NIOS A records
- infoblox.nios_modules.nios_aaaa_record - Configure Infoblox NIOS AAAA records
- infoblox.nios_modules.nios_cname_record - Configure Infoblox NIOS CNAME records
- infoblox.nios_modules.nios_dns_view - Configure Infoblox NIOS DNS views
- infoblox.nios_modules.nios_fixed_address - Configure Infoblox NIOS DHCP Fixed Address
- infoblox.nios_modules.nios_host_record - Configure Infoblox NIOS host records
- infoblox.nios_modules.nios_member - Configure Infoblox NIOS members
- infoblox.nios_modules.nios_mx_record - Configure Infoblox NIOS MX records
- infoblox.nios_modules.nios_naptr_record - Configure Infoblox NIOS NAPTR records
- infoblox.nios_modules.nios_network - Configure Infoblox NIOS network object
- infoblox.nios_modules.nios_network_view - Configure Infoblox NIOS network views
- infoblox.nios_modules.nios_nsgroup - Configure Infoblox NIOS Nameserver Groups
- infoblox.nios_modules.nios_ptr_record - Configure Infoblox NIOS PTR records
- infoblox.nios_modules.nios_srv_record - Configure Infoblox NIOS SRV records
- infoblox.nios_modules.nios_txt_record - Configure Infoblox NIOS txt records
- infoblox.nios_modules.nios_zone - Configure Infoblox NIOS DNS zones
