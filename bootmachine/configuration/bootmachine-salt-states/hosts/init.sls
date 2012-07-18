{% for server, args in pillar['servers'].iteritems() %}
{{ server }}-private:
  host:
    - present
    - name: {{ server }}
    - ip: {{ args['private_ip'] }}

{{ server }}-public:
  host:
    - present
    - name: {{ server }}
    - ip: {{ args['public_ip'] }}
{% endfor %}

saltmaster-private:
  host.present:
    - ip: {{ pillar['saltmaster_private_ip'] }}
