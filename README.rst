bootmachine
===========

Bootmachine is a bootstrapping tool for securely provisioning
virtual servers up until the point where customized configuration
management begins.

The bootmachine's goal is to allow getting started with, maintenance
of, and exploring new stack options through a simple, pluggable and highly
customizable interface.

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

    * Arch Linux (as of Aug 10 2012, see https://github.com/rizumu/bootmachine/issues/8)
    * Ubuntu
    * Fedora
    * Debian
    * Write your own

Next in the queue:

    * Gentoo
    * openSUSE
    * CentOS
    * RHEL
    * Write your own

Documentation about the usage and installation of the bootmachine
can be found at: http://bootmachine.readthedocs.org

The source code and issue tracker can be found on GitHub:
https://github.com/rizumu/bootmachine
