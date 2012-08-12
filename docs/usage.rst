bootmachine  overview and usage
===============================

The ``bootmachine-admin start`` command simply copies two files
to the current working directory. A standard Fabric ``fabfile.py`` and
a ``settings.py`` for which you need to customize. Additionally it
copies over the ``configuration`` folder containing the initial
states/recipes to configure the servers.

After customizing your settings, all it takes to convert bare metal
servers from aluminium into rhodium is one simple Fabric command::

    $ fab bootmachine

Internally this does two things. First ``provider.bootem`` checks if
there are any non-booted servers listed in the
``settings.PROVIDER_BACKENDS``. If ``provider.boot`` finds a
non-booted server, it will boot it in parallel. In the meantime
``provider.bootem`` queries the provider to ensure that all servers are
``ACTIVE`` before continuing.

Second, after all servers are found to be active, the ``bootstrap``
method is called to check if there are any servers which have not yet
been bootstrapped. These servers are then bootstrapped in parallel.

.. note::

    These commands can also be run separately::

        $ fab boot
        $ fab each bootstrap
        $ fab master configure

After provisioning is complete you can manually login, with the user
credentials and port as defined in your settings.py, to the machine
using the following format::

    $ ssh -p {port} {username}@{ip}


To list the details for your new machines, including
ip addresses::

    $ fab provider

Or if you already have ``openstack-compute`` or ``python-novaclient``
installed, you could just as easily::

    $ openstack-compute list
         or
    $ nova list

All available commands can be seen by typing::

    $ fab -l  # which is short for fab --list
