Installation
============

Bootmachine runs locally on OSX or GNU/Linux.

First clone the bootmachine to an easily accessible folder on your
local machine. The recommended place is ``/srv/`` but any
folder in your home directory would work just the same.

If you are unfamiliar with Python's pip or virtualenv packages,
understand them, at least a little, before proceeding::

    * http://pypi.python.org/pypi/virtualenv
    * http://pypi.python.org/pypi/pip

If you don't already have a virtualenv that you would like to use,
first create a new virtualenv for the bootmachine::

    $ cd ~/.virtualenvs/
    $ virtualenv --no-site-packages --distribute bootmachine
    $ source bootmachine/bin/activate

Install the bootmachine::

    $ pip install bootmachine

From within the directory you want the configuration files to be
copied to, execute the following command::

    $ bootmachine-admin start

Now, customize the example settings file and for your stack. A
suggestion is to instead store these private files a private git
repository.

Some info on choosing the type of encryption for your ssh key::

    https://wiki.archlinux.org/index.php/SSH_Keys#Generating_an_SSH_key_pair
    http://pthree.org/2011/02/17/elliptic-curve-cryptography-in-openssh/

.. note::

   Elliptic curve cryptography is excluded from Fedora
   presumably due to patent concerns. Check Fedora 18 once released.
   http://comments.gmane.org/gmane.linux.redhat.fedora.legal/1576

To use Rackspace's openstack api v2 you must also set some environment
variables for your interactive shell. The recommended installation is
to add the following to your ``~/.bashrc``::

    export OS_USERNAME=""  # your rackspace username
    export OS_PASSWORD=""  # your rackspace password
    export OS_TENANT_NAME=""  # your rackspace accountid
    export OS_AUTH_URL="https://identity.api.rackspacecloud.com/v2.0/"
    export OS_REGION_NAME="DFW"
    export OS_COMPUTE_API_VERSION="2"

For Rackspace api v1 (deprecated)::

    export OPENSTACK_COMPUTE_USERNAME=""  # your rackspace username
    export OPENSTACK_COMPUTE_APIKEY=""  # your rackspace apikey


The same is true for the Amazon boto api::

    export AWS_ACCESS_KEY_ID=""  # your amazon access key id
    export AWS_SECRET_ACCESS_KEY=""  # your amazon secret access key
