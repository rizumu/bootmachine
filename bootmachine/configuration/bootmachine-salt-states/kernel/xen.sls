include:
  - kernel

/etc/mkinitcpio.conf:
  file.managed:
    - source: salt://kernel/mkinitcpio.xen.conf
    - require:
      - pkg: kernel

mkinitcpio:
  cmd.wait:
    - name: mkinitcpio -p linux-lts
    - watch:
      - file: /etc/mkinitcpio.conf
