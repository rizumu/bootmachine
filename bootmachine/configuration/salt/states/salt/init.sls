# Ensure that the salt minion is running and on

{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
salt-minion:
  pkg.installed
{% elif grains['os'] == 'Arch' %}
su - aur -c 'yaourt --noconfirm -S salt':
  cmd.run:
    - user: root
    - unless: yaourt -Q salt | grep '{{ pillar['aur_salt_pkgver'] }}'
    - onlyif: curl -s https://aur.archlinux.org/packages/sa/salt/PKGBUILD | grep -A 1 'pkgver={{ pillar['aur_salt_pkgver'] }}' | grep 'pkgrel={{ pillar['aur_salt_pkgrel'] }}'
    - cwd: /home/aur/
    - require:
      - user: aur
{% elif grains['os'] == 'Fedora' %}
salt:
  pkg.installed
{% endif %}

/etc/salt/minion:
  file.managed:
    - mode: 640
    - source: salt://salt/minion.config.j2
    - template: jinja
    - context:
        id: {{ grains['id'] }}
        servers: {{ pillar['servers'] }}
        saltmaster_private_ip: {{ pillar['saltmaster_private_ip'] }}

salt-minion-daemon:
  service.running:
    - name: salt-minion
    - enabled: True
{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
    - watch:
      - file: /etc/salt/minion
      - pkg: salt-minion
    - require:
      - file: /etc/salt/minion
      - pkg: salt-minion
{% elif grains['os'] == 'Arch' %}
    - watch:
      - file: /etc/salt/minion
    - require:
      - file: /etc/salt/minion
{% elif grains['os'] == 'Fedora' %}
    - watch:
      - file: /etc/salt/minion
      - pkg: salt
    - require:
      - file: /etc/salt/minion
      - pkg: salt
{% endif %}

salt-config-templates:
  file.absent:
    - names:
      - /etc/salt/master.template
      - /etc/salt/minion.template

ect-hosts:
  host.present:
    - ip: {{ pillar['saltmaster_private_ip'] }}
    - names:
      - salt-master
