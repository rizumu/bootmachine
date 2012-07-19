/etc/rc.conf:
  file.managed:
    - source: salt://rc/rc.conf.j2
    - template: jinja
    - defaults:
        timezone: 'Etc/UTC'
        locale: 'en_US.UTF-8'
        hostname: 'localhost'
        daemons:
          - syslog-ng
          - iptables
          - network
          - sshd
          - ntpd
          - crond
{% if pillar['daemons'] %}
    - context:
        daemons:
{% for daemon in pillar['daemons'] %}
          - '{{ daemon }}'
{% endfor %}
{% endif %}

/etc/locale.gen:
  file.managed:
    - source: salt://rc/locale.gen.j2
    - template: jinja
    - defaults:
        locales:
          - 'en_US.UTF-8 UTF-8'

locale-gen:
  cmd.wait:
    - watch:
      - file: /etc/locale.gen
