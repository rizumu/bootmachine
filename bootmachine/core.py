"""
BOOTMACHINE: A-Z transmutation of aluminium into rhodium.
"""
import copy
import sys
import telnetlib

from fabric.api import env, local, task, run, sudo
from fabric.decorators import parallel, task
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.contrib.files import contains, exists
from fabric.operations import put, reboot
from fabric.utils import abort

import settings

from bootmachine.settings_validator import validate_settings
validate_settings(settings)


def import_module(module):
    """
    This allows one to write a custom backend for a provider, configurator,
    or distro.

    Import the provider, configurator, or distro module via a string.
        ex. ``bootmachine.contrib.providers.rackspace_openstack_v1``
        ex. ``bootmachine.contrib.configurators.salt``
        ex. ``bootmachine.contrib.distros.arch_201110``
    """
    try:
        __import__(module)
        return sys.modules[module]
    except ImportError:
        abort("Unable to import the module: {0}".format(module))


# import provider and configurator here so their fabric tasks are properly namespaced
provider = import_module(settings.PROVIDER_MODULE)
configurator = import_module(settings.CONFIGURATOR_MODULE)


@task(default=True)
def bootmachine():
    """
    Boot & provision all servers as per the config.

    Usage:
        fab bootmachine
    """
    # set environment variables
    master()
    env.new_server_booted = False

    # boot new servers in serial to avoid api overlimit
    boot()
    print(green("all servers are booted."))

    # provision all servers in parallel for speed
    local("fab all provision")
    print(green("all servers are provisioned."))

    # run the configurator in serial on the master to configure the new servers
    master()
    for server in env.bootmachine_servers:
        if server.port != int(settings.SSH_PORT):
            configurator.launch()
            launch_attempts = 1
            break
    print(green("all servers are configured."))

    # ensure that the servers have been properly configured
    master()
    for server in env.bootmachine_servers:
        while server.port != int(settings.SSH_PORT):
            configurator.restart()
            configurator.launch()
            launch_attempts += 1
            master()
            if launch_attempts == 5:
                abort("CONFIGURATOR FAIL!")
    local("fab all reboot_servers")  # to catch cases when configurator changes the kernel
    local("fab all ssh_test")
    print(green("all servers are booted, provisioned, and configured."))


@task
@parallel
def reboot_servers():
    """
    Simply reboot the servers

    Usage:
        fab all reboot_servers
    """
    try:
        telnetlib.Telnet(env.host, 22)
        env.user = "root"
    except IOError:
        telnetlib.Telnet(env.host, int(settings.SSH_PORT))
        env.port = int(settings.SSH_PORT)
    reboot()


@task
def boot():
    """
    Boot servers as per the config.

    Usage:
        fab boot
    """
    if not hasattr(env, "bootmachine_servers"):
        master()

    servers = copy.copy(settings.SERVERS)
    while servers:
        server = servers.pop(0)
        if not server["servername"] in [server.name for server in env.bootmachine_servers]:
            provider.bootem(settings.SERVERS)
            env.new_server_booted = True
            return


@task
@parallel
def provision():
    """
    Provision all unprovisioned servers.

    Usage:
        fab all provision
    """
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]

    if int(settings.SSH_PORT) == 22:
        abort("provision(): Security Error! Change ``settings.SSH_PORT`` to something other than ``22``")

    try:
        telnetlib.Telnet(server.public_ip, 22)
        env.user = "root"
    except IOError:
        telnetlib.Telnet(server.public_ip, int(settings.SSH_PORT))
        print(green("{ip_addr} is already provisioned, skipping.".format(ip_addr=server.public_ip)))
        return

    print(cyan("... {ip_addr} has started provisioning.".format(ip_addr=server.public_ip)))

    # permanently add server to the local list of known hosts
    local("ssh {user}@{ip_addr} -o StrictHostKeyChecking=no &".format(user=env.user, ip_addr=server.public_ip))

    # upgrade distro
    distro = import_module(server.distro_module)
    distro.bootstrap()

    # bootstrap configurator
    configurator.install(distro)
    configurator.start(distro)


@task
@parallel
def ssh_test():
    """
    Prove that ssh is open on `settings.SSH_PORT`.
    """
    env.port = int(settings.SSH_PORT)
    try:
        run("echo 'CONFIGURATOR SUCCESS!'")
        sudo("echo 'CONFIGURATOR SUCCESS!'")
    except:
        abort("CONFIGURATOR FAIL!")


@task
def all():
    """
    Set the env variables for a command to be run on all servers.

    Warning::
        Bootmachine assumes 'one' master and therefore
        currently does not support a multi-master configuration.
    """
    __shared_setup()

    for server in env.bootmachine_servers:
        if server.public_ip not in env.hosts:
            env.hosts.append(server.public_ip)
        if server.public_ip not in env.all_hosts:
            env.all_hosts.append(server.public_ip)


@task
def master():
    """
    Set the env variables for a command only to be run on the master server.
    """
    __shared_setup()

    for server in env.bootmachine_servers:
        if server.name == env.master_server.name:
            env.port = server.port
            env.user = server.user
            env.hosts.append(server.public_ip)
            env.host = server.public_ip
            env.host_string = "{0}:{1}".format(server.public_ip, server.port)


def __shared_setup():
    """
    Set the env variables common to both master() and all().
    """
    provider.get_ips()

    for server in env.bootmachine_servers:
        if server.name == settings.MASTER:
            env.master_server = server
        try:
            telnetlib.Telnet(server.public_ip, 22)
            server.provisioned = False
            server.user = "root"
            server.port = 22
        except IOError:
            telnetlib.Telnet(server.public_ip, int(settings.SSH_PORT))
            server.provisioned = True
            server.user = env.user
            server.port = int(settings.SSH_PORT)
