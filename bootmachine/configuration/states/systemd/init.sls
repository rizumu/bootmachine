systemdpkgs:
  pkg.installed:
    - names:
      - systemd
      - systemd-sysvcompat

/etc/systemd/system/default.target:
  file.symlink:
    - target: /usr/lib/systemd/system/multi-user.target

/etc/hostname:
  file.managed:
    - source: salt://systemd/hostname.j2
    - template: jinja

/etc/hosts:
  file.managed:
    - source: salt://systemd/hosts.j2
    - template: jinja
    - defaults:
        hostname: {{ grains['host'] }}
        fqdn: {{ grains['fqdn'] }}

/etc/vconsole.conf:
  file.managed:
    - source: salt://systemd/vconsole.conf.j2
    - template: jinja
    - defaults:
        keymap: us

/etc/timezone:
  file.managed:
    - source: salt://systemd/timezone.j2
    - template: jinja
    - defaults:
        timezone: 'Etc/UTC'

/etc/localtime:
  file.symlink:
    - target: /usr/share/zoneinfo/US/Central

/etc/locale.conf:
  file.managed:
    - source: salt://systemd/locale.conf.j2
    - template: jinja
    - defaults:
        locale: 'en_US.UTF-8'

/etc/locale.gen:
  file.managed:
    - source: salt://systemd/locale.gen.j2
    - template: jinja
    - defaults:
        locales:
          - 'en_US.UTF-8 UTF-8'

locale-gen:
  cmd.wait:
    - watch:
      - file: /etc/locale.gen

/var/log/journal:
  file.directory

/etc/systemd/journald.conf:
  file.managed:
    - source: salt://systemd/journald.conf

/etc/systemd/logind.conf:
  file.managed:
    - source: salt://systemd/logind.conf
