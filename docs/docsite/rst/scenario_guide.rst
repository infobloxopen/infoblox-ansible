.. _nios_guide:

************************
 Infoblox Scenario Guide
************************

.. contents:: Topics
   :local:

Introduction
============

This guide describes how to use the ``infoblox.nios_modules`` Ansible collection to automate Infoblox NIOS for DNS and IPAM workflows.

Prerequisites and installation
==============================

Before using the collection, ensure your control node meets these requirements:

- Python 3.10 or later
- Ansible Core 2.16 or later
- NIOS 8.6.x and 9.0.x
- Infoblox WAPI 2.12.3 or later
- ``infoblox-client`` 0.6.2

Install ``infoblox-client``:

.. code-block:: bash

    pip install infoblox-client==0.6.2

Install the collection:

.. code-block:: bash

    ansible-galaxy collection install infoblox.nios_modules

Provider configuration (connecting to NIOS)
===========================================

Define provider credentials once and pass them to each module task:

.. code-block:: yaml

    ---
    nios_provider:
      host: 192.0.2.10
      username: admin
      password: infoblox

Example playbook skeleton:

.. code-block:: yaml

    - name: Infoblox workflow
      hosts: localhost
      connection: local
      gather_facts: false
      vars:
        nios_provider:
          host: 192.0.2.10
          username: admin
          password: infoblox
      tasks:
        - name: Ensure DNS view exists
          infoblox.nios_modules.nios_dns_view:
            name: default
            state: present
            provider: "{{ nios_provider }}"

Working with DNS records
========================

The collection supports DNS record modules including:
``infoblox.nios_modules.nios_a_record``,
``infoblox.nios_modules.nios_aaaa_record``,
``infoblox.nios_modules.nios_cname_record``,
``infoblox.nios_modules.nios_host_record``,
``infoblox.nios_modules.nios_ptr_record``,
``infoblox.nios_modules.nios_mx_record``,
``infoblox.nios_modules.nios_naptr_record``,
``infoblox.nios_modules.nios_srv_record``, and
``infoblox.nios_modules.nios_txt_record``.

.. code-block:: yaml

    - name: Manage common DNS record types
      hosts: localhost
      connection: local
      gather_facts: false
      vars:
        nios_provider:
          host: 192.0.2.10
          username: admin
          password: infoblox
      tasks:
        - name: Create A record
          infoblox.nios_modules.nios_a_record:
            name: app.example.com
            ipv4addr: 192.0.2.20
            state: present
            provider: "{{ nios_provider }}"

        - name: Create AAAA record
          infoblox.nios_modules.nios_aaaa_record:
            name: app-v6.example.com
            ipv6addr: 2001:db8::20
            state: present
            provider: "{{ nios_provider }}"

        - name: Create CNAME record
          infoblox.nios_modules.nios_cname_record:
            name: www.example.com
            canonical: app.example.com
            state: present
            provider: "{{ nios_provider }}"

        - name: Create PTR record
          infoblox.nios_modules.nios_ptr_record:
            ptrdname: app.example.com
            ipv4addr: 192.0.2.20
            state: present
            provider: "{{ nios_provider }}"

        - name: Create MX record
          infoblox.nios_modules.nios_mx_record:
            name: example.com
            mail_exchanger: mail.example.com
            preference: 10
            state: present
            provider: "{{ nios_provider }}"

        - name: Create TXT record
          infoblox.nios_modules.nios_txt_record:
            name: example.com
            text: "v=spf1 -all"
            state: present
            provider: "{{ nios_provider }}"

        - name: Create SRV record
          infoblox.nios_modules.nios_srv_record:
            name: _sip._tcp.example.com
            target: sip.example.com
            port: 5060
            priority: 10
            weight: 5
            state: present
            provider: "{{ nios_provider }}"

        - name: Create NAPTR record
          infoblox.nios_modules.nios_naptr_record:
            name: "*.subscriber-100.example.com"
            order: 1000
            preference: 10
            replacement: replacement1.example.com
            services: "SIP+D2U"
            flags: "U"
            state: present
            provider: "{{ nios_provider }}"

        - name: Create host record with automatic next available IP
          infoblox.nios_modules.nios_host_record:
            name: host01.example.com
            ipv4addrs:
              - ipv4addr: "{{ lookup('infoblox.nios_modules.nios_next_ip', '192.0.2.0/24', provider=nios_provider)[0] }}"
            state: present
            provider: "{{ nios_provider }}"

Working with networks and IP addresses
======================================

Use ``infoblox.nios_modules.nios_network``, ``infoblox.nios_modules.nios_fixed_address``,
and ``infoblox.nios_modules.nios_range`` for IPAM workflows. ``infoblox.nios_modules.nios_network_view``
is also available when managing multiple network views.

.. code-block:: yaml

    - name: Manage network objects
      hosts: localhost
      connection: local
      gather_facts: false
      vars:
        nios_provider:
          host: 192.0.2.10
          username: admin
          password: infoblox
      tasks:
        - name: Ensure network view exists
          infoblox.nios_modules.nios_network_view:
            name: default
            state: present
            provider: "{{ nios_provider }}"

        - name: Create network
          infoblox.nios_modules.nios_network:
            network: 192.0.2.0/24
            comment: Application network
            state: present
            provider: "{{ nios_provider }}"

        - name: Create fixed address
          infoblox.nios_modules.nios_fixed_address:
            name: host01.example.com
            ipv4addr: 192.0.2.30
            mac: "00:11:22:33:44:55"
            state: present
            provider: "{{ nios_provider }}"

        - name: Create DHCP range
          infoblox.nios_modules.nios_range:
            network: 192.0.2.0/24
            start_addr: 192.0.2.100
            end_addr: 192.0.2.150
            state: present
            provider: "{{ nios_provider }}"

Working with DNS zones
======================

Use ``infoblox.nios_modules.nios_zone`` for forward or reverse zones.

.. code-block:: yaml

    - name: Manage DNS zones
      hosts: localhost
      connection: local
      gather_facts: false
      vars:
        nios_provider:
          host: 192.0.2.10
          username: admin
          password: infoblox
      tasks:
        - name: Create forward zone
          infoblox.nios_modules.nios_zone:
            name: example.com
            zone_format: FORWARD
            state: present
            provider: "{{ nios_provider }}"

        - name: Create reverse zone
          infoblox.nios_modules.nios_zone:
            name: 2.0.192.in-addr.arpa
            zone_format: IPV4
            state: present
            provider: "{{ nios_provider }}"

Working with DNS views
======================

Use ``infoblox.nios_modules.nios_dns_view`` to create or remove DNS views.

.. code-block:: yaml

    - name: Manage DNS views
      hosts: localhost
      connection: local
      gather_facts: false
      vars:
        nios_provider:
          host: 192.0.2.10
          username: admin
          password: infoblox
      tasks:
        - name: Create DNS view
          infoblox.nios_modules.nios_dns_view:
            name: internal
            comment: Internal DNS view
            state: present
            provider: "{{ nios_provider }}"

Lookup plugins
==============

Lookup plugins provided by this collection include:
``infoblox.nios_modules.nios_lookup``,
``infoblox.nios_modules.nios_next_ip``,
``infoblox.nios_modules.nios_next_network``, and
``infoblox.nios_modules.nios_next_vlan_id``.

.. code-block:: yaml

    - name: Lookup workflows
      hosts: localhost
      connection: local
      gather_facts: false
      vars:
        nios_provider:
          host: 192.0.2.10
          username: admin
          password: infoblox
      tasks:
        - name: Fetch DNS view objects
          ansible.builtin.set_fact:
            dns_views: "{{ lookup('infoblox.nios_modules.nios_lookup', 'view', filter={'name': 'default'}, provider=nios_provider) }}"

        - name: Get next IP from network
          ansible.builtin.set_fact:
            next_ip: "{{ lookup('infoblox.nios_modules.nios_next_ip', '192.0.2.0/24', provider=nios_provider)[0] }}"

        - name: Get next network from container
          ansible.builtin.set_fact:
            next_network: "{{ lookup('infoblox.nios_modules.nios_next_network', '10.0.0.0/16', cidr=24, provider=nios_provider)[0] }}"

        - name: Get next available VLAN ID from a VLAN view
          ansible.builtin.set_fact:
            next_vlan_id: "{{ lookup('infoblox.nios_modules.nios_next_vlan_id', parent='default', provider=nios_provider)[0] }}"

        - name: Get next two available VLAN IDs, excluding IDs 1-3
          ansible.builtin.set_fact:
            next_vlan_ids: "{{ lookup('infoblox.nios_modules.nios_next_vlan_id', parent='default', num=2, exclude=[1, 2, 3], provider=nios_provider) }}"

Advanced topics
===============

Extensible attributes
---------------------

Use ``infoblox.nios_modules.nios_extensible_attribute`` to define extensible attributes for DNS and IPAM objects.

.. code-block:: yaml

    - name: Manage extensible attributes
      hosts: localhost
      connection: local
      gather_facts: false
      vars:
        nios_provider:
          host: 192.0.2.10
          username: admin
          password: infoblox
      tasks:
        - name: Ensure extensible attribute exists
          infoblox.nios_modules.nios_extensible_attribute:
            name: Owner
            type: STRING
            comment: Owner metadata
            state: present
            provider: "{{ nios_provider }}"

DTC objects
-----------

Use DTC modules such as ``infoblox.nios_modules.nios_dtc_server``,
``infoblox.nios_modules.nios_dtc_pool``, ``infoblox.nios_modules.nios_dtc_lbdn``,
``infoblox.nios_modules.nios_dtc_topology``, and monitor modules
(``infoblox.nios_modules.nios_dtc_monitor_http``,
``infoblox.nios_modules.nios_dtc_monitor_icmp``,
``infoblox.nios_modules.nios_dtc_monitor_pdp``,
``infoblox.nios_modules.nios_dtc_monitor_sip``,
``infoblox.nios_modules.nios_dtc_monitor_snmp``,
``infoblox.nios_modules.nios_dtc_monitor_tcp``).

.. code-block:: yaml

    - name: Manage DTC objects
      hosts: localhost
      connection: local
      gather_facts: false
      vars:
        nios_provider:
          host: 192.0.2.10
          username: admin
          password: infoblox
      tasks:
        - name: Create DTC server
          infoblox.nios_modules.nios_dtc_server:
            name: web01
            host: 192.0.2.40
            state: present
            provider: "{{ nios_provider }}"

        - name: Create DTC pool
          infoblox.nios_modules.nios_dtc_pool:
            name: web-pool
            lb_method: ROUND_ROBIN
            servers:
              - server: web01
            state: present
            provider: "{{ nios_provider }}"

        - name: Create DTC LBDN
          infoblox.nios_modules.nios_dtc_lbdn:
            name: app.example.com
            pools:
              - pool: web-pool
            state: present
            provider: "{{ nios_provider }}"

Dynamic inventory
=================

.. note::

   The legacy Infoblox dynamic inventory script (``infoblox.py``) that was previously
   documented in the central Ansible scenario guide is no longer maintained. It was
   removed from ``community.general`` and is not part of this collection.

   For dynamic inventory with Infoblox NIOS, use the
   `infoblox.nios_modules inventory plugin <https://github.com/infobloxopen/infoblox-ansible>`_
   which is included in this collection, or manage inventory through the NIOS REST API
   directly.
