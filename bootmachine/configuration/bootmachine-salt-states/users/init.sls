{% if grains['os'] == 'Arch' %}
aur:
  user.present:
    - uid: 902
    - gid: 902
    - groups:
      - aur
      - wheel
    - require:
      - group: aur
{% endif %}

{% for user, args in pillar['users'].iteritems() %}
{{ user }}:
  user.present:
    - fullname: {{ args['fullname'] }}
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

{% if 'ssh_auth' in args %}
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
{% endif %}
{% endfor %}
