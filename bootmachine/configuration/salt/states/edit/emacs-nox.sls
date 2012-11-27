{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
emacs23-nox:
  pkg:
    - installed
{% elif grains['os'] == 'Arch' or grains['os'] == 'Fedora' %}
emacs-nox:
  pkg:
    - installed
{% endif %}
