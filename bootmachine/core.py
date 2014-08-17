"""
BOOTMACHINE: A-Z transmutation of aluminium into rhodium.
"""
import copy
import getpass
import logging
import sys
import telnetlib

from fabric.api import env, local, run, sudo
from fabric.decorators import parallel, task
from fabric.colors import blue, cyan, green, magenta, red, white, yellow  # noqa
from fabric.contrib.files import exists
from fabric.context_managers import settings as fabric_settings
from fabric.operations import reboot
from fabric.utils import abort

import settings

from bootmachine import known_hosts
from bootmachine.settings_validator import validate_settings
validate_settings(settings)


# Incrase reconnection attempts when rebooting
env.connection_attempts = 12


def import_module(module):
    """
    Allows custom providers, configurators and distros.

    Import the provider, configurator, or distro module via a string.
        ex. ``bootmachine.contrib.providers.rackspace_openstack_v2``
        ex. ``bootmachine.contrib.configurators.salt``
        ex. ``bootmachine.contrib.distros.arch_201208``
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
    Boot, bootstrap and configure all servers as per the settings.

    Usage:
        fab bootmachine
    """
    # set environment variables
    master()
    env.new_server_booted = False
    # boot new servers in serial to avoid api overlimit
    boot()
    output = local("fab each ssh_test", capture=True)
    if "CONFIGURATOR FAIL!" not in output:
        print(green("all servers are fully provisioned."))
        return

    local("fab each bootstrap_distro")
    print(green("the distro is bootstrapped on all servers."))

    local("fab each bootstrap_configurator")
    print(green("the configurator is bootstrapped on all servers."))

    configure()
    # change the following output with caution
    # runtests.sh depends on exactly the following successful output
    print(green("all servers are fully provisioned."))


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
        if not server["servername"] in [s.name for s in env.bootmachine_servers]:
            provider.bootem(settings.SERVERS)
            print(green("new server(s) have been booted."))
            env.new_server_booted = True
            print(green("all servers are booted."))
            return
    print(green("all servers are booted."))


@task
@parallel
def bootstrap_distro():
    """
    Bootstraps the distro.

    In parallel for speed.

    Usage:
        fab each bootstrap_distro
    """
    if not hasattr(env, "bootmachine_servers"):
        abort("bootstrap_distro(): Try `fab each bootstrap_distro`")

    __set_ssh_vars(env)

    if exists("/root/.bootmachine_distro_bootstrapped", use_sudo=True):
        print(green("{ip_addr} distro is already bootstrapped, skipping.".format(ip_addr=env.host)))
        return

    print(cyan("... {ip_addr} distro has begun bootstrapping .".format(ip_addr=env.host)))

    # upgrade distro
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]
    distro = import_module(server.distro_module)
    distro.bootstrap()

    sudo("touch /root/.bootmachine_distro_bootstrapped")
    print(green("{0} distro is bootstrapped.".format(server.name)))


@task
@parallel
def bootstrap_configurator():
    """
    Bootstraps the configurator.
    Installs the configurator and starts its processes.
    Does not run the configurator.

    Assumes the distro has been bootstrapped on all servers.

    In parallel for speed.

    Usage:
        fab each bootstrap_distro
    """
    if not hasattr(env, "bootmachine_servers"):
        abort("bootstrap_configurator(): Try `fab each bootstrap_configurator`")

    __set_ssh_vars(env)

    if exists("/root/.bootmachine_configurator_bootstrapped", use_sudo=True):
        print(green("{ip_addr} configurator is already bootstrapped, skipping.".format(
            ip_addr=env.host)))
        return

    print(cyan("... {ip_addr} configurator has begun bootstrapping .".format(ip_addr=env.host)))

    # bootstrap configurator
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]
    distro = import_module(server.distro_module)
    configurator.install(distro)
    configurator.setup(distro)
    configurator.start(distro)

    sudo("touch /root/.bootmachine_configurator_bootstrapped")
    print(green("{0} configurator is bootstrapped.".format(server.name)))


@task
def configure():
    """
    Configure all unconfigured servers.

    Assumes the distro and configurator have been bootstrapped on all
    servers.

    Usage:
        fab configure
    """
    master()
    configurator.launch()

    # run the configurator from the the master server, maximum of 5x
    attempts = 0
    __set_unconfigured_servers()
    while env.unconfigured_servers:
        if attempts != 0:
            local("fab master configurator.restartall")
        if attempts == 5:
            abort("unable to configure the servers")
        attempts += 1
        print(yellow("attempt #{0} for {1}".format(attempts, env.unconfigured_servers)))

        configurator.configure()
        for server in env.unconfigured_servers:
            # if configuration was a success, reboot.
            # for example, a reboot is required when rebuilding a custom kernel
            server = __set_ssh_vars(server)  # mask the server
            if server.port == int(settings.SSH_PORT):
                reboot_server(server.name)
            else:
                print(red("after #{0} attempts, server {1} is still unconfigured".format(
                          attempts, server.name)))
            __set_ssh_vars(env)  # back to default
        __set_unconfigured_servers()

    # last, ensure that SSH is configured (locked down) for each server
    output = local("fab each ssh_test", capture=True)
    if "CONFIGURATOR FAIL!" in output:
        print(red("configurator failure."))


@task
def reboot_server(name):
    """
    Simply reboot a server by name.
    The trick here is to change the env vars to that of the server
    to be rebooted. Perform the reboot and change env vars back
    to their original value.

    Usage:
        fab reboot_server:name
    """
    __shared_setup()
    try:
        server = [s for s in env.bootmachine_servers if s.name == name][0]
    except IndexError:
        abort("The server '{0}' was not found.".format(name))
    original_user = env.user
    original_host_string = env.host_string
    try:
        env.port = 22
        telnetlib.Telnet(server.public_ip, env.port)
        env.user = "root"
    except IOError:
        env.port = int(settings.SSH_PORT)
        env.user = getpass.getuser()
        telnetlib.Telnet(server.public_ip, env.port)
    env.host_string = "{0}:{1}".format(server.public_ip, env.port)

    env.keepalive = 30  # keep the ssh key active, see fabric issue #402
    with fabric_settings(warn_only=True):
        reboot()

    env.user = original_user
    env.host_string = original_host_string


@task
@parallel
def ssh_test():
    """
    Prove that ssh is open on `settings.SSH_PORT`.

    Usage:
        fab each ssh_test
    """
    for server in env.bootmachine_servers:
        if server.status != "ACTIVE":
            abort("The server '{0}' is in the '{1}' state.".format(server.name, server.status))
    __set_ssh_vars(env)
    if ":{0}".format(settings.SSH_PORT) not in env.host_string:
        local("echo 'CONFIGURATOR FAIL!'")
        return
    try:
        run("echo 'CONFIGURATOR SUCCESS!'")
        sudo("echo 'CONFIGURATOR SUCCESS!'")
    except:
        local("echo 'CONFIGURATOR FAIL!'")


@task
def each():
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
    Set the env variables common to both master() and each().
    """
    provider.set_bootmachine_servers()
    for server in env.bootmachine_servers:
        if server.name == settings.MASTER:
            env.master_server = server
        server = __set_ssh_vars(server)
        # the following prevent prompts and warnings related to ssh keys by:
        # a) skipping false man-in-the-middle warnings
        # b) adding hosts to ~/.ssh/known_hosts
        known_hosts.add(server.user, server.public_ip, server.port)


def __set_ssh_vars(valid_object):
    """
    This method takes a valid_object, either the env or a server,
    and based on the results of telnet, it sets port, user,
    host_string varibles for ssh. It also sets a configured
    variable if the SSH_PORT matches that in the settings. This
    would only match if the server is properly configured.
    """
    if valid_object == env:
        public_ip = env.host
    else:
        public_ip = valid_object.public_ip

    try:
        port = 22
        telnetlib.Telnet(public_ip, port)
    except IOError:
        port = int(settings.SSH_PORT)
        telnetlib.Telnet(public_ip, port)

    valid_object.port = port

    if valid_object.port == 22:
        valid_object.configured = False
        valid_object.user = "root"
    else:
        valid_object.configured = True
        valid_object.user = getpass.getuser()

    valid_object.host_string = "{0}:{1}".format(public_ip, port)
    return valid_object


def __set_unconfigured_servers():
    env.unconfigured_servers = []
    for server in env.bootmachine_servers:
        if server.port != int(settings.SSH_PORT):
            env.unconfigured_servers.append(server)


# Resolve issue with paramiko which occasionaly causes bootmachine to hang
# http://forum.magiksys.net/viewtopic.php?f=5&t=82
logging.getLogger("paramiko").setLevel(logging.DEBUG)
