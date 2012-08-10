grub-bios:
  pkg.installed:
    - require:
      - cmd: mkinitcpio
