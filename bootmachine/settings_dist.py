import os


"""
CONFIGURATION MANAGEMENT
"""

# bootmachine does not allow using multiple configuration management tools.
# choose one, and only one, configurator module.
CONFIGURATOR_MODULE = "bootmachine.contrib.configurators.salt"

# the servername of your saltmaster, chefmaster, puppetmaster
MASTER = "loadbalancer"

# salt
SALTSTATES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              "configuration", "bootmachine-salt-states/")
PILLAR_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                          "configuration", "bootmachine-pillar/")
SALT_INSTALLER_ARCH_201110 = "aur"
SALT_INSTALLER_ARCH_201208 = "aur"
SALT_INSTALLER_DEBIAN_6 = "pip"
SALT_INSTALLER_FEDORA_16 = "rpm-stable"
SALT_INSTALLER_FEDORA_17 = "rpm-stable"
SALT_INSTALLER_UBUNTU_1204LTS = "ppa"

# puppet (not yet implemented)
PUPPET_VERSION = NotImplementedError()
PUPPET_RECIPES_DIR = NotImplementedError()

# chef (not yet implemented)
CHEF_VERSION = NotImplementedError()
CHEF_RECIPIES_DIR = NotImplementedError()

"""
PROVIDERS AND SERVER STACK
"""
# bootmachine does not allow using multiple providers simultaneously.
# choose one, and only one, provider module
PROVIDER_MODULE = "bootmachine.contrib.providers.rackspace_openstack_v1"

# Rackspace authentication via openstack-compute
OPENSTACK_USERNAME = os.environ.get("OPENSTACK_COMPUTE_USERNAME")
OPENSTACK_APIKEY = os.environ.get("OPENSTACK_COMPUTE_APIKEY")

# Rackspace authentication via python-novaclient api v2
OS_USERNAME = os.environ.get("OS_USERNAME")
OS_PASSWORD = os.environ.get("OS_PASSWORD")
OS_TENANT_NAME = os.environ.get("OS_TENANT_NAME")
OS_AUTH_URL = os.environ.get("OS_AUTH_URL")
OS_REGION_NAME = os.environ.get("OS_REGION_NAME")
OS_COMPUTE_API_VERSION = os.environ.get("OS_COMPUTE_API_VERSION")

# Amazon authentication via boto
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

# Your stack: providers and their servers.
# Each server must have a unique servername.
SERVERS = [
    # STACK EXAMPLE
    {"servername": "loadbalancer",
     "roles": ["loadbalancer"],
     "flavor": "1",
     "image": "Arch 2012.08",
     "distro_module": "bootmachine.contrib.distros.rackspace_arch_201208"},
    # {"servername": "application1",
    #  "roles": ["application"],
    #  "flavor": "1",
    #  "image": "Arch 2012.08",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_arch_201208"},
    # {"servername": "database",
    #  "roles": ["database"],
    #  "flavor": "1",
    #  "image": "Arch 2012.08",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_arch_201208"},
    # {"servername": "cache",
    #  "roles": ["cache"],
    #  "flavor": "1",
    #  "image": "Arch 2012.08",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_arch_201208"},
    # WORKING DISTRO EXAMPLES
    # {"servername": "arch",
    #  "roles": [],
    #  "flavor": "1",
    #  "image": "Arch 2012.08",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_arch_201208"},
    # {"servername": "ubuntu",
    #  "roles": [],
    #  "flavor": "1",
    #  "image": "Ubuntu 12.04 LTS",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_ubuntu_1204"},
    # {"servername": "fedora16",
    #  "roles": [],
    #  "flavor": "1",
    #  "image": "Fedora 16",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_fedora_16"},
    # {"servername": "fedora17",
    #  "roles": [],
    #  "flavor": "1",
    #  "image": "Fedora 17",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_fedora_17"},
    # NON-WORKING DISTRO EXAMPLES
    # {"servername": "debian",
    #  "roles": [],
    #  "flavor": "1",
    #  "image": "Debian 6 (Squeeze)",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_debian_6"},
    # {"servername": "gentoo",
    #  "roles": [],
    #  "flavor": "1",
    #  "image": "Gentoo 11.0",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_gentoo_110"},
    # {"servername": "centos",
    #  "roles": [],
    #  "flavor": "1",
    #  "image": "CentOS 6.2",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_centos_62"},
    # {"servername": "rhel",
    #  "roles": [],
    #  "flavor": "1",
    #  "image": "Red Hat Enterprise Linux 6",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_rhel_6"},
    # {"servername": "opensuse",
    #  "roles": [],
    #  "flavor": "1",
    #  "image": "openSUSE 12",
    #  "distro_module": "bootmachine.contrib.distros.rackspace_opensuse_12"},
]

"""
SECURITY
"""

# Change the default SSH port of 22, suggestion is between 20000 and 65535.
SSH_PORT = "30000"

# The local path to your public ssh key.
# This key is used to ssh as root during the bootstrap() stage.
# NOTE: Elliptic curve cryptography support has been excluded from Fedora
# presumably due to patent concerns.
# http://comments.gmane.org/gmane.linux.redhat.fedora.legal/1576
SSH_PUBLIC_KEY = os.path.join(os.environ["HOME"], ".ssh", "id_ecdsa.pub")

# Public key info for users to be granted direct SSH logins.
# Users may have multiple keys.
# do not include comment symbols `==` at the end of the hash
SSH_USERS = [
    {"fullname": "Eric Idle",
     "username": "eidle",
     "uid": "1000",
     "gid": "1000",
     "extra_groups": ["sshers", "wheel", "ops"],
     "ssh_keys": [{
         "hash": "PUT_PUBLICKEYHASH_HERE",
         "enc": "ecdsa-sha2-nistp521",
         "comment": "eric.key",
     }, {
         "hash": "PUT_PUBLICKEYHASH_HERE",
         "enc": "ssh-rsa",
         "comment": "eric.oldkey",
     }]},
    {"fullname": "Graham Chapman",
     "username": "gchapman",
     "extra_groups": ["sshers", "wheel", "ops"],
     "uid": "1001",
     "gid": "1001",
     "ssh_keys": [{
         "hash": "PUT_PUBLICKEYHASH_HERE",
         "enc": "ssh-rsa",
         "comment": "graham.key",
     }]},
    {"fullname": "John Cleese",
     "username": "jcleese",
     "extra_groups": ["sshers", "wheel", "ops"],
     "uid": "1002",
     "gid": "1002",
     "ssh_keys": [{
         "hash": "PUT_PUBLICKEYHASH_HERE",
         "enc": "ssh-rsa",
         "comment": "graham.key",
     }]},
]
