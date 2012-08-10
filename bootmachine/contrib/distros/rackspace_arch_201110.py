import time

from fabric.api import env, run, sudo
from fabric.context_managers import cd, settings as fabric_settings
from fabric.contrib.files import append, sed, uncomment
from fabric.operations import reboot


DISTRO = "ARCH_201110"
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
    run("pacman -Syy")
    run("rm -rf /var/run /var/lock")
    run("printf 'n\nY\n' | pacman -S --force filesystem")
    run("printf 'n\nY\n' | pacman -S tzdata")

    # https://www.archlinux.org/news/the-lib-directory-becomes-a-symlink/
    run("pacman --noconfirm -U http://pkgbuild.com/~allan/glibc-2.16.0-1-x86_64.pkg.tar.xz")
    run("rm /etc/profile.d/locale.sh")

    # haveged generates the entropy necessary for making the pacman gpg key
    run("printf 'n\nY\n' | pacman -S haveged")
    run("rc.d start haveged", pty=False)

    # upgrade everything except glibc
    run("printf 'n\nY\nY\nY\nY\nY\nY\nY\nY\nY\nY\nY\nY\nY\n' | pacman -Su --ignore glibc")

    # configure pacman
    run("pacman-key --init")
    run("rc.d stop haveged", pty=False)
    run("pacman --noconfirm -Rns haveged")
    # sign the master pacman keys https://wiki.archlinux.org/index.php/Pacman-key#Master_keys
    # Note: Level 3 'marginal trust' is suggested, but had to trust level of 4 because of an unknown error.
    run("for key in 6AC6A4C2 824B18E8 4C7EA887 FFF979E7 CDFD6BB0; \
           do pacman-key --recv-keys $key; pacman-key --lsign-key $key; \
           printf 'trust\n4\nquit\n' | gpg --homedir /etc/pacman.d/gnupg/ --no-permission-warning --command-fd 0 --edit-key $key; \
         done")
    # ARGH!!! printf won't work here!!!
    #run("printf 'Y\nY\nY\nY\nY\nY\nY\nY\n' | pacman-key --populate archlinux", shell=False)

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

    # more glibc crap, uninstall non-pacman rackspace installed packages
    run("rm -rf /lib/modules")
    run("pacman --noconfirm -Rns xe-guest-utilities kernel26-xen")
    with cd("/tmp/"):
        sudo("yaourt --noconfirm -S xe-guest-utilities", user="aur")

    # finally we can upgrade glibc and run a successful full system upgrade
    run("pacman --noconfirm -Su")

    # tweak sshd_config (before reboot so it is restarted!) so fabric can sftp with contrib.files.put, see:
    # http://stackoverflow.com/questions/10221839/cant-use-fabric-put-is-there-any-server-configuration-needed
    sed("/etc/ssh/sshd_config", "Subsystem sftp /usr/lib/openssh/sftp-server", "Subsystem sftp internal-sftp")
    run("rc.d restart sshd", pty=False)

    # force netcfg to automatically connect to eth0 and eth1 on reboot
    sed("/etc/conf.d/netcfg", "NETWORKS=\(last\)", "NETWORKS=(@eth0 @eth1)")
    sed("/etc/rc.conf", "NETWORKS=\(eth1 eth0\)", "")

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
    Starts salt master and minions.
    """
    # use warn_only to catch already running errors
    # probably should use pgrep instead
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("rc.d start salt-master", pty=False)
            time.sleep(3)
        sudo("rc.d start salt-minion", pty=False)


def restart_salt():
    """
    Restarts salt master and minions.
    """
    # use warn_only to catch already running errors
    # probably should use pgrep instead
    with fabric_settings(warn_only=True):
        if env.host == env.master_server.public_ip:
            sudo("rc.d restart salt-master", pty=False)
            time.sleep(3)
        sudo("rc.d restart salt-minion", pty=False)
