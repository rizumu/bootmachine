/etc/pacman.conf:
  file.managed:
    - source: salt://pacman/pacman.conf.j2
    - order: 1
    - mode: 644
    - template: jinja
    - context:
        extra_repos: {{ pillar.pacman_extra_repos or [] }}
