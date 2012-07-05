# TODO
# http://www.ml.reddit.com/r/archlinux/comments/s38q1/having_some_issues_with_logging_iptables/
# In addition, you should add the iptables daemon to start on boot to your rc.conf
#    DAEMONS=(... iptables network ...)

include:
  - ssh

{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
/etc/iptables.up.rules:
  file.managed:
    - user: root
    - group: root
    - mode: 644
    - makedirs: True
    - source: salt://iptables/rules.j2
    - template: jinja
    - defaults:
        ssh_port: 22
{% if pillar['ssh_port'] %}
    - context:
        ssh_port: {{ pillar['ssh_port'] }}
        saltminion_private_ips: {{ pillar['saltminion_private_ips'] }}
{% endif %}

/etc/network/if-pre-up.d/iptables:
  file.managed:
    - source: salt://iptables/iptables
    - user: root
    - group: root
    - mode: 744
    - makedirs: True
  cmd:
    - run
    - require:
      - file: /etc/network/if-pre-up.d/iptables
      - file: /etc/iptables.up.rules

{% elif grains['os'] == 'Arch' or grains['os'] == 'Fedora' %}
iptables:
  pkg:
    - installed
  service.running:
    - enabled: True
    - require:
      - pkg: iptables

/etc/iptables/iptables.rules:
  file.managed:
    - source: salt://iptables/rules.j2
    - template: jinja
    - user: root
    - group: root
    - mode: 644
    - makedirs: True
    - require:
      - pkg: iptables
    - defaults:
        ssh_port: 22
{% if pillar['ssh_port'] %}
    - context:
        ssh_port: {{ pillar['ssh_port'] }}
        saltminion_private_ips: {{ pillar['saltminion_private_ips'] }}
{% endif %}

iptables-restore < /etc/iptables/iptables.rules:
  cmd.wait:
    - watch:
      - file: /etc/iptables/iptables.rules
{% endif %}

{% if grains['os'] == 'Fedora' %}
iptables-save > /etc/sysconfig/iptables:
  cmd.wait:
    - watch:
      - file: /etc/iptables/iptables.rules
{% endif %}
