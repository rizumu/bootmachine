/etc/pacman.d/mirrorlist:
  file.managed:
    - source: salt://pacman/mirrorlist.uk
