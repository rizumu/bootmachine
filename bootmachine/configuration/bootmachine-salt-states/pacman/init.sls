/etc/pacman.conf:
  file.managed:
    - mode: 644
    - source: salt://pacman/pacman.conf.j2
    - order: 1
    - template: jinja
    - context:
        extra_repos: {{ pillar.pacman_extra_repos or [] }}

pacman-contrib:
  pkg.installed
