include:
  - kernel.lts

/etc/mkinitcpio.conf:
  file.managed:
    - source: salt://xen/kernel/mkinitcpio.xen.conf
    - require:
      - pkg: kernel-lts

mkinitcpio:
  cmd.wait:
    - name: mkinitcpio -p linux-lts
    - watch:
      - file: /etc/mkinitcpio.conf
