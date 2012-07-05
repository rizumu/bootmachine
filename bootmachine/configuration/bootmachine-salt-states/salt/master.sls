# Turn on a salt master

include:
  - salt

{% if grains['os'] == 'Ubuntu' %}
salt-master:
  pkg.installed
{% endif %}

/etc/salt/master:
  file.managed:
    - mode: 640
    - source: salt://salt/master.config
    - require:
{% if grains['os'] == 'Ubuntu' %}
      - pkg: salt-master
{% else %}
      - pkg: salt
{% endif %}

salt-master-daemon:
  service.running:
    - name: salt-master
    - enabled: True
    - watch:
      - file: /etc/salt/master
{% if grains['os'] == 'Ubuntu' %}
      - pkg: salt-master
{% else %}
      - pkg: salt
{% endif %}
    - require:
      - file: /etc/salt/master
{% if grains['os'] == 'Ubuntu' %}
      - pkg: salt-master
{% else %}
      - pkg: salt
{% endif %}
