bootmachine
===========

Bootmachine is a bootstrapping tool for securely provisioning
virtual servers up until the point where customized configuration
management begins.

The bootmachine's goal is to allow getting started with, maintenance
of, and exploring new stack options through a simple, pluggable and highly
customizable interface.

|buildstatus|_

.. image:: https://pypip.in/v/$REPO/badge.png
    :target: https://crate.io/packages/$REPO/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/$REPO/badge.png
    :target: https://crate.io/packages/$REPO/
    :alt: Number of PyPI downloads

Configuration Management Tools
------------------------------

Currently supported:

    * Salt http://saltstack.org
    * Write your own

Next in the queue:

    * Chef http://www.opscode.com/chef/
    * Puppet http://puppetlabs.com/
    * Write your own

Providers
---------

Currently supported:

    * Rackspace Openstack Compute API v2 via python-novaclient
    * Non-rackspace Openstack Compute via python-novaclient
    * Rackspace Openstack Compute API v1 via openstack.compute (deprecated) http://www.rackspace.com/cloud/
    * Write your own

Next in the queue:

    * Amazon EC2 via boto https://aws.amazon.com/ec2/
    * Virtualbox / Vagrant http://vagrantup.com/
    * Write your own

Distros
-------

Currently supported:

    * Arch Linux
    * Ubuntu
    * Fedora
    * Debian
    * Write your own

Next in the queue:

    * FreeBSD
    * Gentoo
    * openSUSE
    * CentOS
    * RHEL
    * Write your own

Documentation about the usage and installation of the bootmachine
can be found at: http://bootmachine.readthedocs.org

The source code and issue tracker can be found on GitHub:
https://github.com/rizumu/bootmachine

.. |buildstatus| image:: https://secure.travis-ci.org/rizumu/bootmachine.png?branch=master
.. _buildstatus: http://travis-ci.org/#!/rizumu/bootmachine
