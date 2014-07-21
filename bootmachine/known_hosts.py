from fabric.api import local


def add(user, public_ip, port):
    """
    Permanently add server to the local list of known hosts, but
    first remove any matching keys to prevent conflicts.
    """
    # if search(public_ip):
    #     remove(public_ip)
    local('ssh -q {user}@{ip_addr} -p {port} -o StrictHostKeyChecking=no "echo 2>&1"'.format(
        user=user, ip_addr=public_ip, port=port))


def update(user, public_ip, port):
    """
    Updating a key is the same as adding.
    """
    add(public_ip, port)


def search(public_ip):
    """
    Search for the ``public_ip`` in the ~/.ssh/known_hosts file,
    returning any occurrences found.
    """
    result = local("ssh-keygen -H -F {0}".format(public_ip), capture=True)
    return bool(result)


def remove(public_ip):
    """
    Removes all keys belonging to ``public_ip`` from the ~/.ssh/known_hosts file.
    """
    local("ssh-keygen -R {0}".format(public_ip))
