===========================
Contributing to Bootmachine
===========================

As an open source project, Bootmachine welcomes contributions.

What to contribute
------------------

* New modules for the contrib

* Code patches

* Documentation improvements

* Bug reports and patch reviews

Python code style
-----------------

Bootmachine adheres to the Pep8 style guide in the majority of cases.

Double quotes are used in Python files and Jinja Templates. Single
quotes are used in sls and yaml files. Except when using the opposite
makes the code easier to read, for example to prevent or reduce the
need to escape characters.

* Python enhancement proposals related to style
  http://www.python.org/dev/peps/pep-0008/
  http://www.python.org/dev/peps/pep-0257/
  http://www.python.org/dev/peps/pep-3101/

* General Python style tips
  http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html
  http://jaynes.colorado.edu/PythonGuidelines.html

* Writing forwards compatible Python
  http://lucumr.pocoo.org/2011/1/22/forwards-compatible-python/

Git commit message style
------------------------

* Writing a good commit message makes it simple for us to identify what
  your commit does from a high-level. We are not too picky, but there
  are some basic guidelines we’d like to ask you to follow::

    Fixed #1 — added some feature

* We ask that you indicate which task you have fixed (if the commit
  fixes it) or if you are working something complex you may want or be
  asked to only commits parts::

    Refs #1 — added part one of feature X

* A critical part is that you keep the first line as short and sweet
  as possible. This line is important because when git shows commits
  and it has limited space or a different formatting option is used
  the first line becomes all someone might see. If you need to explain
  why you made this change or explain something in detail use this
  format::

    Fixed #13 — added time travel

    You need to be driving 88 miles per hour to generate 1.21 gigawatts of
    power to properly use this feature.

* Aim to adhere to the following commit message style:
  https://docs.djangoproject.com/en/dev/internals/contributing/committing-code/

* Keep in mind there are other opinions:
  http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
  http://stackoverflow.com/questions/2290016/git-commit-messages-50-72-formatting
  http://news.ycombinator.com/item?id=1619458
  http://news.ycombinator.com/item?id=2079612

.. NOTE:: Much of this was graciously lifted from the Pinax style guide:
          http://pinax.readthedocs.org/en/latest/development.html#coding-style
