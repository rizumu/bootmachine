grub2-bios:
  pkg.installed:
    - require:
      - cmd: mkinitcpio
