Motivation
==========

There are many options when it comes to server providers,
configuration management tools, and distros. The bootmachine's goal is
to reduce maintenance and overhead when managing a server stack, but
through its pluggable api it also simplifies exploring new options.

The bootmachine is written in PEP8 compliant Python and is at its most
basic, simply a specialized Fabric libary.

Providers:

    * Rackspace Openstack API v2
    * Rackspace Openstack API v1 (deprecated)
    * Amazon EC2 (forthcoming)
    * Write your own..

Configurators:

    * Salt http://saltstack.org/
    * Chef (forthcoming)
    * Puppet (forthcoming)
    * Write your own...

Distros:

    * Arch Linux
    * Fedora 16+17
    * Ubuntu 12.04 LTS
    * Debian 6
    * Gentoo 11.0 (forthcoming)
    * OpenSUSE 12 (forthcoming)
    * CentOS 6.2 (forthcoming)
    * Red Hat Enterprise Linux 6 (forthcoming)
    * write your own...

First, the bootmachine boots each new server as defined in its
``settings.py`` using the distro and provider of your choice. Next it
bootstaps setting up the distro and installs the configuration
management tool of your choice. Finally it uses the configuration
management tool to provision the server to a secure state. The
supplied states/recipes handle iptables, ssh, users, and not much
more. The idea is to keep things simple, but it is up to you to
customize the stack to your preferences.

For example, you could create a new stack with four Arch Linux servers
using the Rackspace api. After defining your settings and running `fab
bootmachine`. Salt is installed and the server is configured as the
states tell it to be. The stack could contain a loadbalancer, cache,
application, and database server. It is up to you to define the
individual roles, but the bootmachine gets you as close as it can to a
secure and ready system before personalization takes over.

Booting
=======

Bootmachine simplifies the initial boot phase of creating new servers,
by reading configuration from ``settings.SERVERS``. Choose from the
built-in cloud providers, or write a custom ``settings.PROVIDER_MODULE``.

.. note::

    Write a custom backed if your intention is to support local
    virtual machines, an not yet included cloud provider, or hardware
    in a private datacenter. If your module is generic enough to share
    with others, please consider contributing it back to the
    bootmachine.

Provisioning with Configuration Management Tools
================================================

The bootmachine reads the settings file and checks for servers that are
not yet booted. It will then boot each new server, with its defined
distro and size, and next bootstrap the configuration management tool
of your choice.

.. note::

    The bootmachine supports a stack with multiple distros, but it is
    assumed that only *one* provider and *one* configuration
    management tool will be used per stack.

    Although you may boot a mixture of distro types, it is advised
    against because this will most likely create unnecessary
    complexity down the road. Mainly because the configuration
    management tools could have conflicting versions per distro.
    If you know what your doing than go ahead, otherwise be warned.

After your configuration management tool of choice is bootstrapped on
the new servers, the last step is provisioning the server to a secure
state. For this it following community approved best-practices in the
supplied salt-states, chef/puppet recipes, etc.

Bootmachine adheres to the Slicehost provisioning documentation and
the Arch Linux wiki:

    * Slicehost provisioning docs: http://articles.slicehost.com/ubuntu-10
    * Arch Linux wiki : https://wiki.archlinux.org/

What's Next
===========

The function of the bootmachine is to create a new server, or cluster of
servers, based on a configuration file and provision them into a secure
state. It is the job of a configuration management tool to setup the
server for its real task, such as application server, database server,
loadbalancer, etc.

Every application is different, have fun.
