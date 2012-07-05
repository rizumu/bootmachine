import os
import sys
import time

from fabric.api import env, local, run, sudo
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.context_managers import settings as fabric_settings
from fabric.contrib.files import contains, exists
from fabric.contrib.project import rsync_project
from fabric.decorators import task, parallel
from fabric.utils import abort

from jinja2 import Template

import settings


def install(distro):
    """
    Simply call the install method for salt using chosen distro and installer.
    """
    installer = getattr(settings, "SALT_INSTALLER_{0}".format(distro.DISTRO))
    distro.install_salt(installer)


def start(distro):
    """
    Simply call the start method for salt for the chosen distro.
    """
    distro.start_salt()


@task
@parallel
def restart():
    """
    Call the restart method for all salt masters and minions.
    """
    for server in env.bootmachine_servers:
        if env.host == server.public_ip:
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
        abort("Unable to import the module: {0}".format(module))

    distro.restart_salt()


@task
def launch():
    """
    After salt is installed, accept the minions, upload states,
    and call highstate.
    """
    if env.host != env.master_server.public_ip:
        abort("tried to launch on a non-master server")

    upload_saltstates(bootmachine=True)

    run("iptables -F")  # flush iptables before accepting minions and calling highstate
    accept_minions()
    pillar_update()

    # TODO: salt-state bug, highstate should do everying on first pass
    # highstate must be called twice, otherwise authorized_keys aren't added
    highstate()
    highstate()
    if contains("/etc/issue", "Fedora release 16"):
        # TODO: salt-state bug, Fedora isn't properly restarting ssh
        # call highstate 2x more as a workaround
        highstate()
        highstate()


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
def upload_saltstates(bootmachine=False):
    """
    Upload the salt states to all servers.
    It's a little more complicated then it needs to be,
    because we have to rsync as root and root login is disabled.
    Usage:
        fab master configurator.upload_saltstates
    """
    if env.host != env.master_server.public_ip:
        abort("tried to upload salttates on a non-master server")

    ss_dir = settings.SALTSTATES_DIR
    pillar_dir = settings.PILLAR_DIR

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
    local("scp -P {0} {1}bootmachine.sls {2}@{3}:/tmp/bootmachine.sls".format(env.port, pillar_dir, env.user, env.host))
    sudo("mv /tmp/bootmachine.sls /srv/pillar/bootmachine.sls")
    sudo("salt '*' saltutil.refresh_pillar")


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
            local("fab all configurator.restart")
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
def change_master_ip(ip):
    "TODO: allowing changing of the master ip, say on a master only rebuild."
    raise NotImplementedError()
