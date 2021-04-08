# Infoblox Ansible Collections for vNIOS

About 
======

Infoblox Ansible Collection for vNIOS allows managing your NIOS objects
through APIs.
It, thus, enables the DNS and IPAM automation of VM workloads that are
deployed across multiple platforms. The `nios_modules` collection
provides modules and plugins for managing the networks, IP addresses,
and DNS records in NIOS. This collection is hosted on Ansible Galaxy
under `infoblox.nios_modules`.

Modules Overview:
=================

The `infoblox.nios_modules` collection has the following content:

Modules:
--------

-   `nios_a_record` – Configure Infoblox NIOS A records

-   `nios_aaaa_record` – Configure Infoblox NIOS AAAA records

-   `nios_cname_record` – Configure Infoblox NIOS CNAME records

-   `nios_dns_view` – Configure Infoblox NIOS DNS views

-   `nios_fixed_address` – Configure Infoblox NIOS DHCP Fixed Address

-   `nios_host_record` – Configure Infoblox NIOS host records

-   `nios_member` – Configure Infoblox NIOS members

-   `nios_mx_record` – Configure Infoblox NIOS MX records

-   `nios_naptr_record` – Configure Infoblox NIOS NAPTR records

-   `nios_network` – Configure Infoblox NIOS network object

-   `nios_network_view` – Configure Infoblox NIOS network views

-   `nios_nsgroup` – Configure Infoblox DNS Nameserver Groups

-   `nios_ptr_record` – Configure Infoblox NIOS PTR records

-   `nios_srv_record` – Configure Infoblox NIOS SRV records

-   `nios_txt_record` – Configure Infoblox NIOS txt records

-   `nios_zone` – Configure Infoblox NIOS DNS zones

Plugins:
--------

-   `nios_inventory`: List all the hosts with records created in NIOS

-   `nios_lookup`: Look up queries for NIOS database objects

-   `nios_next_ip`: Returns the next available IP address for a network

-   `nios_next_network`: Returns the next available network addresses
    for a given network CIDR

Installation 
=============

Dependencies
------------

-   Python version 2.7 and above

-   Ansible version 2.9.0 or above

-   NIOS 8.2.4 and above

Prerequisites
-------------

You need to install the infoblox-client package. To install
infoblox-client WAPI package, run the following command:

```shell
$ pip install infoblox-client
```

Installation of nios\_modules Collection
----------------------------------------

The `nios_modules` collection can be installed either from Ansible Galaxy
or directly from git. It is recommended to install collections from
Ansible Galaxy as those are more stable than the ones in the git
branch.

### Installation from Ansible Galaxy

To directly install the `nios_modules` collection from Ansible Galaxy,
run the following command:

```shell
$ ansible-galaxy collection install infoblox.nios_modules
```

The collection folder would be installed at
`~/.ansible/collections/ansible_collections/infoblox/nios_modules`

### Installation from Git

To git clone and install from this repo, follow these steps:

-   **Clone the repo:**

```shell
$ git clone https://github.com/infobloxopen/infoblox-ansible.git
```

-   **Build the collection:**

    To build a collection, run the following command from inside the
    root directory of the collection:
    
```shell
$ ansible-galaxy collection build
```

This creates a tarball of the built collection in the current directory.

-   **Install the collection:**

```shell
$ ansible-galaxy collection install <collection-name>.tar.gz -p ./collections
```

Please refer to our Ansible [deployment
guide](https://www.infoblox.com/wp-content/uploads/infoblox-deployment-guide-infoblox-and-ansible-integration.pdf)
for more details.

Current release
=========

1.0.2 on 27 January 2021

Versioning
=========

-   galaxy.yml in the master branch will always contain the version of the current major or minor release. It will be updated right after a release.
-   version_added needs to be used for every new feature and module/plugin, and needs to coincide with the next minor/major release version. (This will eventually be enforced by CI.)

Resources
=========

-   Infoblox [NIOS
    modules](https://docs.ansible.com/ansible/latest/scenario_guides/guide_infoblox.html)
    on Ansible documentation

-   Infoblox [workspace](https://galaxy.ansible.com/infoblox) in Ansible
    Galaxy

-   Infoblox Ansible [deployment
    guide](https://www.infoblox.com/wp-content/uploads/infoblox-deployment-guide-infoblox-and-ansible-integration.pdf)

License
=======

This code is published under `GPL v3.0`

[COPYING](https://github.com/infobloxopen/infoblox-ansible/blob/master/COPYING)

Issues or RFEs
===============
You can open an issue or request for enhancement
[here](https://github.com/infobloxopen/infoblox-ansible/issues)
