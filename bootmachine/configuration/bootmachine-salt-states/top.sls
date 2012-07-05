# Set the saltmaster ip address in `ssh/init.sls`

base:
  '*':
    - core
    - users
    - groups
  '^{{ pillar['saltmaster_hostname'] }}':
    - match: pcre
    - salt.master
    - salt.dirs
  'os:Arch':
    - match: grain
    - grub
    - kernel.xen
    - pacman
    - pacman.usa
