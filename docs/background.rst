Motivation
==========

There are multiple options when it comes to distros, cloud providers and
configuration management tools. The bootmachine's goal is to allow
getting started and switching between the options with as little
effort as possible.

    * Arch Linux | Debian | Fedora | Ubuntu | write your own...
    * Rackspace Openstack Cloudservers | Amazon EC2 | write your own..
    * Salt | Chef | Puppet | write your own...

The bootmachine will boot each new server as defined in the
``settings.py``, install a configuration management tool
on the server, and finally use the configuration management tool to
provision the server to a secure state.

Booting
=======

Bootmachine simplifies the initial boot phase of creating new servers,
by reading configuration from
``settings.PROVIDER_BACKENDS``.  Select from the built-in
cloud providers, or write a custom ``provider_backend``.

Currently supported providers are:

    * openstack|rackspace

Next in the queue:

    * amazon

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
distro and size, and next install the configuration management tool
of your choice.

Currently supported distros are:

    * Arch Linux
    * Ubuntu
    * Fedora

Next in the queue:

    * Debian

Currently supported configuration management tools are:

    * Salt

Next in the queue:

    * Chef
    * Puppet

.. note::

    The bootmachine supports a configuration with multiple providers
    and distros, but it is assumed that only *one* configuration
    management tool will be used.

.. note::

    Although you may boot a mixture of distro types, it is advised
    against because this will most likely create unnecessary
    complexity down the road. Mainly because the configuration
    management tools could have conflicting versions per distro.
    If you know what your doing than go ahead, otherwise be warned.


After the configuration management tool of choice is bootstrapped, the
last step is to provision the server to a secure state, following community
approved best-practices.

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
