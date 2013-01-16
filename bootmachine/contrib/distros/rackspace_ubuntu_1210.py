import time

from fabric.api import env, run, sudo
from fabric.contrib.files import append, sed, uncomment
from fabric.context_managers import settings as fabric_settings
from fabric.operations import reboot

import settings


Distro = "UBUNTU_1210"
SALT_INSTALLERS = ["ppa"]


def bootstrap():
    """
    Bootstrap Ubuntu for use with the configuration manager of choice.

    Only the bare essentials, the configuration manager will take care of the rest.
    """
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    run("aptitude update")
    append("/etc/hosts", "{0} saltmaster-private".format(env.master_server.private_ip))
    with fabric_settings(warn_only=True):
        reboot()
    run("aptitude install -y build-essential")
    # allow users in the wheel group to sudo without a password
    uncomment("/etc/sudoers", "wheel.*NOPASSWD")


def upgrade_ubuntu():
    """
    When a provider doesn't offer the latest version, and you want to automate the upgrade.
    """
    with fabric_settings(warn_only=True):
        # dist-upgrade without a grub config prompt
        # http://askubuntu.com/questions/146921/how-do-i-apt-get-y-dist-upgrade-without-a-grub-config-prompt  # nopep8
        run('DEBIAN_FRONTEND=noninteractive apt-get -y \
        -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')


def install_salt(installer="ppa"):
    """
    Install salt with the chosen installer.
    """
    if installer == "ppa":
        run("echo deb http://ppa.launchpad.net/saltstack/salt/ubuntu `lsb_release -sc` main | \
             sudo tee /etc/apt/sources.list.d/saltstack.list")
        key_url = "http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x4759FA960E27C0A6"
        run("wget -q -O- '{0}' | sudo apt-key add -".format(key_url))
        run("aptitude update")
        if env.host == env.master_server.public_ip:
            run("aptitude install -y salt-master")
        run("aptitude install -y salt-minion salt-syndic")
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
