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
    - source: salt://salt/master.config
    - require:
{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
      - pkg: salt-master
{% else %}
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
{% else %}
    - watch:
      - file: /etc/salt/master
      - pkg: salt
    - require:
      - file: /etc/salt/master
      - pkg: salt
{% endif %}

