import time

from fabric.api import env, run, sudo
from fabric.contrib.files import append, sed
from fabric.context_managers import settings as fabric_settings
from fabric.operations import reboot

import settings


DISTRO = "DEBIAN_7"
SALT_INSTALLERS = ["saltstack"]


def bootstrap():
    """
    Bootstrap Ubuntu for use with the configuration manager of choice.

    Only the bare essentials, the configuration manager will take care of the rest.
    """
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    with fabric_settings(warn_only=True):
        run("aptitude update && aptitude -y dist-upgrade")
    append("/etc/hosts", "{0} saltmaster-private".format(env.master_server.private_ip))
    with fabric_settings(warn_only=True):
        reboot()
    run("aptitude install -y build-essential rsync sudo")
    append("/etc/sudoers",
           "## allow members of group wheel to execute any command\n%wheel ALL=(ALL) ALL")


def upgrade():
    """
    When a provider doesn't offer the latest version.
    """
    raise NotImplementedError()


def install_salt(installer="saltstack"):
    """
    Install salt with the chosen installer.
    """
    if installer == "saltstack":
        append("/etc/apt/sources.list.d/saltstack.list",
               "deb http://debian.saltstack.com/debian wheezy-saltstack main")
        run("aptitude update")
        run("aptitude -o Aptitude::Cmdline::ignore-trust-violations=true -y install salt-master")
        run("aptitude -o Aptitude::Cmdline::ignore-trust-violations=true -y install salt-minion")
    else:
        raise NotImplementedError()


def setup_salt():
    """
    Setup the salt configuration files.
    """
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]

    if env.host == env.master_server.public_ip:
        append("/etc/salt/master", "file_roots:\n  base:\n    - {0}".format(
               settings.REMOTE_STATES_DIR))
        append("/etc/salt/master", "pillar_roots:\n  base:\n    - {0}".format(
               settings.REMOTE_PILLARS_DIR))

    sed("/etc/salt/minion", "#master: salt", "master: {0}".format(env.master_server.private_ip))
    sed("/etc/salt/minion", "#id:", "id: {0}".format(server.name))
    append("/etc/salt/minion", "grains:\n  roles:")
    for role in server.roles:
        append("/etc/salt/minion", "    - {0}".format(role))


def start_salt():
    """
    Starts salt master and minions.
    """
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("service salt-master start")
        time.sleep(3)
        sudo("service salt-minion start")


def stop_salt():
    """
    Stops salt master and minions.
    """
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("service salt-master stop")
        sudo("service salt-minion stop")


def restart_salt():
    """
    Restarts salt master and minions.
    """
    stop_salt()
    start_salt()
