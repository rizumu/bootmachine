import os

from bootmachine.settings_tests import *  # noqa


CONFIGURATOR_MODULE = "bootmachine.contrib.configurators.salt"
MASTER = "rackspacev2-salt-arch201208-a"

PROVIDER_MODULE = "bootmachine.contrib.providers.rackspace_openstack_v2"
SERVERS = [
    {"servername": "rackspacev2-salt-arch201208-a",
     "roles": ["salt-master"],
     "flavor": "2",
     "image": "Arch 2012.08",
     "distro_module": "bootmachine.contrib.distros.rackspace_arch_201208"},
    {"servername": "rackspacev2-salt-arch201208-b",
     "roles": ["test-additional-minions"],
     "flavor": "2",
     "image": "Arch 2012.08",
     "distro_module": "bootmachine.contrib.distros.rackspace_arch_201208"},
]

SSH_PUBLIC_KEY = os.path.join(os.environ["HOME"], ".ssh", "id_ecdsa.pub")
enc, keyhash = open(SSH_PUBLIC_KEY).read().split(" ")[:2]
if "==" in keyhash:
    keyhash = keyhash.split("==")[0]
SSH_USERS = [
    {"fullname": "bootmachine",
     "username": os.environ["USER"],
     "uid": "1000",
     "gid": "1000",
     "extra_groups": ["sshers", "wheel", "ops"],
     "ssh_keys": [{
         "hash": keyhash,
         "enc": enc,
         "comment": "bootmachine.key",
     }]},
]
