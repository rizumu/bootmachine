# Set the saltmaster ip address in `ssh/init.sls`

base:
  '*':
    - edit.vim
    - edit.emacs-nox
    - edit.zile
    - groups
    - iptables
    - salt
    - ssh
    - sudo
    - swap
    - users
  '^{{ pillar['saltmaster_hostname'] }}':
    - match: pcre
    - salt.master
    - salt.dirs
  'os:Arch':
    - match: grain
    - kernel.xen
    - pacman
    - pacman.usa
    - ntp
    - systemd
    - xen
