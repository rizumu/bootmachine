import time
import urllib2

from fabric.api import env, run, sudo
from fabric.colors import blue, cyan, green, magenta, red, white, yellow  # noqa
from fabric.context_managers import cd, settings as fabric_settings
from fabric.contrib.files import append, contains, sed, uncomment
from fabric.utils import abort

import settings


DISTRO = "ARCH_20139"
SALT_INSTALLERS = ["aur", "aur-git", "bootstrap"]


def validate_configurator_version():
    """
    Arch is a rolling release distro, therefore it is important to ensure
    the configurator version is current.
    """
    if settings.CONFIGURATOR_MODULE == "bootmachine.contrib.configurators.salt":
        pkgver = settings.SALT_AUR_PKGVER
        pkgrel = settings.SALT_AUR_PKGREL
        response = urllib2.urlopen("https://aur.archlinux.org/packages/sa/salt/PKGBUILD")
        for line in response:
            if line.startswith("pkgver=") and not pkgver in line:
                abort("The requested Salt 'pkgrel={0}' in the AUR was updated to '{1}'.".format(
                    pkgver, line.strip()))
            if line.startswith("pkgrel=") and not pkgrel in line:
                abort("The requested Salt 'pkgrel={0}' in the AUR was updated to '{1}'.".format(
                    pkgrel, line.strip()))


def bootstrap():
    """
    Bootstrap Arch Linux.

    Only the bare essentials, the configurator will take care of the rest.
    """
    validate_configurator_version()

    # upgrade pacakges
    run("pacman --noconfirm -Syu")

    # install essential packages
    run("pacman --noconfirm -S base-devel")
    run("pacman --noconfirm -S curl git rsync")

    # create a user, named 'aur', to safely install AUR packages under fakeroot
    # uid and gid values auto increment from 1000
    # to prevent conficts set the 'aur' user's gid and uid to 902
    run("groupadd -g 902 aur && useradd -m -u 902 -g 902 -G wheel aur")

    # allow users in the wheel group to sudo without a password
    # so that the aur user can be scripted to install yaourt
    uncomment("/etc/sudoers", "wheel.*NOPASSWD")

    # install yaourt
    sudo("rm -rf /home/aur/.builds && mkdir /home/aur/.builds/", user="aur")
    with cd("/home/aur/.builds/"):
        sudo("bash <(curl aur.sh) -si --noconfirm package-query yaourt", user="aur")

    # set locale and server timezone
    run("localectl set-locale LANG='en_US.utf8'")
    run("timedatectl set-timezone US/Central")

    # reboot for kernel upgrade
    print(yellow("rebooting."))
    sudo("reboot")
    while True:
        time.sleep(1)
        run("date")
    print(green("rebooted!"))


def install_salt(installer="aur"):
    """
    Install salt with the chosen installer.
    """
    append("/etc/hosts",
           "{0} saltmaster-private".format(env.master_server.private_ip))
    with cd("/home/aur/"):
        if installer == "aur":
            validate_configurator_version()
            sudo("yaourt --noconfirm -S salt", user="aur")
        elif installer == "aur-git":
            sudo("yaourt --noconfirm -S salt-git", user="aur")
        elif installer == "bootstrap":
            sudo("curl -L http://bootstrap.saltstack.org | sudo sh -s -- git v0.17.5")
            sudo("cp /usr/lib/systemd/system/salt-minion.service /usr/lib/systemd/system/salt-master.service")
            sed("/usr/lib/systemd/system/salt-master.service", "Minion", "Master")
            sed("/usr/lib/systemd/system/salt-master.service", "minion", "master")
        else:
            raise NotImplementedError()


def setup_salt():
    """
    Setup the salt configuration files and enable dameon on a reboot.
    See: http://salt.readthedocs.org/en/latest/topics/installation/arch.html
    """
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]

    if env.host == env.master_server.public_ip:
        run("touch /etc/salt/master")
        append("/etc/salt/master", "file_roots:\n  base:\n    - {0}".format(
               settings.REMOTE_STATES_DIR))
        append("/etc/salt/master", "pillar_roots:\n  base:\n    - {0}".format(
               settings.REMOTE_PILLARS_DIR))
        run("systemctl enable salt-master")
    run("touch /etc/salt/minion")
    append("/etc/salt/minion", "master: {0}".format(env.master_server.private_ip))
    append("/etc/salt/minion", "id: {0}".format(server.name))
    append("/etc/salt/minion", "grains:\n  roles:")
    for role in server.roles:
        append("/etc/salt/minion", "    - {0}".format(role))
    run("systemctl enable salt-minion")


def start_salt():
    """
    Starts salt master and minions.
    """
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("systemctl start salt-master")
        time.sleep(3)
        sudo("systemctl start salt-minion")


def stop_salt():
    """
    Stops salt master and minions.
    """
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("systemctl stop salt-master")
        sudo("systemctl stop salt-minion")


def restart_salt():
    """
    Restart salt master and the minions.
    """
    stop_salt()
    start_salt()
