include:
  - groups

{{ pillar['salt_remote_states_dir'] }}:
  file.directory:
    - user: root
    - group: ops
    - mode: 770
    - makedirs: True

{{ pillar['salt_remote_pillars_dir'] }}:
  file.directory:
    - user: root
    - group: ops
    - mode: 770
    - makedirs: True
