Bootmachine Changelog
=====================

0.5.9
-----
CHANGES:

* resolve issue #8 by using pgrep to check if
  salt-master/minion daemons instead of relying
  on Fabric.
* deprecate explicit support for rackspace api v1

0.5.4, 0.5.5, 0.5.6, 0.5.7, 0.5.8 (13.09.2012)
------------------
CHANGES:

* fix setup.py and use a MANIFEST.in to include configuration files

0.5.3 (13.09.2012)
------------------
CHANGES:

* some fixes to the provided salt-states

0.5.2 (13.08.2012)
------------------
NEW FEATURES:

* debian 6 is now supported on rackspace with salt

CHANGES:
* the `fab all` task has been renamed to `fab each`, mostly to
  avoid the name clash with the Python's global all() method.
* the `fab provision` task has been renamed to `fab bootstrap` and
  a new `fab configure` task has been added to better clarify
  intent. Additionaly a thorough refactoring of core.py has taken
  place.
* instead of aborting, a y/n continue prompt has been added
  when a rackspace server found to be not `ACTIVE`.

0.5.1 (23.07.2012)
------------------
NEW FEATURES:

* add a test runner that runs all builds, logs output and scans for
  failures
* add a requirements.txt, so installing in a new virtualenv is simpler
  when working on the bootmachine
* friendlier time counter while waiting for servers to boot
* add a warning prompt to require confirmation before deleting
  servers, with an option to force.
* changed fab all reboot_servers() to fab reboot_server(servername)
* added an internal __set_ssh_vars(valid_object) method. After
  performing a few sanity tests this method adds reliable ssh
  variables to the passed in object (env or server).

SALT:

* add a bootmachine-pillar/deploymachine.sls as an example of where
  post bootmachine pillar data can be stored. Bootmachine boots your
  servers, deploymachine is the states for your custom stack.
* fix require relationship between users/ssh/iptables states
* fix iptables issues and simplify the salt-state

ARCH LINUX:

* upgrade salt-state for grub to install and use grub2
* fix the recent glibc update that broke the build
* add a salt-state for the rc.conf
* add a way for the saltmaster to open a port for newly booted minions
* use hostname instead of ip in the salt-minion config
* follow netcfg best practice, by removing networking settings from rc.conf

0.5.0 (23.07.2012) -- Initial release.
--------------------------------------

The bootmachine grew out of the desire to automate the launching,
configuration, and scaling of a stack of servers in the cloud.

The provider, configurator, and distro functionality has been written
in such a way that each module is pluggable. Therefore customization
and extension can be achieved with little effort.

The bootmachine has existing modules for Rackspace, Salt and a handful
of distros. Additional modules could easily be written to support EC2, Chef,
Puppet, and other distros.

Any contributions to the core or submissions of new modules for the
contrib will be much appreciated. I'd like to see this project allow
developers to switch between providers with ease, simplify the process
of configuring a cloud stack, and encourage experimentation with new
distros.

This is not a 1.0 yet, but please give it a try. It has been working
well for me and I'm excited about this first public release.

Github page: https://github.com/rizumu/bootmachine
