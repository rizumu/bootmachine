{% if grains['os'] == 'Ubuntu' or grains['os'] == 'Debian' %}
wheel:
  group.present:
    - gid: 902
{% else %}
wheel:
  group.present:
    - gid: 10
{% endif %}

sshers:
  group.present:
    - gid: 900

ops:
  group.present:
    - gid: 901

{% if grains['os'] == 'Arch' %}
aur-group:
  group.present:
    - name: aur
    - gid: 902
{% endif %}

{% for user, args in pillar['users'].iteritems() %}
{{ user }}-group:
  group.present:
    - name: {{ user }}
    - gid: {{ args['gid'] }}
{% endfor %}
