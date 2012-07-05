bootmachine
===========

Bootmachine is a bootstrapping tool for securely provisioning
virtual servers up until the point where customized configuration
management begins.

The bootmachine's goal is to allow getting started with, maintenance
of, and exploring new stack options through a simple and highly
customizable interface.

Providers
---------

Currently supported:

    * Rackspace Openstack Compute API v1 via openstack.compute
    * Rackspace Openstack Compute API v2 via python-novaclient
    * Non-rackspace Openstack Compute via python-novaclient
    * Write your own

Next in the queue:

    * Amazon EC2 via boto
    * Virtualbox / Vagrant
    * Write your own

Distros
-------

Currently supported:

    * Arch Linux
    * Ubuntu
    * Fedora
    * Debian (ready, but waiting for salt to land in the repos or a workaround)
    * Write your own

Next in the queue:

    * Gentoo
    * openSUSE
    * CentOS
    * RHEL
    * Write your own

Configuration Management Tools
------------------------------

Currently supported:

    * Salt
    * Write your own

Next in the queue:

    * Chef
    * Puppet
    * Write your own

Documentation about the usage and installation of the bootmachine
can be found at http://bootmachine.readthedocs.org

The source code and issue tracker can be found on GitHub.
https://github.com/rizumu/bootmachine
