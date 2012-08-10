import time

from fabric.api import env, run, sudo
from fabric.context_managers import settings as fabric_settings
from fabric.contrib.files import append, sed
from fabric.operations import reboot


DISTRO = "FEDORA_17"
SALT_INSTALLERS = ["rpm-stable", "rpm-epel-testing"]


def bootstrap():
    """
    Bootstrap Fedora.

    Only the bare essentials, salt takes care of the rest.

    """
    base_packages = [
        "curl",
        "git",
        "rsync",
    ]
    run("/usr/bin/localedef -i en_US -f UTF-8 en_US.UTF-8")
    run("export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8")
    append("/etc/sysconfig/i18n", 'LC_ALL="en_US.UTF-8"')
    run("yum update --assumeyes")
    run("yum groupinstall --assumeyes 'Development Tools'")
    run("yum install --assumeyes {pkgs}".format(pkgs=" ".join(base_packages)))
    append("/etc/hosts", "{0} saltmaster-private".format(env.master_server.private_ip))
    with fabric_settings(warn_only=True):
        reboot()


def install_salt(installer="rpm"):
    """
    Install salt with the chosen installer.
    """
    if installer == "rpm-stable":
        run("yum install --assumeyes salt-master salt-minion")
    elif installer == "rpm-testing":
        run("yum install --assumeyes --enablerepo=updates-testing salt-master salt-minion")
    else:
        raise NotImplementedError()


def setup_salt():
    """
    Setup the salt configuration files and enable dameon on a reboot.
    """
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]

    if env.host == env.master_server.public_ip:
        run("systemctl enable salt-master.service")
    run("systemctl enable salt-minion.service")

    sed("/etc/salt/minion", "#master: salt", "master: saltmaster-private")
    append("/etc/salt/minion", "grains:\n  roles:")
    for role in server.roles:
        append("/etc/salt/minion", "    - {0}".format(role))


def start_salt():
    """
    Starts salt master and minions.
    """
    # use warn_only to catch already running errors
    # probably should use pgrep instead
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("systemctl start salt-master.service")
            time.sleep(3)
        sudo("systemctl start salt-minion.service")


def restart_salt():
    """
    Restarts salt master and minions.
    """
    # use warn_only to catch already running errors
    # probably should use pgrep instead
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("systemctl restart salt-master.service")
            time.sleep(3)
        sudo("systemctl restart salt-minion.service")
