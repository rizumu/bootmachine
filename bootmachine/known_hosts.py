from fabric.api import env, local


def add(public_ip):
    """
    Permanently add server to the local list of known hosts, but
    first remove any matching keys to prevent conflicts.
    """
    if search(public_ip):
        remove(public_ip)
    local("ssh {user}@{ip_addr} -o StrictHostKeyChecking=no &".format(user=env.user, ip_addr=public_ip))


def update(public_ip):
    """
    Updating a key is the same as adding.
    """
    add(public_ip)


def search(public_ip):
    """
    Search for the ``public_ip`` in the ~/.ssh/known_hosts file,
    returning any occurrences found.
    """
    result = local("ssh-keygen -H -F {0}".format(public_ip), capture=True)
    if result:
        return True
    else:
        return False


def remove(public_ip):
    """
    Removes all keys belonging to ``public_ip`` from the ~/.ssh/known_hosts file.
    """
    local("ssh-keygen -R {0}".format(public_ip))
