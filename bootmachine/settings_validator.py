import collections

from fabric.utils import abort
from fabric.colors import red


def validate_settings(settings):
    """
    Ensure that the settings file is valid.

    This is a work in progress, if users have errors related
    to settings, this method can be imporved to help guide them.
    """
    if not hasattr(settings, "PROVIDER_MODULE"):
        abort("The `settings.PROVIDER_MODULE` was not found in your settings.py")

    if not hasattr(settings, "CONFIGURATOR_MODULE"):
        abort("The `settings.CONFIGURATOR_MODULE` was not found in your settings.py")

    # Validate required settings exist
    required_settings = [
        "MASTER",
        "SERVERS",
        "SSH_PUBLIC_KEY",
        "SSH_PORT",
        "SSH_USERS",
    ]
    if settings.CONFIGURATOR_MODULE == "bootmachine.contrib.configurators.salt":
        required_settings.extend(["LOCAL_STATES_DIR", "LOCAL_PILLARS_DIR"])
    if settings.PROVIDER_MODULE == "bootmachine.contrib.providers.rackspace_openstack_v1":
        print(red("Rackspace Openstack API v1 is deprecated. Upgrade to v2."))
        required_settings.extend(["OPENSTACK_USERNAME", "OPENSTACK_APIKEY"])
    if settings.PROVIDER_MODULE == "bootmachine.contrib.providers.rackspace_openstack_v2":
        required_settings.extend([
            "OS_USERNAME",
            "OS_PASSWORD",
            "OS_TENANT_NAME",
            "OS_AUTH_URL",
            "OS_REGION_NAME",
            "OS_COMPUTE_API_VERSION",
        ])
    for setting in required_settings:
        if not hasattr(settings, setting):
            abort("The `{0}` setting was not found in your settings.py".format(setting))

    # Validate non-standard port
    if int(settings.SSH_PORT) == 22:
        abort("bootstrap(): Security Error! Change ``settings.SSH_PORT`` to anything except ``22``")

    # Validate unique servernames and existence of a configurator master
    servernames = [server["servername"] for server in settings.SERVERS]
    if not settings.MASTER in servernames:
        abort("The settings.MASTER server was not defined in settings.SERVERS")
    for c in collections.Counter(servernames).values():
        if c is not 1:
            abort("Each servername must be unique for each server defined in settings.SERVERS")

    # Validate server settings
    required_server_keys = [
        "servername",
        "roles",
        "flavor",
        "image",
        "distro_module",
    ]
    for server in settings.SERVERS:
        for key in required_server_keys:
            if key not in server:
                abort("The `{0}` key was not found\
for a server in the settings.SERVER dictionary".format(key, server))

    # Validate user settings
    required_user_keys = [
        "fullname",
        "username",
        "uid",
        "gid",
        "extra_groups",
        "ssh_keys",
    ]
    required_key_keys = [
        "hash",
        "enc",
        "comment",
    ]
    for user in settings.SSH_USERS:
        for key in required_user_keys:
            if key not in user:
                abort("The `{0}` key was not found\
for a server in the settings.SSH_USERS dictionary".format(key, user))
        for key in required_key_keys:
            for sshkey in user["ssh_keys"]:
                if key not in sshkey:
                    abort("The `{0}` key was not found\
for a server in a `settings.SSH_USERS` `ssh_keys` dictionary".format(key, sshkey))
