# (c) 2008-2011 James Tauber and contributors; written for Pinax (http://pinaxproject.com)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import os
import sys

import bootmachine

BOOTMACHINE_COMMAND_DIR = os.path.join(
    os.path.dirname(bootmachine.__file__), "management", "commands"
)


class CommandNotFound(Exception):
    pass


class CommandLoader(object):

    def __init__(self):
        self.command_dir = BOOTMACHINE_COMMAND_DIR
        self.commands = {}
        self._load_commands()

    def _load_commands(self):
        for f in os.listdir(self.command_dir):
            if not f.startswith("_") and f.endswith(".py"):
                name = f[:-3]
                mod = "bootmachine.management.commands.%s" % name
                try:
                    __import__(mod)
                except:
                    self.commands[name] = sys.exc_info()
                else:
                    mod = sys.modules[mod]
                    self.commands[name] = mod.Command()

    def load(self, name):
        try:
            command = self.commands[name]
        except KeyError:
            raise CommandNotFound("Unable to find command '%s'" % name)
        else:
            if isinstance(command, tuple):
                # an exception occurred when importing the command so let's
                # re-raise it here
                raise(command[0], command[1], command[2])
            return command


class CommandRunner(object):

    usage = "bootmachine-admin command [options] [args]"

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.loader = CommandLoader()
        self.loader.commands["help"] = self.help()

    def help(self):
        loader, usage = self.loader, self.usage
        # use BaseCommand for --version
        from bootmachine.management.base import BaseCommand

        class HelpCommand(BaseCommand):
            def handle(self, *args, **options):
                print("Usage: {}\n".format(usage))
                print("Options:"
                      "  --version   show program's version number and exit\n"
                      "  -h, --help  show this help message and exit\n"
                      "Available commands:\n")
                for command in loader.commands.keys():
                    print(" {}".format(command))
        return HelpCommand()

    def execute(self):
        argv = self.argv[:]
        try:
            command = self.argv[1]
        except IndexError:
            # display help if no arguments were given.
            command = "help"
            argv.extend(["help"])
        # special cases for bootmachine-admin itself
        if command in ["-h", "--help"]:
            argv.pop()
            command = "help"
            argv.extend(["help"])
        if command == "--version":
            argv.pop()
            command = "help"
            argv.extend(["help", "--version"])
        # load command and run it!
        try:
            self.loader.load(command).run_from_argv(argv)
        except CommandNotFound as e:
            sys.stderr.write("{}\n".format(e.args[0]))
            sys.exit(1)


def execute_from_command_line():
    """
    A simple method that runs a ManagementUtility.
    """
    runner = CommandRunner()
    runner.execute()
