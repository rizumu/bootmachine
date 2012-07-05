Bootmachine 0.5.0 release notes

The bootmachine grew out of the desire to automate the launching,
configuration, and scaling of a stack of servers in the cloud.

The provider, configurator, and distro functionality has been written
in such a way that each module is pluggable. Therefore customization
and extension can be achieved with little effort.

The bootmachine has existing modules for Rackspace, Salt and a handful
of distros. Additional modules could easily be written to support EC2, Chef,
Puppet, and other distros.

Any contributions to the core or submissions of new modules for the
contrib will be much appreciated. I'd like to see this project allow
developers to switch between providers with ease, simplify the process
of configuring a cloud stack, and encourage experimentation with new
distros.

This is not a 1.0 yet, but please give it a try. It has been working
well for me and I'm excited about this first public release.

Github page: https://github.com/rizumu/bootmachine
