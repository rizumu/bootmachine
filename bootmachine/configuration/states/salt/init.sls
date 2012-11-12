# Ensure that the salt minion is running and on

{% if grains['os'] == 'Arch' %}
su - aur -c 'yaourt --noconfirm -S salt':
  cmd.run:
    - user: root
    - unless: yaourt -Q salt | grep '{{ pillar['salt_version'] }}'
    - cwd: /tmp/
    - require:
      - user: aur
{% elif grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
salt-minion:
  pkg.installed
{% else %}
salt:
  pkg.installed
{% endif %}

/etc/salt/minion:
  file.managed:
    - mode: 640
    - source: salt://salt/minion.config.j2
    - template: jinja
    - context:
        salt_version: {{ pillar['salt_version'] }}
        servers: {{ pillar['servers'] }}
        saltmaster_private_ip: {{ pillar['saltmaster_private_ip'] }}
        nodename: {{ grains['nodename'] }}

salt-minion-daemon:
  service.running:
    - name: salt-minion
    - enabled: True
    - provider: systemd
    - watch:
      - file: /etc/salt/minion
    - require:
      - file: /etc/salt/minion
{% if grains['os'] == 'Arch' %}
    - watch:
      - file: /etc/salt/minion
    - require:
      - file: /etc/salt/minion
{% elif grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
    - watch:
      - file: /etc/salt/minion
      - pkg: salt-minion
    - require:
      - file: /etc/salt/minion
      - pkg: salt-minion
{% endif %}

salt-config-templates:
  file.absent:
    - names:
      - /etc/salt/master.template
      - /etc/salt/minion.template

salt-master:
  host.present:
    - ip: {{ pillar['saltmaster_private_ip'] }}
