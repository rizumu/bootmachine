import time

from fabric.api import env, run, sudo
from fabric.contrib.files import append, sed
from fabric.context_managers import settings as fabric_settings
from fabric.operations import reboot


DISTRO = "UBUNTU_1204LTS"
SALT_INSTALLERS = ["ppa"]


def bootstrap():
    """
    Bootstrap Ubuntu for use with the configuration manager of choice.

    Only the bare essentials, the configuration manager will take care of the rest.
    """
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    run("aptitude update")
    with fabric_settings(warn_only=True):
        # dist-upgrade without a grub config prompt
        # http://askubuntu.com/questions/146921/how-do-i-apt-get-y-dist-upgrade-without-a-grub-config-prompt
        run('DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')
    append("/etc/hosts", "{0} saltmaster-private".format(env.master_server.private_ip))
    reboot()
    run("aptitude install -y build-essential")


def upgrade_ubuntu():
    """
    When a provider doesn't offer the latest version.
    """
    raise NotImplementedError()


def install_salt(installer="ppa"):
    """
    Install salt with the chosen installer.
    """
    if installer == "ppa":
        run("aptitude install -y python-software-properties")
        run("add-apt-repository --yes ppa:saltstack/salt")
        with fabric_settings(warn_only=True):
            run("aptitude update")
        if env.host == env.master_server.public_ip:
            run("aptitude install -y salt-master salt-minion salt-syndic")
        else:
            run("aptitude install -y salt-minion salt-syndic")
    else:
        raise NotImplementedError()


def setup_salt():
    """
    Setup the salt configuration files.
    """
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]

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
            sudo("service salt-master start", pty=False)
            time.sleep(3)
        sudo("service salt-minion start", pty=False)


def restart_salt():
    """
    Restarts salt master and minions.
    """
    # use warn_only to catch already running errors
    # probably should use pgrep instead
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("service salt-master restart", pty=False)
            time.sleep(3)
        sudo("service salt-minion restart", pty=False)
