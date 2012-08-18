import os
import sys
import time

from fabric.api import env, local, sudo
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.context_managers import settings as fabric_settings
from fabric.contrib.files import contains, exists
from fabric.contrib.project import rsync_project
from fabric.decorators import task, parallel
from fabric.utils import abort

from jinja2 import Template

from bootmachine import known_hosts

import settings


@task
def highstate(match="'*'"):
    """
    Run salt state.highstate on hosts that match.
    Usage:
        fab master configurator.highstate
    """
    if env.host != env.master_server.public_ip:
        abort("tried to highstate on a non-master server")

    sudo("salt {regex} state.highstate".format(regex=match))


@task
def upload_saltstates():
    """
    Upload the salt states to all servers.
    It's a little more complicated then it needs to be,
    because we have to rsync as root and root login is disabled.
    Usage:
        fab master configurator.upload_saltstates
    """
    if env.host != env.master_server.public_ip:
        abort("tried to upload salttates on a non-master server")

    # catch rsync issue with emacs autosave files
    for path in (settings.SALTSTATES_DIR, settings.PILLAR_DIR):
        for match in ("#*#", ".#*"):
            if local('find {0} -name "{1}"'.format(path, match), capture=True):
                abort("A temp file matching '{0}' exists in the {1} directory.".format(match, path))

    # rsync pillar and salt files to the fabric users local directory

    rsync_project(local_dir=settings.SALTSTATES_DIR, remote_dir="./salt/", delete=True,
                  extra_opts="--compress --copy-links", ssh_opts="-o StrictHostKeyChecking=no")
    rsync_project(local_dir=settings.PILLAR_DIR, remote_dir="./pillar/", delete=True,
                  extra_opts="--compress --copy-links", ssh_opts="-o StrictHostKeyChecking=no")

    # backup the jinja2 created pillar files
    if exists("/srv/pillar/salt.sls"):
        sudo("mv /srv/pillar/salt.sls /srv/salt.sls")
    if exists("/srv/pillar/users.sls"):
        sudo("mv /srv/pillar/users.sls /srv/users.sls")
    # delete the pillar and state files
    sudo("rm -rf /srv/salt && rm -rf /srv/pillar")
    # copy the rsynced versions over as root
    sudo("cp -r ./salt /srv/salt && cp -r ./pillar /srv/pillar")
    # put the jinja2 created pillar files back in place
    if exists("/srv/salt.sls"):
        sudo("mv /srv/salt.sls /srv/pillar/salt.sls")
    if exists("/srv/users.sls"):
        sudo("mv /srv/users.sls /srv/pillar/users.sls")


@task
def pillar_update():
    """
    Update the pillar files with the current server info.
    Usage:
        fab master configuration salt.pillar_update
    """
    if env.host != env.master_server.public_ip:
        abort("tried to pillar_update on a non-master server")

    pillar_dir = settings.PILLAR_DIR
    bootmachine_sls_j2 = Template(open("{0}bootmachine.sls.j2".format(pillar_dir), "r", 0).read())
    bootmachine_sls = open("{0}bootmachine.sls".format(pillar_dir), "w", 0)
    bootmachine_sls.write(bootmachine_sls_j2.render(
        bootmachine_servers=env.bootmachine_servers,
        saltmaster_hostname=settings.MASTER,
        saltmaster_public_ip=env.master_server.public_ip,
        saltmaster_private_ip=env.master_server.private_ip,
        ssh_port = settings.SSH_PORT,
        ssh_users = settings.SSH_USERS,
    ))
    # TODO: only upload and refresh when file has changes
    try:
        local("scp -P {0} {1}bootmachine.sls {2}@{3}:/tmp/bootmachine.sls".format(env.port, pillar_dir, env.user, env.host))
    except:
        known_hosts.update(env.host)
        local("scp -P {0} {1}bootmachine.sls {2}@{3}:/tmp/bootmachine.sls".format(env.port, pillar_dir, env.user, env.host))
    sudo("mv /tmp/bootmachine.sls /srv/pillar/bootmachine.sls")
    sudo("salt '*' saltutil.refresh_pillar &")  # background because it hangs on debian 6


@task
def update_master_iptables():
    """
    Update iptables rules for salt, on the salt master,
    to accept newley booted minions.

    Usage:
        fab master configurator.update_master_iptables
    """
    if env.host != env.master_server.public_ip:
        abort("tried to update_master_iptables on a non-master server")

    configurator_ports = ["4505", "4506"]  # get from settings.py?

    # Get the line in the iptables chain for inserting the new minon's
    with fabric_settings(warn_only=True):
        insert_line = sudo("iptables -L --line-numbers | grep {0}".format(configurator_ports[0]))

    if not insert_line:
        print(yellow("NOTE: iptables are wide open during first boot of a master"))
        return

    for port in configurator_ports:
        match = sudo("iptables -nvL | grep {0}".format(port))
        for server in env.bootmachine_servers:
            if server.private_ip not in match:
                sudo("iptables -I INPUT {0} -s {1} -m state --state new -m tcp -p tcp --dport {2} -j ACCEPT".format(
                    insert_line[0], server.private_ip, port))


@task
def launch():
    """
    After the salt packages are installed, accept the new minions,
    upload states, and call highstate.
    """
    if env.host != env.master_server.public_ip:
        abort("tried to launch on a non-master server")

    upload_saltstates()

    # add ipaddresses from the newly booted servers to the pillar and update
    local("fab master configurator.update_master_iptables")
    pillar_update()

    time.sleep(10)  # sleep a little to give minions a chance to become visible
    accept_minions()

    highstate()


@task
def accept_minions():
    """
    Accept salt-key's for all minions.
    Usage:
        fab master salt.accept_minions
    """
    if env.host != env.master_server.public_ip:
        abort("tried to accept minions on a non-master server")

    accepted = filter(None, sudo("salt-key --raw-out --list acc").translate(None, "'[]\ ").split(","))

    slept = 0
    while len(accepted) != len(settings.SERVERS):
        unaccepted = [s["servername"] for s in settings.SERVERS if s["servername"] not in accepted]

        with fabric_settings(warn_only=True):
            for server in unaccepted:
                sudo("salt-key --quiet --accept={0}".format(server))
        accepted = filter(None, sudo("salt-key --raw-out --list acc").translate(None, "'[]\ ").split(","))
        if len(accepted) != len(settings.SERVERS):
            local("fab each configurator.restart")
            time.sleep(5)
            slept += 5
            print(yellow("there are still unaccpeted keys, trying again."))
        if slept > 300:
            abort("After 5 minutes of attempts, there still exist unaccpeted keys.")

    print(green("all keys have been accepted."))


@task
def list_minions():
    """
    List all minions.
    Usage:
        fab master salt.list_minions
    """
    if env.host != env.master_server.public_ip:
        abort("tried to list minions on a non-master server")

    sudo("salt-key --list all")


@task
def change_master_ip(ip_address):
    "TODO: allowing changing of the master ip, say on a master only rebuild."
    raise NotImplementedError()


@task
@parallel
def restart():
    """
    Restart all salt masters and minion daemons.
    Simply wrap salt's reestart method cor the chose distro.
    """
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]
    env.servername = server.name
    env.port = server.port
    env.user = server.user

    for server in settings.SERVERS:
        if env.servername == server["servername"]:
            distro_module = server["distro_module"]

    try:
        __import__(distro_module)
        distro = sys.modules[distro_module]
    except ImportError:
        abort("Unable to import the module: {0}".format(distro_module))

    distro.restart_salt()


def revoke(servername):
    """
    Simply revoke a minion's key by servername
    """
    sudo("salt-key --quiet --delete={0}".format(servername))


def install(distro):
    """
    Install salt.
    Simply wrap salt's install method for the chosen distro and installer.
    """
    installer = getattr(settings, "SALT_INSTALLER_{0}".format(distro.DISTRO))
    distro.install_salt(installer)


def setup(distro):
    """
    Setup salt's configuration files and ensure it is enabled at reboot.
    Simply wrap salt's setup method for the chosen distro.
    """
    distro.setup_salt()


def start(distro):
    """
    Start the salt master and minion daemons.
    Simply wrap salt's start method for the chosen distro.
    """
    distro.start_salt()
