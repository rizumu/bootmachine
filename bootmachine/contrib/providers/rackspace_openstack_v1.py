import time

from telnetlib import Telnet

import openstack.compute

from fabric.api import env, local
from fabric.contrib import console
from fabric.decorators import task
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.operations import prompt
from fabric.utils import abort

import settings

"""
To view info on existing machines:
    openstack-compute list (or) fab provider

For more info on the OpenStack Compute Client:
    http://github.com/jacobian/openstack.compute
"""

COMPUTE_CONN = openstack.compute.Compute(username=settings.OPENSTACK_USERNAME,
                                         apikey=settings.OPENSTACK_APIKEY)


@task(default=True)
def list_servers(as_list=False):
    """
    Print all booted `openstack` servers.
    Set ``as_list`` to return a python list object.

    Usage:
        fab provider
    """
    print(cyan("... querying rackspace for current server list."))

    if not as_list:
        print(local("openstack-compute list"))

    bootmachine_servers = []

    # only return servers that are explicitly defined in the settings
    for booted in COMPUTE_CONN.servers.list():
        for defined in settings.SERVERS:
            if booted.name == defined["servername"]:
                booted.roles = defined["roles"]
                bootmachine_servers.append(booted)
    return bootmachine_servers


@task
def list_images(as_list=False):
    """
    Print `openstack` image (distro) options.
    Set ``as_list`` to return a python list object.

    Usage:
        fab provider.list_images
    """
    print(cyan("... querying rackspace for available images."))
    if as_list:
        return COMPUTE_CONN.servers.api.images.list()
    print(local("openstack-compute image-list"))


@task
def list_flavors(as_list=False):
    """
    Print `openstack` server size (flavor) options.
    Set ``as_list`` to return a python list object.

    Usage:
        fab provider.list_flavors

    Flavors:
        +----+---------------+-------+------+
        | ID |      Name     |  RAM  | Disk |
        +----+---------------+-------+------+
        | 1  | 256 server    | 256   | 10   |
        | 2  | 512 server    | 512   | 20   |
        | 3  | 1GB server    | 1024  | 40   |
        | 4  | 2GB server    | 2048  | 80   |
        | 5  | 4GB server    | 4096  | 160  |
        | 6  | 8GB server    | 8192  | 320  |
        | 7  | 15.5GB server | 15872 | 620  |
        +----+---------------+-------+------+
    """
    print(cyan("... querying rackspace for available flavors."))
    if as_list:
        return COMPUTE_CONN.servers.api.flavors.list()
    print(local("openstack-compute flavor-list"))


@task
def boot(servername, image, flavor=1, servers=None):
    """
    Boot a new server.
    Optionally takes an image name/id from which to clone from, or a flavor type.

    .. warning::
       It is worth the extra query and is advisable to use the image name and
       not the id. Rackspace is known to change the number of the id over time.

    Usage:
        fab provider.boot:role,servername
    """
    if not servers:
        servers = list_servers(as_list=True)

    if servername in [server.name for server in servers]:
        print(blue("{name} is already booted, skipping.".format(name=servername)))
        return
    try:
        image_id = int(image)
    except ValueError:
        for i in list_images(as_list=True):
            if i.name == image:
                image_id = i.id
                break
        else:
            abort("Image not found. Run ``openstack image-list`` to view options.")
    print(green("... sending boot request to rackspace for ``{name}``".format(name=servername)))
    local("openstack-compute boot --key {key} --image={image_id} --flavor={flavor} {name}".format(
           key=settings.SSH_PUBLIC_KEY, image_id=image_id, flavor=flavor, name=servername))
    env.new_server_booted = True


@task
def bootem(servers=None):
    """
    Boot all `openstack` servers as per the config.

    Usage:
        fab boot
        fab provider.bootem
    """
    if servers is None:
        servers = settings.SERVERS

    for server in servers:
        boot(server["servername"], server["image"], server["flavor"], env.bootmachine_servers)

    print(yellow("... verifying that all servers are ``ACTIVE``."))

    env.bootmachine_servers = list_servers(as_list=True)

    slept = 0
    sleep_interval = 10
    status = None
    while status is None:
        statuses = [n.status for n in env.bootmachine_servers]
        if ("BUILD" or "UNKNOWN") not in statuses:
            status = "ACTIVE"
            print(green("all servers are currently ``ACTIVE``!"))
        else:
            time.sleep(sleep_interval)
            slept += sleep_interval
            if slept <= 60:
                print(yellow("... waited {0} seconds.".format(slept)))
            else:
                minutes, seconds = divmod(slept, 60)
                print(yellow("... waited {0} min and {1} sec".format(minutes, seconds)))
            env.bootmachine_servers = list_servers(as_list=True)


@task
def destroy(servername, destroy_all=False, force=False):
    """
    Kill a server, destroying its data. Achtung!
    Usage:
        fab provider.destroy:servername
    """
    if not destroy_all and not force:
        reply = prompt("Permanently destroying '{0}'. Are you sure? y/N".format(servername))
        if reply is not "y":
            abort("Did not destroy {0}".format(servername))

    from bootmachine.core import configurator, master
    if not destroy_all:
        master()
        configurator.revoke(servername)

    local("openstack-compute delete {name} || true".format(name=servername))


@task
def destroyem(force=False):
    """
    Kill all servers and destroy the data. Achtung!
    Usage:
        fab provider.destroyem
    """
    if not force:
        servers = ", ".join([s["servername"] for s in settings.SERVERS])
        reply = prompt("Permanently destroying *EVERY* server:\n{0}\n\nAre you sure? y/N".format(servers))
        if reply is not "y":
            abort("Did not destroy *ANY* servers")

    for server in settings.SERVERS:
        destroy(server["servername"], destroy_all=True, force=force)


def set_bootmachine_servers(roles=None, ip_type="public", append_port=True):
    """
    Internal bootmachine method to set the Fabric env.bootmachine_servers variable.
    """
    env.bootmachine_servers = list_servers(as_list=True)
    ips = []

    for server in env.bootmachine_servers:
        if server.status != "ACTIVE":
            console.confirm("The server `{0}` is not `ACTIVE` and is in the `{1}` phase. Continue?".format(server.name, server.status))

    for server in env.bootmachine_servers:
        # Verify (by name) that the live server was defined in the settings.
        try:
            instance = [n for n in settings.SERVERS if n["servername"] == server.name][0]
        except IndexError:
            continue
        # If a ``roles`` list was passed in, verify it identically matches the server's roles.
        if roles and sorted(roles) != sorted(server["roles"]):
            continue
        if append_port:
            try:
                Telnet(server.public_ip, 22)
                server.port = 22
                ips.append(server.public_ip + ":" + "22")
            except IOError:
                Telnet(server.public_ip, int(settings.SSH_PORT))
                server.port = int(settings.SSH_PORT)
                ips.append(server.public_ip + ":" + str(settings.SSH_PORT))
        else:
            ips.append(server.addresses[ip_type][0])
        server.distro_module = [n["distro_module"] for n in settings.SERVERS if n["servername"] == server.name][0]
    return ips
