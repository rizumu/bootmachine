# Ensure that the salt minion is running and on

{% if grains['os'] == 'Ubuntu' %}
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
        servers: {{ pillar['servers'] }}
        saltmaster_ip: {{ pillar['saltmaster_private_ip'] }}
        hostname: {{ grains["host"] }}

salt-minion-daemon:
  service.running:
    - name: salt-minion
    - enabled: True
    - watch:
      - file: /etc/salt/minion
    - require:
      - file: /etc/salt/minion
{% if grains['os'] == 'Ubuntu' %}
      - pkg: salt-minion
{% else %}
      - pkg: salt
{% endif %}

salt-config-templates:
  file.absent:
    - names:
      - /etc/salt/master.template
      - /etc/salt/minion.template
