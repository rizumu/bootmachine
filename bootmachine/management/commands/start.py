import os
import shutil
from distutils.dir_util import copy_tree

import bootmachine

from bootmachine.management.base import BaseCommand, CommandError


BOOTMACHINE_DIR = os.path.dirname(bootmachine.__file__)
BOOTMACHINE_FABFILE = os.path.join(BOOTMACHINE_DIR, "fabfile_dist.py")
BOOTMACHINE_SETTINGS = os.path.join(BOOTMACHINE_DIR, "settings_dist.py")
CONFIGURATION_DIR = os.path.join(BOOTMACHINE_DIR, "configuration/")


class Command(BaseCommand):

    help = "Creates a new bootmachine installation in the current working directory."

    def handle(self, *args, **options):
        if os.path.exists("fabfile.py"):
            raise CommandError("`fabfile.py` already exists")
        if os.path.exists("settings.py"):
            raise CommandError("`settings.py` already exists")
        shutil.copyfile(BOOTMACHINE_FABFILE, os.path.join(os.getcwd(), "fabfile.py"))
        shutil.copyfile(BOOTMACHINE_SETTINGS, os.path.join(os.getcwd(), "settings.py"))
        copy_tree(CONFIGURATION_DIR, os.path.join(os.getcwd(), "configuration/"))
        print("""The bootmachine was sucessfully setup.
    1. Customize the ``settings.py`` to your desired stack.
    2. Type ``fab -l`` for the list of available bootmachine comamnds.""")
