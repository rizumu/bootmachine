# Permission of 600 recommended for this file

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
