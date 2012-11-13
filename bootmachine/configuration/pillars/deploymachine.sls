# Permission of 600 recommended for this file
salt_version: 0.10.4-1

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