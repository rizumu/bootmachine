{% if grains['os'] == 'Debian' or grains['os'] == 'Ubuntu' %}
emacs23-nox:
  pkg:
    - installed
{% else %}
emacs-nox:
  pkg:
    - installed
{% endif %}
