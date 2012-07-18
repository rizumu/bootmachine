from fabric.api import env, run
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
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    with fabric_settings(warn_only=True):
        run("aptitude update && aptitude -y dist-upgrade")
        run("aptitude install -y build-essential")
    append("/etc/hosts", "{0} saltmaster-private".format(env.master_server.private_ip))
    reboot()


def upgrade():
    """
    When a provider doesn't offer the latest version.
    """
    raise NotImplementedError()


def install_salt(installer="pip"):
    """
    Install salt with the chosen installer.
    """
    if installer == "pip":
        run('echo "deb http://backports.debian.org/debian-backports squeeze-backports main" >/etc/apt/sources.list.d/backports.list')
        run("aptitude update")
        run("aptitude install -y libzmq1 python-crypto python-m2crypto python-yaml python-pip")
        run("aptitude install -y python-dev libzmq-dev")
        run("pip install --noconfirm pyzmq salt")
    else:
        raise NotImplementedError()


def setup_salt():
    """
    Setup the salt configuration files and enable dameon on a reboot.
    """
    raise NotImplementedError()


def start_salt():
    """
    Restarts salt master and minions.
    """
    raise NotImplementedError()


def restart_salt():
    """
    Restarts salt master and minions.
    """
    raise NotImplementedError()
