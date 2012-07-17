import time

from fabric.api import env, run, sudo
from fabric.contrib.files import sed
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
    Install salt via ppa with aptitude.
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


def start_salt():
    """
    Upload the bootmachine's bundled salt-states.
    Launch the salt-master daemon on the saltmaster server.
    Launch a salt-minion daemon on all servers, including the saltmaster.
    """
    if env.host == env.master_server.public_ip:
        run("service salt-master restart", pty=False)
    sed("/etc/salt/minion", "#master: salt", "master: saltmaster-private")
    run("service salt-minion restart", pty=False)


def restart_salt():
    """
    Restarts salt master and/or minions.
    """
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("service salt-master restart", pty=False)
            time.sleep(3)
            sudo("service salt-minion restart", pty=False)
        else:
            sudo("service salt-minion restart", pty=False)
