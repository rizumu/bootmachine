include:
  - groups

/srv/salt/:
  file.directory:
    - user: root
    - group: ops
    - mode: 770
    - makedirs: True

/srv/pillar/:
  file.directory:
    - user: root
    - group: ops
    - mode: 770
    - makedirs: True
