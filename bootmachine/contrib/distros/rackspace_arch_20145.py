import time
import urllib2

from fabric.api import env, run, sudo
from fabric.context_managers import cd, settings as fabric_settings
from fabric.contrib.files import append, contains, sed, uncomment
from fabric.operations import reboot
from fabric.utils import abort

import settings


DISTRO = "ARCH_20145"
SALT_INSTALLERS = ["pacman", "aur", "aur-git"]


def bootstrap():
    """
    Bootstrap Arch Linux.

    Only the bare essentials, the configurator will take care of the rest.
    """
    # put new mkinitcpio.conf in place
    run("mv /etc/mkinitcpio.conf.pacnew /etc/mkinitcpio.conf")
    sed("/etc/mkinitcpio.conf",
        'MODULES=""',
        'MODULES="xen-blkfront xen-fbfront xen-kbdfront xen-netfront xen-pcifront xenbus_probe_frontend xenfs"')  # nopep8
    sed("/etc/mkinitcpio.conf",
        'HOOKS="base udev autodetect modconf block filesystems keyboard fsck',
        'HOOKS="base udev block filesystems shutdown autodetect"')

    # upgrade pacakges
    run("pacman --noconfirm -Syu")

    # # put new pacman.conf in place
    # run("mv /etc/pacman.conf.pacnew /etc/pacman.conf")

    # install essential packages
    run("pacman --noconfirm -S base-devel")
    run("pacman --noconfirm -S curl git rsync")

    # allow users in the wheel group to sudo without a password
    uncomment("/etc/sudoers", "wheel.*NOPASSWD")

    # create a user, named 'aur', to safely install AUR packages under fakeroot
    # uid and gid values auto increment from 1000
    # to prevent conficts set the 'aur' user's gid and uid to 902
    run("groupadd -g 902 aur && useradd -m -u 902 -g 902 -G wheel aur")

    # install yaourt (TODO: this can be moved into salt)
    sudo("rm -rf /home/aur/.builds && mkdir /home/aur/.builds/", user="aur")
    with cd("/home/aur/.builds/"):
        sudo("bash <(curl aur.sh) -si --noconfirm package-query yaourt", user="aur")

    if not contains("/proc/1/comm", "systemd"):
        abort("systemd is not installed properly")
    run("locale-gen")
    run("localectl set-locale LANG='en_US.utf8'")
    run("timedatectl set-timezone US/Central")


def install_salt(installer="pacman"):
    """
    Install salt with the chosen installer.
    """
    append("/etc/hosts",
           "{0} saltmaster-private".format(env.master_server.private_ip))
    with cd("/home/aur/"):
        if installer == "pacman":
            run("pacman --noconfirm -S salt")
        elif installer == "aur":
            sudo("yaourt --noconfirm -S salt", user="aur")
        elif installer == "aur-git":
            sudo("yaourt --noconfirm -S salt-git", user="aur")
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
