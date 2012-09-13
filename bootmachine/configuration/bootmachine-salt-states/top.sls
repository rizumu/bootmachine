# Set the saltmaster ip address in `ssh/init.sls`

base:
  '*':
    - edit.vim
    - edit.emacs-nox
    - edit.zile
    - groups
    - hosts
    - iptables
    - salt
    - ssh
    - sudo
    - swap
    - users
    - xcbc
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
    - rc
