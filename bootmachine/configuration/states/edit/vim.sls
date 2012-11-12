{% if grains['os'] == 'RedHat' or grains['os'] == 'Fedora' %}
vim:
  pkg.installed:
    - name: vim-enhanced
{% endif %}

/etc/vimrc:
  file.managed:
    - source: salt://edit/vimrc
    - user: root
{% if grains['os'] == 'FreeBSD'%}
    - group: wheel
{% else %}
    - group: root
{% endif %}
    - mode: 644
    - makedirs: True
{% if grains['os'] == 'RedHat' or grains['os'] == 'Fedora' %}
    - require:
      - pkg: vim
{% endif %}
