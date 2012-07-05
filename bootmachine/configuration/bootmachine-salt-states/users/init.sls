include:
  - iptables
  - groups

{% if grains['os'] == 'Arch' %}
aur:
  user.present:
    - uid: 902
    - gid: 902
    - groups:
      - aur
    - require:
      - group: aur
{% endif %}

{% for user, args in pillar['users'].iteritems() %}
{{ user }}:
  user.present:
    - fullname: {{ args['fullname'] }}
    - home: /home/{{ user }}
    - shell: /bin/bash
    - uid: {{ args['uid'] }}
    - gid: {{ args['gid'] }}
    - require:
      - group: {{ args['group'] }}
{% for group in args['extra_groups'] %}
      - group: {{ group }}
{% endfor %}
    - groups:
      - {{ args['group'] }}
{% for group in args['extra_groups'] %}
      - {{ group }}
{% endfor %}
{% if 'password' in args %}
    - password: {{ args['password'] }}
{% else %}
    - password: '!'
{% endif %}

/home/{{ user }}:
  file.directory:
    - user: {{ user }}
    - group: {{ args['group'] }}

{% if 'ssh_auth' in args %}
/home/{{ user }}/.ssh:
  file.directory:
    - user: {{ user }}
    - group: {{ args['group'] }}
    - mode: 700
    - require:
      - user: {{ user }}
      - group: {{ args['group'] }}
      - file: /home/{{ user }}

/home/{{ user }}/.ssh/authorized_keys:
  file.managed:
    - user: {{ user }}
    - group: {{ args['group'] }}
    - mode: 600
    - require:
      - user: {{ user }}
      - group: {{ args['group'] }}
      - file: /home/{{ user }}
      - file: /home/{{ user }}/.ssh

{{ user }}-sshkeys:
  ssh_auth:
    - present
    - user: {{ user }}
    - names:
{% for key in args['ssh_auth']['keys'] %}
      - {{ key }}
{% endfor %}
    - require:
      - user: {{ user }}
      - group: {{ args['group'] }}
      - file: /home/{{ user }}
      - file: /home/{{ user }}/.ssh
      - file: /home/{{ user }}/.ssh/authorized_keys
{% endif %}
{% endfor %}
