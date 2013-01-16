"""
BOOTMACHINE: A-Z transmutation of aluminium into rhodium.
"""
from bootmachine.core import *  # noqa

# an example of how to import custom fabric commands from
# a file named ``fabfile_local.py``
try:
    from fabfile_local import *  # noqa
except ImportError:
    pass
