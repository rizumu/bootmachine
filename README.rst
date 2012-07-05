bootmachine
===========

Bootmachine is a bootstrapping tool for securely provisioning
virtual servers up until the point where customized configuration
management begins.

The bootmachine's goal is to allow getting started and switching
between the options with as little effort as possible.

Providers
---------

Currently supported:

    * Rackspace Openstack Compute API v1
    * Rackspace Openstack Compute API v2
    * Non-rackspace Openstack Compute via python-novaclient
    * Write your own

Next in the queue:

    * Amazon EC2
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
