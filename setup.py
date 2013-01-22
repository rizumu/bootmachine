import os
import re
import sys
from fnmatch import fnmatchcase
from distutils.util import convert_path
from setuptools import setup, find_packages


def read(*parts):
    return open(os.path.join(os.path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ("*.py", "*.pyc", "*$py.class", "*~", ".*", "*.bak")
standard_exclude_directories = (".*", "CVS", "_darcs", "./build",
                                "./dist", "EGG-INFO", "*.egg-info")


# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Note: you may want to copy this into your setup.py file verbatim, as
# you can't import this from another package, when you don't know if
# that package is installed yet.


def find_package_data(
    where=".", package="",
    exclude=standard_exclude,
    exclude_directories=standard_exclude_directories,
    only_in_packages=True,
    show_ignored=False):  # nopep8
    """\
Return a dictionary suitable for use in ``package_data``
in a distutils ``setup.py`` file.

The dictionary looks like::

{"package": [files]}

Where ``files`` is a list of all the files in that package that
don"t match anything in ``exclude``.

If ``only_in_packages`` is true, then top-level directories that
are not packages won't be included (but directories under packages
will).

Directories matching any pattern in ``exclude_directories`` will
be ignored; by default directories with leading ``.``, ``CVS``,
and ``_darcs`` will be ignored.

If ``show_ignored`` is true, then all the files that aren't
included in package data are shown on stderr (for debugging
purposes).

Note patterns use wildcards, or can be exact paths (including
leading ``./``), and all searching is case-insensitive.
"""

    out = {}
    stack = [(convert_path(where), "", package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern) or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if (os.path.isfile(os.path.join(fn, "__init__.py")) and not prefix):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + "." + name
                    stack.append((fn, "", new_package, False))
                else:
                    stack.append((fn, prefix + name + "/", package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern) or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "File %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out

docs_extras = [
    "Sphinx",
    "docutils",
]

testing_extras = [
    "nose",
    "coverage",
]

setup(
    name="bootmachine",
    version=find_version("bootmachine", "__init__.py"),
    url="http://bootmachine.readthedocs.org/",
    license="BSD",
    description="A fabric library to bootstrap servers and configuration management software.",
    long_description=read("README.rst"),
    dependency_links=["http://github.com/rizumu/openstack.compute/tarball/master#egg=openstack.compute-2.0a1"],  # nopep8
    author="Thomas Schreiber",
    author_email="tom@nillab.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-novaclient==2.10.0",
        "Fabric==1.5.2",
        "Jinja2==2.6",
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "bootmachine-admin = bootmachine.management:execute_from_command_line",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    setup_requires=[
        "flake8",
    ],
    extras_require={
        "testing": testing_extras,
        "docs": docs_extras,
    },
)
