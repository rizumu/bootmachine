import os
import sys
import time

from fabric.api import cd, env, run
from fabric.contrib.files import append, contains, sed
from fabric.context_managers import settings as fabric_settings
from fabric.operations import reboot


DISTRO = "DEBIAN_6"
SALT_INSTALLERS = ["pip"]


def bootstrap():
    """
    Bootstrap Ubuntu for use with the configuration manager of choice.

    Only the bare essentials, the configuration manager will take care of the rest.
    """
    BASE_PACKAGES = [
        "build-essential",
    ]
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    with fabric_settings(warn_only=True):
        run("aptitude update && aptitude -y dist-upgrade")
        run("aptitude install -y {base_packages}".format(base_packages=" ".join(BASE_PACKAGES)))
    reboot()


def upgrade():
    """
    When a provider doesn't offer the latest version.
    """
    raise NotImplementedError()


def install_salt(installer="pip"):
    """
    Upload the bootmachine's bundled salt-states.
    Launch the salt-master daemon on the saltmaster server.
    Launch a salt-minion daemon on all servers, including the saltmaster.
    """
    if installer == "pip":
        run('echo "deb http://backports.debian.org/debian-backports squeeze-backports main" >/etc/apt/sources.list.d/backports.list')
        run("aptitude update")
        run("aptitude install -y libzmq1 python-crypto python-m2crypto python-yaml python-pip")
        run("aptitude install -y python-dev libzmq-dev")
        run("pip install --noconfirm pyzmq salt")
    else:
        raise NotImplementedError()


def start_salt():
    raise NotImplementedError()
    # run("cp /etc/salt/minion.template /etc/salt/minion")
    # if env.host == env.master_server.public_ip:
    #     run("cp /etc/salt/master.template /etc/salt/master")
    #     run("service salt-master restart")
    #     time.sleep(3)

    # sed("/etc/salt/minion", "#master: salt", "master: {0}".format(env.master_server.private_ip))
    # run("service salt-minion restart")


def restart_salt():
    """
    Restarts salt master and/or minions.
    """
    raise NotImplementedError()
