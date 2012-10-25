import time

from fabric.api import env, run, sudo
from fabric.context_managers import cd, settings as fabric_settings
from fabric.contrib.files import append, sed, uncomment
from fabric.operations import reboot


DISTRO = "ARCH_201208"
SALT_INSTALLERS = ["aur", "aur-git"]


def bootstrap():
    """
    Bootstrap Arch Linux.

    Only the bare essentials, the configurator will take care of the rest.
    """
    # manually set hostname so salt finds it via socket.gethostname()
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]
    sed("/etc/hosts", "# End of file", "")
    if server.public_ip == env.host:
        append("/etc/hosts", "{0} {1}".format(server.public_ip, server.name))
        append("/etc/hosts", "{0} {1}".format(server.private_ip, server.name))
        append("/etc/hosts", "{0} {1}".format(server.private_ip, server.name))
    # add the saltmaster-private last
    append("/etc/hosts", "{0} saltmaster-private".format(env.master_server.private_ip))
    append("/etc/hosts", "\n# End of file")

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
    run("groupadd -g 902 aur && useradd -u 902 -g 902 -G wheel aur")
    uncomment("/etc/sudoers", "wheel.*NOPASSWD")

    # upgrade non-pacman rackspace installed packages
    with cd("/tmp/"):
        sudo("yaourt --noconfirm -S xe-guest-utilities", user="aur")

    # tweak sshd_config (before reboot so it is restarted!) so fabric can sftp with contrib.files.put, see:
    # http://stackoverflow.com/questions/10221839/cant-use-fabric-put-is-there-any-server-configuration-needed
    sed("/etc/ssh/sshd_config", "Subsystem sftp /usr/lib/openssh/sftp-server", "Subsystem sftp internal-sftp")
    run("rc.d restart sshd", pty=False)

    # upgrade grub
    run("mv /boot/grub /boot/grub-legacy")
    run("printf 'y\nY\nY\nY\nY\nY\nY\nY\nY\nY\n' | pacman -S grub-bios")
    with fabric_settings(warn_only=True):
        run("modprobe dm_mod")
    run("grub-install --directory=/usr/lib/grub/i386-pc --target=i386-pc --boot-directory=/boot --recheck --debug /dev/xvda")
    run("grub-mkconfig -o /boot/grub/grub.cfg")

    # configure new kernel and reboot
    sed("/etc/mkinitcpio.conf", "xen-", "xen_")  # see: https://projects.archlinux.org/mkinitcpio.git/commit/?id=5b99f78331f567cc1442460efc054b72c45306a6
    sed("/etc/mkinitcpio.conf", "usbinput", "usbinput fsck")
    run("mkinitcpio -p linux")
    reboot()


def install_salt(installer="aur"):
    """
    Install salt with the chosen installer.
    """
    with cd("/tmp/"):
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

    run("cp /etc/salt/minion.template /etc/salt/minion")
    if env.host == env.master_server.public_ip:
        run("cp /etc/salt/master.template /etc/salt/master")
        sed("/etc/rc.conf", "crond sshd", "crond sshd iptables @salt-master @salt-minion")
    else:
        sed("/etc/rc.conf", "crond sshd", "crond sshd iptables @salt-minion")

    sed("/etc/salt/minion", "#master: salt", "master: saltmaster-private")
    append("/etc/salt/minion", "grains:\n  roles:")
    for role in server.roles:
        append("/etc/salt/minion", "    - {0}".format(role))


def start_salt():
    """
    Starts salt master and minions if not already running.
    """
    with fabric_settings(warn_only=True):
        master_running = run("pgrep salt-master")
        minion_running = run("pgrep salt-minion")
    if not master_running and env.host == env.master_server.public_ip:
        sudo("rc.d start salt-master")
        time.sleep(3)
    if not minion_running:
        sudo("rc.d start salt-minion")


def restart_salt():
    """
    Restarts salt master and minions.
    """
    with fabric_settings(warn_only=True):
        master_running = run("pgrep salt-master")
        minion_running = run("pgrep salt-minion")
    if env.host == env.master_server.public_ip:
        if master_running:
            sudo("rc.d restart salt-master")
        else:
            sudo("rc.d start salt-master")
        time.sleep(3)
    if minion_running:
        sudo("rc.d restart salt-minion")
    else:
        sudo("rc.d start salt-minion")
