**Infoblox Ansible Collections for vNIOS**

About
=====

Infoblox Ansible Collection for vNIOS allows managing your NIOS objects
through APIs.\
It, thus, enables the DNS and IPAM automation of VM workloads that are
deployed across multiple platforms. The nios\_modules collection
provides modules and plugins for managing the networks, IP addresses,
and DNS records in NIOS. This collection is hosted on Ansible Galaxy
under infoblox.nios\_modules.

Modules Overview:
=================

The infoblox.nios\_modules collection has the following content:

Modules:
--------

-   nios\_a\_record – Configure Infoblox NIOS A records

-   nios\_aaaa\_record – Configure Infoblox NIOS AAAA records

-   nios\_cname\_record – Configure Infoblox NIOS CNAME records

-   nios\_dns\_view – Configure Infoblox NIOS DNS views

-   nios\_fixed\_address – Configure Infoblox NIOS DHCP Fixed Address

-   nios\_host\_record – Configure Infoblox NIOS host records

-   nios\_member – Configure Infoblox NIOS members

-   nios\_mx\_record – Configure Infoblox NIOS MX records

-   nios\_naptr\_record – Configure Infoblox NIOS NAPTR records

-   nios\_network – Configure Infoblox NIOS network object

-   nios\_network\_view – Configure Infoblox NIOS network views

-   nios\_nsgroup – Configure Infoblox DNS Nameserver Groups

-   nios\_ptr\_record – Configure Infoblox NIOS PTR records

-   nios\_srv\_record – Configure Infoblox NIOS SRV records

-   nios\_txt\_record – Configure Infoblox NIOS txt records

-   nios\_zone – Configure Infoblox NIOS DNS zones

Plugins:
--------

-   infoblox: List all the hosts with records created in NIOS

-   lookup: Look up queries for NIOS database objects

Installation 
=============

Dependencies
------------

-   Python version 2.7 and above

-   Ansible version 2.9.0 or above

-   NIOS 8.2.4 and above

You can install the nios\_modules collection either from Ansible Galaxy
or directly from Git. It is recommended to install collection from
Ansible Galaxy are those are more stable than the git branch.

Installation from Ansible Galaxy
--------------------------------

To directly install the nios\_modules collection from Ansible Galaxy,
run the following command:

\$ ansible-galaxy collection install infoblox.nios\_modules

The collection folder would be installed at
\~/.ansible/collections/ansible\_collections/infoblox/nios\_modules

Installation from Git
---------------------

To git clone and install from this repo, follow these steps:

-   **Clone the repo:**

\$ git clone
https://github.com/infobloxopen/infoblox-ansible/nios\_modules.git

-   **Build the collection: **

    To build a collection, run the following command from inside the
    root directory of the collection:

\$ ansible-galaxy collection build

This creates a tarball of the built collection in the current directory.

-   **Install the collection:**

> \$ ansible-galaxy collection install &lt;collection-name&gt;.tar.gz -p
> ./collections

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

This code is published under [Apache
License](https://github.com/infobloxopen/infoblox-ansible/blob/master/LICENSE)

Support
=======

Infoblox supports the existing modules in the collections. You can open
an issue or request for enhancement
[here](https://github.com/infobloxopen/infoblox-ansible/issues)
