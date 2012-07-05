import os
import sys
import time

from fabric.api import cd, env, run, sudo
from fabric.context_managers import settings as fabric_settings
from fabric.contrib.files import append, contains, put, sed, uncomment
from fabric.operations import reboot

import settings


DISTRO = "ARCH_201110"
SALT_INSTALLERS = ["aur", "aur-git"]


def bootstrap():
    """
    Bootstrap Arch Linux.

    Only the bare essentials, the configurator will take care of the rest.
    """
    # manually set hostname so salt finds proper hostname via socket.gethostname()
    for server in env.bootmachine_servers:
        if server.public_ip == env.host:
            sed("/etc/hosts", "# End of file", "")
            append("/etc/hosts", "{0} {1}".format(server.public_ip, server.name))
            append("/etc/hosts", "{0} {1}".format(server.private_ip, server.name))
            append("/etc/hosts", "\n# End of file")
    # pre upgrade maintenance (updating filesystem and tzdata before pacman)
    run("pacman -Syy")
    run("rm -rf /var/run /var/lock")
    run("printf 'n\nY\n' | pacman -S --force filesystem")
    run("printf 'n\nY\n' | pacman -S tzdata")
    run("printf 'n\nY\n' | pacman -S haveged")

    # upgrade pacman
    run("pacman -S --noconfirm pacman")
    # haveged generates the entropy necessary for making a pacman gpg key
    run("rc.d start haveged", pty=False)
    run("pacman-key --init")
    run("rc.d stop haveged", pty=False)
    run("pacman -Rns --noconfirm haveged")
    # sign the master pacman keys https://wiki.archlinux.org/index.php/Pacman-key#Master_keys
    # Note: Level 3 'marginal trust' is suggested, but had to trust level of 4 because of an unknown error.
    run("for key in 6AC6A4C2 824B18E8 4C7EA887 FFF979E7 CDFD6BB0; \
           do pacman-key --recv-keys $key; pacman-key --lsign-key $key; \
           printf 'trust\n4\nquit\n' | gpg --homedir /etc/pacman.d/gnupg/ --no-permission-warning --command-fd 0 --edit-key $key; \
         done")
    # ARGH!!! printf won't work here!!!
    #run("printf 'Y\nY\nY\nY\nY\nY\nY\nY\n' | pacman-key --populate archlinux", shell=False)

    # configure new kernel and reboot (before system upgrade!!)
    run("printf 'y\ny\nY\nY\nY\nY\nY\nY\nY\nY\nY\n' | pacman --force -S  linux mkinitcpio udev")  # key accepting does work here
    sed("/etc/mkinitcpio.conf", "xen-", "xen_")  # patch: https://projects.archlinux.org/mkinitcpio.git/commit/?id=5b99f78331f567cc1442460efc054b72c45306a6
    sed("/etc/mkinitcpio.conf", "usbinput", "usbinput fsck")
    run("mkinitcpio -p linux")
    reboot()

    # full system upgrade and installtion of a few essential packages and another reboot for good measure
    run("pacman -Syyu --noconfirm")
    run("pacman -S --noconfirm base-devel")
    run("pacman -S --noconfirm curl git rsync")
    reboot()

    # install yaourt
    append("/etc/pacman.conf", "\n[archlinuxfr]\nServer = http://repo.archlinux.fr/$arch", use_sudo=True)
    run("pacman -Syy")
    run("pacman -S --noconfirm yaourt")

    # create a user, named 'aur', to safely install packages under fakeroot
    # uid and gid values auto increment from 1000
    # to prevent conficts set the 'aur' user's gid and uid to 902
    run("groupadd -g 902 aur && useradd -u 902 -g 902 -G wheel aur")
    uncomment("/etc/sudoers", "wheel.*NOPASSWD")

    # tweak sshd_config (before reboot so it is restarted!) so fabric can sftp with contrib.files.put, see:
    # http://stackoverflow.com/questions/10221839/cant-use-fabric-put-is-there-any-server-configuration-needed
    sed("/etc/ssh/sshd_config", "Subsystem sftp /usr/lib/openssh/sftp-server", "Subsystem sftp internal-sftp")
    run("rc.d restart sshd", pty=False)


def install_salt(installer="aur"):
    """
    Install salt from the AUR.
    """
    # TODO: figure out how to run yaourt under fakeroot
    # TODO: support installation or freezing at an older version
    if installer == "aur":
        sudo("yaourt -S --noconfirm salt", user="aur")
    elif installer == "aur-git":
        sudo("yaourt -S --noconfirm salt-git", user="aur")
    else:
        raise NotImplementedError()


def start_salt():
    """
    See: http://salt.readthedocs.org/en/latest/topics/installation/arch.html

    Upload the bootmachine's bundled salt-states.
    Launch the salt-master daemon on the saltmaster server.
    Launch a salt-minion daemon on all servers, including the saltmaster.
    """
    run("cp /etc/salt/minion.template /etc/salt/minion")
    if env.host == env.master_server.public_ip:
        run("cp /etc/salt/master.template /etc/salt/master")
        sed("/etc/rc.conf", "crond sshd", "crond sshd @salt-master @salt-minion")
        run("rc.d start salt-master", pty=False)
    else:
        sed("/etc/rc.conf", "crond sshd", "crond sshd @salt-minion")
    sed("/etc/salt/minion", "#master: salt", "master: {0}".format(env.master_server.private_ip))
    run("rc.d start salt-minion", pty=False)


def restart_salt():
    """
    Restarts salt master and/or minions.
    """
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("rc.d restart salt-master", pty=False)
            time.sleep(3)
            sudo("rc.d restart salt-minion", pty=False)
        else:
            sudo("rc.d restart salt-minion", pty=False)
