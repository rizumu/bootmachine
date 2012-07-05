import os
import sys
import time

from fabric.api import cd, env, run, sudo
from fabric.contrib.files import append, contains, sed
from fabric.context_managers import settings as fabric_settings
from fabric.operations import reboot


DISTRO = "UBUNTU_1204LTS"
SALT_INSTALLERS = ["ppa"]


def bootstrap():
    """
    Bootstrap Ubuntu for use with the configuration manager of choice.

    Only the bare essentials, the configuration manager will take care of the rest.
    """
    BASE_PACKAGES = [
        "build-essential",
        "python-software-properties",
    ]
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    run("aptitude update")
    with fabric_settings(warn_only=True):
        # dist-upgrade without a grub config prompt
        # http://askubuntu.com/questions/146921/how-do-i-apt-get-y-dist-upgrade-without-a-grub-config-prompt
        run('DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')
    reboot()
    run("aptitude install -y {base_packages}".format(base_packages=" ".join(BASE_PACKAGES)))


def upgrade_ubuntu():
    """
    When a provider doesn't offer the latest version.
    """
    raise NotImplementedError()


def install_salt(installer="ppa"):
    """
    Install salt via ppa with aptitude.
    """
    if installer == "ppa":
        run("add-apt-repository --yes ppa:chris-lea/libpgm")
        run("add-apt-repository --yes ppa:chris-lea/zeromq")
        run("add-apt-repository --yes ppa:saltstack/salt")
        run("apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4759FA960E27C0A6")
        with fabric_settings(warn_only=True):
            run("aptitude update")
        if env.host == env.master_server.public_ip:
            run("aptitude install -y salt-master salt-minion salt-syndic")
        else:
            run("aptitude install -y salt-minion salt-syndic")
    else:
        raise NotImplementedError()


def start_salt():
    """
    Upload the bootmachine's bundled salt-states.
    Launch the salt-master daemon on the saltmaster server.
    Launch a salt-minion daemon on all servers, including the saltmaster.
    """
    if env.host == env.master_server.public_ip:
        run("service salt-master restart")

    sed("/etc/salt/minion", "#master: salt", "master: {0}".format(env.master_server.private_ip))
    run("service salt-minion restart")


def restart_salt():
    """
    Restarts salt master and/or minions.
    """
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("service salt-master restart")
            time.sleep(3)
            sudo("service salt-minion restart")
        else:
            sudo("service salt-minion restart")
