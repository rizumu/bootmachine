import os

from bootmachine.settings_tests import *


CONFIGURATOR_MODULE = "bootmachine.contrib.configurators.salt"
MASTER = "rackspacev2-salt-fedora17-a"
SALTSTATES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              "configuration", "bootmachine-salt-states/")
PILLAR_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                          "configuration", "bootmachine-pillar/")

PROVIDER_MODULE = "bootmachine.contrib.providers.rackspace_openstack_v2"
OPENSTACK_USERNAME = os.environ.get("OPENSTACK_COMPUTE_USERNAME")
OPENSTACK_APIKEY = os.environ.get("OPENSTACK_COMPUTE_APIKEY")
SERVERS = [
    {"servername": "rackspacev2-salt-fedora17-a",
     "roles": ["loadbalancer"],
     "flavor": "2",
     "image": "Fedora 17",
     "distro_module": "bootmachine.contrib.distros.rackspace_fedora_17"},
    {"servername": "rackspacev2-salt-fedora17-b",
     "roles": ["application"],
     "flavor": "2",
     "image": "Fedora 17",
     "distro_module": "bootmachine.contrib.distros.rackspace_fedora_17"},
]

SSH_PUBLIC_KEY = os.path.join(os.environ["HOME"], ".ssh", "id_rsa.pub")
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
