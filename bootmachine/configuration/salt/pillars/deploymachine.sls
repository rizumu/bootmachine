# Permission of 600 recommended for this file
aur_salt_pkgver: 0.10.5
aur_salt_pkgrel: 4

# put some custom salt data here

# RC (rackspace)
daemons:
  - 'syslog-ng'
  - '!network'
  - '@net-profiles'
  - 'netfs'
  - 'ntpd'
  - 'crond'
  - 'sshd'
  - 'iptables'
  - 'xe-linux-distribution'
  - 'nova-agent'
