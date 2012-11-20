import time

from fabric.api import env, run, sudo
from fabric.context_managers import cd, settings as fabric_settings
from fabric.contrib.files import append, sed, uncomment
from fabric.operations import reboot

import settings


DISTRO = "ARCH_201208"
SALT_INSTALLERS = ["aur", "aur-git"]


def bootstrap():
    """
    Bootstrap Arch Linux.

    Only the bare essentials, the configurator will take care of the rest.
    """
    # pre upgrade maintenance (updating filesystem and tzdata before pacman)
    run("pacman --noconfirm -Syyu")

    # install essential packages
    run("pacman --noconfirm -S base-devel")
    run("pacman --noconfirm -S curl git rsync")
    append("/etc/pacman.conf", "\n[archlinuxfr]\nServer = http://repo.archlinux.fr/$arch", use_sudo=True)
    run("pacman -Syy")
    run("pacman --noconfirm -S yaourt")

    # create a user, named 'aur', to safely install AUR packages under fakeroot
    # uid and gid values auto increment from 1000
    # to prevent conficts set the 'aur' user's gid and uid to 902
    run("groupadd -g 902 aur && useradd -m -u 902 -g 902 -G wheel aur")
    uncomment("/etc/sudoers", "wheel.*NOPASSWD")

    # upgrade non-pacman rackspace installed packages
    with cd("/home/aur/"):
        sudo("yaourt --noconfirm -S xe-guest-utilities", user="aur")

    # upgrade grub
    run("mv /boot/grub /boot/grub-legacy")
    run("printf 'y\nY\nY\nY\nY\nY\nY\nY\nY\nY\n' | pacman -S grub-bios")
    with fabric_settings(warn_only=True):
        run("modprobe dm_mod")
    run("grub-install --directory=/usr/lib/grub/i386-pc --target=i386-pc --boot-directory=/boot --recheck --debug /dev/xvda")
    run("grub-mkconfig -o /boot/grub/grub.cfg")

    # tweak sshd_config (before reboot so it is restarted!) so fabric can sftp with contrib.files.put, see:
    # http://stackoverflow.com/questions/10221839/cant-use-fabric-put-is-there-any-server-configuration-needed
    sed("/etc/ssh/sshd_config", "Subsystem sftp /usr/lib/openssh/sftp-server", "Subsystem sftp internal-sftp")

    # configure new kernel before reboot
    sed("/etc/mkinitcpio.conf", "xen-", "xen_")  # see: https://projects.archlinux.org/mkinitcpio.git/commit/?id=5b99f78331f567cc1442460efc054b72c45306a6
    sed("/etc/mkinitcpio.conf", "usbinput", "usbinput fsck")
    run("mkinitcpio -p linux")

    # a pure systemd installation
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]
    append("/etc/hostname", server.name)
    append("/etc/locale.conf", "LANG=en_US.UTF-8\nLC_COLLATE=C")
    run("printf 'y\nY\n' | pacman -S systemd-sysvcompat")
    reboot()
    run("pacman --noconfirm -Rns initscripts")
    for daemon in ["netcfg", "sshd", "syslog-ng"]:
        run("systemctl enable {0}.service".format(daemon))


def install_salt(installer="aur"):
    """
    Install salt with the chosen installer.
    """
    append("/etc/hosts",
           "{0} saltmaster-private".format(env.master_server.private_ip))
    with cd("/home/aur/"):
        if installer == "aur":
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
        run("systemctl enable salt-master.service")
    run("touch /etc/salt/minion")
    append("/etc/salt/minion", "master: {0}".format(env.master_server.private_ip))
    append("/etc/salt/minion", "id: {0}".format(server.name))
    append("/etc/salt/minion", "grains:\n  roles:")
    for role in server.roles:
        append("/etc/salt/minion", "    - {0}".format(role))
    run("systemctl enable salt-minion.service")


def start_salt():
    """
    Starts salt master and minions if not already running.
    """
    with fabric_settings(warn_only=True):
        master_running = run("pgrep salt-master")
        minion_running = run("pgrep salt-minion")
    if not master_running and env.host == env.master_server.public_ip:
        sudo("systemctl start salt-master.service")
        time.sleep(3)
    if not minion_running:
        sudo("systemctl start salt-minion.service")


def restart_salt():
    """
    Restarts salt master and minions.
    """
    with fabric_settings(warn_only=True):
        master_running = run("pgrep salt-master")
        minion_running = run("pgrep salt-minion")
    if env.host == env.master_server.public_ip:
        if master_running:
            sudo("systemctl restart salt-master.service")
        else:
            sudo("systemctl restart salt-master.service")
            time.sleep(3)
    if minion_running:
        sudo("systemctl restart salt-minion.service")
    else:
        sudo("systemctl start salt-minion.service")
