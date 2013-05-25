import os


"""
CONFIGURATION MANAGEMENT
"""
# salt
LOCAL_STATES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                "configuration", "salt", "states/")
LOCAL_PILLARS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 "configuration", "salt", "pillars/")
REMOTE_STATES_DIR = "/srv/salt/states/"
REMOTE_PILLARS_DIR = "/srv/salt/pillars/"
SALT_INSTALLER_ARCH_20132 = "aur"
SALT_AUR_PKGVER = "0.15.1"
SALT_AUR_PKGREL = "1"
SALT_INSTALLER_DEBIAN_6 = "backports"
SALT_INSTALLER_DEBIAN_7 = "saltstack"
SALT_INSTALLER_FEDORA_16 = "rpm-stable"
SALT_INSTALLER_FEDORA_17 = "rpm-stable"
SALT_INSTALLER_FEDORA_18 = "rpm-stable"
SALT_INSTALLER_UBUNTU_1204LTS = "ppa"
SALT_INSTALLER_UBUNTU_1210 = "ppa"
SALT_INSTALLER_UBUNTU_1304 = "ppa"

# puppet (not yet implemented)
PUPPET_VERSION = NotImplementedError()
PUPPET_RECIPES_DIR = NotImplementedError()

# chef (not yet implemented)
CHEF_VERSION = NotImplementedError()
CHEF_RECIPIES_DIR = NotImplementedError()


"""
PROVIDERS AND SERVER STACK
"""
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


"""
SECURITY
"""
# Change the default SSH port of 22, suggestion is between 20000 and 65535.
SSH_PORT = "30303"
