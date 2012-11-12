ntp:
  pkg.installed

ntpd:
  service.running:
    - enable: True
    - provider: systemd
    - require:
      - pkg: ntp
