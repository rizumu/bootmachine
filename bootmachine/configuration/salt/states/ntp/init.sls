ntp:
  pkg.installed

ntpd:
  service.running:
    - enable: True
    - require:
      - pkg: ntp
