import time

from telnetlib import Telnet

import novaclient.v1_1

from fabric.api import env, local
from fabric.contrib import console
from fabric.decorators import task
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.operations import prompt
from fabric.utils import abort

import settings

"""
To view info on existing machines:
    nova list (or) fab provider

For more info on the Python Nova Client:
    https://github.com/openstack/python-novaclient
"""

COMPUTE_CONN = novaclient.v1_1.client.Client(
    settings.OS_USERNAME,
    settings.OS_PASSWORD,
    settings.OS_TENANT_NAME,
    settings.OS_AUTH_URL,
    region_name=settings.OS_REGION_NAME,
)


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
        print(local("nova list"))

    bootmachine_servers = []

    # only return servers that are explicitly defined in the settings
    for booted in COMPUTE_CONN.servers.list():
        for defined in settings.SERVERS:
            if booted.name == defined["servername"]:
                # wait for newly booted servers to be assigned addresses
                while ("public" or "private") not in booted.addresses:
                    time.sleep(10)
                    booted = [s for s in COMPUTE_CONN.servers.list() if s.name == booted.name][0]
                booted.roles = defined["roles"]
                public_addresses = booted.addresses["public"]
                private_addresses = booted.addresses["private"]
                booted.public_ip = [a for a in public_addresses if a["version"] == 4][0]["addr"]
                booted.private_ip = [a for a in private_addresses if a["version"] == 4][0]["addr"]
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
    print(local("nova image-list"))


@task
def list_flavors(as_list=False):
    """
    Print `openstack` server size (flavor) options.
    Set ``as_list`` to return a python list object.

    Usage:
        fab provider.list_flavors

    Flavors:
        +----+-------------------------+-----------+------+----------+-------+-------------+
        | ID |           Name          | Memory_MB | Swap | Local_GB | VCPUs | RXTX_Factor |
        +----+-------------------------+-----------+------+----------+-------+-------------+
        | 2  | 512MB Standard Instance | 512       | 512  | 20       | 1     | 2.0         |
        | 3  | 1GB Standard Instance   | 1024      | 1024 | 40       | 1     | 3.0         |
        | 4  | 2GB Standard Instance   | 2048      | 2048 | 80       | 2     | 6.0         |
        | 5  | 4GB Standard Instance   | 4096      | 2048 | 160      | 2     | 10.0        |
        | 6  | 8GB Standard Instance   | 8192      | 2048 | 320      | 4     | 15.0        |
        | 7  | 15GB Standard Instance  | 15360     | 2048 | 620      | 6     | 20.0        |
        | 8  | 30GB Standard Instance  | 30720     | 2048 | 1200     | 8     | 30.0        |
        +----+-------------------------+-----------+------+----------+-------+-------------+
    """
    print(cyan("... querying rackspace for available flavors."))
    if as_list:
        return COMPUTE_CONN.servers.api.flavors.list()
    print(local("nova flavor-list"))


@task
def boot(servername, image, flavor=2, servers=None):
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
    local("nova boot --image={image_id} --flavor={flavor} {name} --file /root/.ssh/authorized_keys={key}".format(
           image_id=image_id, flavor=flavor, name=servername, key=settings.SSH_PUBLIC_KEY))
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

    local("nova delete {name} || true".format(name=servername))

    # calling list_servers immediately after deleting returns the deleted servers
    if not destroy_all:
        time.sleep(5)
        env.bootmachine_servers = list_servers(as_list=True)


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
        destroy(server["servername"], destroy_all=True)
    time.sleep(5)


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
