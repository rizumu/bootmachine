import os
import sys
import time

from fabric.api import env, local, sudo
from fabric.colors import blue, cyan, green, magenta, red, white, yellow  # noqa
from fabric.context_managers import settings as fabric_settings
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.utils import abort

from jinja2 import Template

from bootmachine import known_hosts

import settings


@task
def configure(match="'*'"):
    """
    Run salt state.highstate on hosts that match.
    Usage:
        fab master configurator.configure
    """
    highstate(match)


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
    if not exists(settings.REMOTE_STATES_DIR, use_sudo=True):
        sudo("mkdir --parents {0}".format(settings.REMOTE_STATES_DIR))

    # catch rsync issue with emacs autosave files
    temp_files = []
    for path in (settings.LOCAL_STATES_DIR, settings.LOCAL_PILLARS_DIR):
        for match in ("#*#", ".#*"):
            temp_file = local('find {0} -name "{1}"'.format(path, match), capture=True)
            if temp_file:
                temp_files.append(temp_file)
    if temp_files:
        print(red("Temp files must not exist in the saltstates or pillars dirs."))
        for temp_file in temp_files:
            print(yellow("found: {0}".format(temp_file)))
        abort("Found temp files in the saltstates or pillars dirs.")

    # rsync pillar and salt files to the fabric users local directory
    local('rsync -a -e "ssh -p {0}" --rsync-path="sudo rsync" {1} {2}@{3}:{4}'.format(
        env.port, settings.LOCAL_STATES_DIR, env.user, env.host, settings.REMOTE_STATES_DIR))
    local('rsync -a -e "ssh -p {0}" --rsync-path="sudo rsync" {1} {2}@{3}:{4}'.format(
        env.port, settings.LOCAL_PILLARS_DIR, env.user, env.host, settings.REMOTE_PILLARS_DIR))


@task
def pillar_update():
    """
    Update the pillar files with the current server info.
    Usage:
        fab master configuration salt.pillar_update
    """
    if env.host != env.master_server.public_ip:
        abort("tried to pillar_update on a non-master server")

    local_pillars_dir = settings.LOCAL_PILLARS_DIR
    remote_pillars_dir = settings.REMOTE_PILLARS_DIR
    if not exists(remote_pillars_dir, use_sudo=True):
        sudo("mkdir --parents {0}".format(remote_pillars_dir))
    bootmachine_sls_j2 = Template(
        open(os.path.join(local_pillars_dir, "bootmachine.sls.j2"), "r", 0).read())
    bootmachine_sls = open(os.path.join(local_pillars_dir, "bootmachine.sls"), "w", 0)
    bootmachine_sls.write(bootmachine_sls_j2.render(
        bootmachine_servers=env.bootmachine_servers,
        salt_remote_states_dir=settings.REMOTE_STATES_DIR,
        salt_remote_pillars_dir=remote_pillars_dir,
        saltmaster_hostname=settings.MASTER,
        saltmaster_public_ip=env.master_server.public_ip,
        saltmaster_private_ip=env.master_server.private_ip,
        ssh_port=settings.SSH_PORT,
        ssh_users=settings.SSH_USERS,
    ))

    # TODO: only upload and refresh when file has changes
    home_dir = local("eval echo ~${0}".format(env.user), capture=True)
    if exists(home_dir, use_sudo=True):
        scp_dir = home_dir
    else:
        scp_dir = "/tmp/"
    try:
        local("scp -P {0} {1} {2}@{3}:{4}".format(
              env.port,
              os.path.join(local_pillars_dir, "bootmachine.sls"),
              env.user,
              env.host,
              os.path.join(scp_dir, "bootmachine.sls")))
    except:
        known_hosts.update(env.host)
        local("scp -P {0} {1} {2}@{3}:$(eval echo ~${4})bootmachine.sls".format(
              env.port,
              os.path.join(local_pillars_dir, "bootmachine.sls"),
              env.user,
              env.host,
              scp_dir))
    sudo("mv {0} {1}".format(
        os.path.join(scp_dir, "bootmachine.sls"),
        os.path.join(remote_pillars_dir, "bootmachine.sls")))
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
                sudo("iptables -I INPUT {0} -s {1} -m state --state new -m tcp -p tcp \
                --dport {2} -j ACCEPT".format(insert_line[0], server.private_ip, port))


@task
def launch():
    """
    After the salt packages are installed, accept the new minions,
    upload states.
    Usage:
        fab master configurator.launch
    """
    if env.host != env.master_server.public_ip:
        abort("tried to launch on a non-master server")

    upload_saltstates()

    # add ipaddresses from the newly booted servers to the pillar and update
    local("fab master configurator.update_master_iptables")
    pillar_update()

    time.sleep(10)  # sleep a little to give minions a chance to become visible
    accept_minions()
    local("fab master configurator.restartall")


@task
def accept_minions():
    """
    Accept salt-key's for all minions.
    Usage:
        fab master configurator.accept_minions
    """
    if env.host != env.master_server.public_ip:
        abort("tried to accept minions on a non-master server")

    def __get_accepted_minions():
        """TODO: remove when all distros support salt 0.10.5"""
        try:
            accepted = eval(sudo("salt-key --yes --out raw --list acc"))
        except:
            accepted = eval(sudo("salt-key --raw-out --list acc"))
        if type(accepted) == dict:
            return accepted["minions"]
        else:
            return accepted  # support salt version < 0.10.5
    minions = __get_accepted_minions()
    slept = 0

    while len(minions) != len(settings.SERVERS):
        unaccepted = [s["servername"] for s in settings.SERVERS if s["servername"] not in minions]

        with fabric_settings(warn_only=True):
            for server in unaccepted:
                sudo("salt-key --quiet --accept={0} --yes".format(server))
        minions = __get_accepted_minions()
        if len(minions) != len(settings.SERVERS):
            local("fab master configurator.restartall")
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
        fab master configurator.list_minions
    """
    if env.host != env.master_server.public_ip:
        abort("tried to list minions from a non-master server")

    sudo("salt-key --list all")


@task
def change_master_ip(ip_address):
    "TODO: allowing changing of the master ip, say on a master only rebuild."
    raise NotImplementedError()


@task
def restartall():
    """
    Restart first the salt master than all minion daemons.
    Usage:
        fab master configurator.restartall
    """
    if env.host != env.master_server.public_ip:
        abort("tried to restartall from a non-master server")

    for server in env.bootmachine_servers:
        stop(__getdistro_setenv(server.name))
    time.sleep(5)
    start(__getdistro_setenv(env.master_server.name))
    for server in env.bootmachine_servers:
        if server.name != env.master_server.name:
            start(__getdistro_setenv(server.name))
    env.servername = env.master_server.name
    env.host = server.public_ip
    env.host_string = "{0}:{1}".format(env.master_server.public_ip,
                                       env.master_server.port)
    env.hosts = [env.master_server.public_ip]
    env.port = env.master_server.port
    env.user = env.master_server.user


def revoke(servername):
    """
    Simply revoke a minion's key by servername
    """
    sudo("salt-key --quiet --yes --delete={0}".format(servername))


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


def stop(distro):
    """
    Stop the salt master and minion daemons.
    Simply wrap salt's stop method for the chosen distro.
    """
    distro.stop_salt()


def __getdistro_setenv(servername):
    """
    """
    server = [s for s in env.bootmachine_servers
              if s.name == servername][0]
    env.servername = server.name
    env.host = server.public_ip
    env.host_string = "{0}:{1}".format(server.public_ip, server.port)
    env.hosts = [server.public_ip]
    env.port = server.port
    env.user = server.user
    distro_module = [s for s in settings.SERVERS
                     if s["servername"] == server.name][0]["distro_module"]
    try:
        __import__(distro_module)
        return sys.modules[distro_module]
    except ImportError:
        abort("Unable to import the module: {0}".format(distro_module))
