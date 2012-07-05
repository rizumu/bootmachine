import os
import sys
import time

from fabric.api import cd, env, run, sudo
from fabric.context_managers import settings as fabric_settings
from fabric.contrib.files import append, put, sed, uncomment
from fabric.operations import reboot


DISTRO = "FEDORA_16"
SALT_INSTALLERS = ["rpm-stable", "rpm-epel-testing"]


def bootstrap():
    """
    Bootstrap Fedora.

    Only the bare essentials, salt takes care of the rest.

    """
    BASE_PACKAGES = [
        "curl",
        "git",
        "rsync",
    ]
    run("/usr/bin/localedef -i en_US -f UTF-8 en_US.UTF-8")
    run("export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8")
    append("/etc/sysconfig/i18n", 'LC_ALL="en_US.UTF-8"')
    run("yum update --assumeyes")
    run("yum groupinstall --assumeyes 'Development Tools'")
    run("yum install --assumeyes {pkgs}".format(pkgs=" ".join(BASE_PACKAGES)))
    reboot()


def install_salt(installer="rpm"):
    """
    Install salt via rpm.
    """
    if installer == "rpm-stable":
        run("yum install --assumeyes salt-master salt-minion")
    elif installer == "rpm-testing":
        run("yum install --assumeyes --enablerepo=updates-testing salt-master salt-minion")
    else:
        raise NotImplementedError()


def start_salt():
    """
    Upload the bootmachine's bundled salt-states.
    Launch the salt-master daemon on the saltmaster server.
    Launch a salt-minion daemon on all servers, including the saltmaster.
    """
    if env.host == env.master_server.public_ip:
        run("systemctl enable salt-master.service")
        run("systemctl start salt-master.service")

    sed("/etc/salt/minion", "\#master\: salt", "master: {ip_addr}".format(
        ip_addr=env.master_server.private_ip))

    run("systemctl enable salt-minion.service")
    run("systemctl start salt-minion.service")


def restart_salt():
    """
    Restarts salt master and/or minions.
    """
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("systemctl restart salt-master.service")
            time.sleep(3)
            sudo("systemctl restart salt-minion.service")
        else:
            sudo("systemctl restart salt-minion.service")
