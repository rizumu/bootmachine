netcfg:
  pkg:
    - installed
  file.managed:
    - name: /etc/conf.d/netcfg
    - source: salt://netcfg/netcfg.conf.j2
    - template: jinja
  service.running:
    - enable: True
    - provider: systemd
    - require:
      - file: netcfg
      # - file: netcfg-service-override

# netcfg-service-override:
#   file.managed:
#     - name: /etc/systemd/system/netcfg.service
#     - source: salt://netcfg/netcfg.service.j2
#     - template: jinja
