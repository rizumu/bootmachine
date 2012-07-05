saltmaster-public:
  host.present:
    - ip: {{ pillar['saltmaster_public_ip'] }}

saltmaster-private:
  host.present:
    - ip: {{ pillar['saltmaster_private_ip'] }}

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
