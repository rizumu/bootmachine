iptables-rules:
  file.managed:
{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
    - name: /etc/iptables.up.rules
{% elif grains['os'] == 'Arch' or grains['os'] == 'Fedora' %}
    - name: /etc/iptables/iptables.rules
{% endif %}
    - user: root
    - group: root
    - mode: 644
    - makedirs: True
    - source: salt://iptables/rules.j2
    - template: jinja
    - defaults:
        ssh_port: 22
    - context:
        ssh_port: {{ pillar['ssh_port'] }}
        saltminion_private_ips: {{ pillar['saltminion_private_ips'] }}
    - require:
{% for user in pillar['users'] %}
      - user: {{ user }}
{% endfor %}
{% if grains['os'] == 'Arch' or grains['os'] == 'Fedora' %}
      - pkg: iptables
{% endif %}

{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
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
      - file: /etc/iptables/iptables.rules

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
