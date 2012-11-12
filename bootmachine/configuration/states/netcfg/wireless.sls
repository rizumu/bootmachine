include:
  - netcfg

netcfg-wireless-deps:
  pkg.installed:
    - names:
      - wireless_tools
      - wpa_supplicant

{% for name args in pillar['netcfg_wireless_profiles'].iteritems() %}
/etc/network.d/{{ name }}:
  file.managed:
    - source: salt://netcfg/wireless_profile.j2
    - template: jinja
    - defaults:
        name: {{ name }}
        security: {{ args['security'] }}
        essid: {{ args['essid'] }}
        key: {{ args['key'] }}
        key_mgmt: {{ args['key_mgmt'] }}
        eap: {{ args['eap'] }}
        identity: {{ args['identity'] }}
        password: {{ args['password'] }}
{% endfor %}
