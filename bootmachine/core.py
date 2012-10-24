
"""
BOOTMACHINE: A-Z transmutation of aluminium into rhodium.
"""
import copy
import getpass
import logging
import sys
import telnetlib

from fabric.api import env, local, task, run, sudo
from fabric.decorators import parallel, task
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.contrib.files import exists
from fabric.exceptions import NetworkError
from fabric.network import connect
from fabric.operations import reboot
from fabric.utils import abort

import settings

from bootmachine import known_hosts
from bootmachine.settings_validator import validate_settings
validate_settings(settings)


def import_module(module):
    """
    This allows one to write a custom backend for a provider, configurator,
    or distro.

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

    # bootstrap all servers in parallel for speed
    local("fab each bootstrap")
    print(green("all servers are bootstrapped."))

    # run the configurator from the the master server, maximum of 5x
    master()
    __set_unconfigured_servers()
    while env.unconfigured_servers and env.configure_attempts != 5:
        print(env.unconfigured_servers, env.configure_attempts)
        configure()

    # lastly, double check that the SSH settings for each server are correct
    output = local("fab each ssh_test", capture=True)
    if "CONFIGURATOR FAIL!" in output:
        print(red("configurator failure."))
    else:
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
        if not server["servername"] in [server.name for server in env.bootmachine_servers]:
            provider.bootem(settings.SERVERS)
            print(green("new server(s) have been booted."))
            env.new_server_booted = True
            print(green("all servers are booted."))
            return
    print(green("all servers are booted."))


@task
@parallel
def bootstrap():
    """
    Bootstraps the configurator on all newly booted servers.
    Installs the configurator and starts its processes.
    Does not run the configurator.

    Usage:
        fab each bootstrap
    """
    if not hasattr(env, "bootmachine_servers"):
        abort("bootstrap(): Try `fab each bootstrap`")

    if int(settings.SSH_PORT) == 22:
        abort("bootstrap(): Security Error! Change ``settings.SSH_PORT`` to something other than ``22``")

    __set_ssh_vars(env)

    if exists("/root/.bootmachine_bootstrapped", use_sudo=True):
        print(green("{ip_addr} is already bootstrapped, skipping.".format(ip_addr=env.host)))
        return

    print(cyan("... {ip_addr} has begun bootstrapping .".format(ip_addr=env.host)))

    # upgrade distro
    server = [s for s in env.bootmachine_servers if s.public_ip == env.host][0]
    distro = import_module(server.distro_module)
    distro.bootstrap()

    # bootstrap configurator
    configurator.install(distro)
    configurator.setup(distro)
    configurator.start(distro)
    run("iptables -F")  # flush defaults before configuring
    run("touch /root/.bootmachine_bootstrapped")

    print(green("{0} is bootstrapped.".format(server.name)))


@task
def configure():
    """
    Configure all unconfigured servers.

    Usage:
        fab configure
    """
    master()
    __set_unconfigured_servers()

    # run the configurator and refresh the env variables by calling master()
    if env.unconfigured_servers:
        configurator.launch()
        env.configure_attempts += 1
        master()
        # determine if configuration was a success and reboot just in case.
        # for example, a reboot is required when rebuilding a custom kernel
        for server in env.unconfigured_servers:
            server = __set_ssh_vars(server)
            if server.port == int(settings.SSH_PORT):
                reboot_server(server.name)
            else:
                print(red("after {0} attempt, server {1} is still unconfigured".format(env.configure_attempts, server.name)))

    __set_unconfigured_servers()
    __set_ssh_vars(env)
    if not env.unconfigured_servers:
        print(green("all servers are configured."))


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
    server = [s for s in env.bootmachine_servers if s.name == name][0]
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

        # prevent prompts and warnings related to ssh keys:
        # a) skips false man-in-the-middle warnings
        # b) adds a missing key to ~/.ssh/known_hosts
        try:
            connect(server.user, server.public_ip, server.port)
        except NetworkError:
            known_hosts.add(server.public_ip)

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
    if not hasattr(env, "configure_attempts"):
        env.configure_attempts = 0

    env.unconfigured_servers = []
    for server in env.bootmachine_servers:
        if server.port != int(settings.SSH_PORT):
            env.unconfigured_servers.append(server)


# Resolve issue with paramiko which occasionaly causes bootmachine to hang
# http://forum.magiksys.net/viewtopic.php?f=5&t=82
logging.getLogger("paramiko").setLevel(logging.DEBUG)
