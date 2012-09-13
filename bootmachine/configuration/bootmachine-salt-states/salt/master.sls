# Turn on a salt master

include:
  - salt

{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
salt-master:
  pkg.installed
{% endif %}

/etc/salt/master:
  file.managed:
    - mode: 640
    - source: salt://salt/master.config.j2
    - template: jinja
    - context:
        salt_version: {{ pillar['salt_version'] }}
{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
    - require:
      - pkg: salt-master
{% elif grains['os'] == 'Fedora' %}
    - require:
      - pkg: salt
{% endif %}

salt-master-daemon:
  service.running:
    - name: salt-master
    - enabled: True
{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
    - watch:
      - file: /etc/salt/master
      - pkg: salt-master
    - require:
      - file: /etc/salt/master
      - pkg: salt-master
{% elif grains['os'] == 'Fedora' %}
    - watch:
      - file: /etc/salt/master
      - pkg: salt
    - require:
      - file: /etc/salt/master
      - pkg: salt
{% elif grains['os'] == 'Arch' %}
    - watch:
      - file: /etc/salt/master
    - require:
      - file: /etc/salt/master
{% endif %}
