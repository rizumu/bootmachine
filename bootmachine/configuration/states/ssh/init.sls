# PACKAGES

{% if grains['os'] == 'Arch' %}
openssh:
  pkg.installed

net-tools:
  pkg.installed

{% elif grains['os'] == 'Fedora' %}

openssh-clients:
  pkg.installed

openssh-server:
  pkg.installed

{% elif grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}

openssh-client:
  pkg.installed

openssh-server:
  pkg.installed

{% endif %}

# SERVICES

{% if grains['os'] == 'Arch' %}

systemctl restart sshd.service:
  cmd:
    - run
    - unless: "P1=$(netstat -ano --tcp --programs | grep LISTEN | grep sshd | grep -o :[0-9]* | grep -o [0-9]* | head -1); P2=$(cat /etc/ssh/sshd_config | grep Port | grep -o [0-9]*); [[ $P1 == $P2 ]]"
    - require:
      - pkg: net-tools
      - file: /etc/ssh/sshd_config

sshd.socket:
  service.running:
    - enable: True
    - provider: systemd
    - watch:
      - file: /etc/ssh/sshd_config

{% elif grains['os'] == 'Fedora' %}

systemctl restart sshd.service:
  cmd:
    - run
    - unless: "P1=$(netstat -ano --tcp --programs | grep LISTEN | grep sshd | grep -o :[0-9]* | grep -o [0-9]* | head -1); P2=$(cat /etc/ssh/sshd_config | grep Port | grep -o [0-9]*); [[ $P1 == $P2 ]]"
    - require:
      - file: /etc/ssh/sshd_config

sshd:
  service.running:
    - enable: True
    - watch:
      - file: /etc/ssh/sshd_config

{% elif grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}

service ssh restart:
  cmd:
    - run
    - unless: "P1=$(netstat -ano --tcp --programs | grep LISTEN | grep sshd | grep -o :[0-9]* | grep -o [0-9]* | head -1); P2=$(cat /etc/ssh/sshd_config | grep Port | grep -o [0-9]*); [[ $P1 == $P2 ]]"
    - require:
      - file: /etc/ssh/sshd_config

ssh:
  service.running:
    - enable: True
    - provider: systemd
    - watch:
      - file: /etc/ssh/sshd_config

{% endif %}

# CONFIGURATION

/etc/ssh/sshd_config:
  file.managed:
    - user: root
    - group: root
    - mode: 644
    - source: salt://ssh/sshd_config.j2
    - template: jinja
    - defaults:
        ssh_port: 22
    - context:
        ssh_port: {{ pillar['ssh_port'] }}
        ssh_users: {{ pillar['users'] }}
    - require:
{% for user in pillar['users'] %}
      - ssh_auth: {{ user }}-sshkeys
{% endfor %}
