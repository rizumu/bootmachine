troubleshooting tips
====================

On rackspace a server can become stuck in the UNKNOWN or ERROR phase
and the bootmachine will be unable to perform most commands. In the
future repairing this may be handled automatically by the bootmachine,
but at this time it is best to manually delete the server. An
alternative to waiting for rackspace to release the server, wait time
can be more than a few hours, is remove the problematic server from
your settings file and add it again. *Make sure to select a different
server name for the replacement.*

