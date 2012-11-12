include:
  - netcfg

{% for name, args in pillar['netcfg_wired_profiles'].iteritems() %}
/etc/network.d/{{ name }}:
  file.managed:
    - source: salt://netcfg/wired_profile.j2
    - template: jinja
    - defaults:
        name: {{ name }}
        interface: {{ args['interface'] }}
        ip_type: {{ args['ip_type'] }}
        addr: {{ args['addr'] }}
        netmask: {{ args['netmask'] }}
        gateway: {% if 'gateway' in args %}{{ args['gateway'] }}{% endif %}
        ip6_type: {% if 'ip6_type' in args %}{{ args['ip6_type'] }}{% endif %}
        addr6: {% if 'addr6' in args %}{{ args['addr6'] }}{% endif %}
        gateway6: {% if 'gateway6' in args %}{{ args['gateway6'] }}{% endif %}
        routes: {% if 'routes' in args %}{{ args['routes'] }}{% endif %}
        dns: {{ args['dns'] }}
{% endfor %}
