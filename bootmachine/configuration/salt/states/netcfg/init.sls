netcfg:
  pkg:
    - installed
  file.managed:
    - name: /etc/conf.d/netcfg
    - source: salt://netcfg/netcfg.conf.j2
    - template: jinja
  service.running:
    - enable: True
    - require:
      - file: netcfg
