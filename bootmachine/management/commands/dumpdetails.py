import os
import shutil
import importlib

from optparse import make_option
import bootmachine

from bootmachine.management.base import BaseCommand, CommandError


### DOES NOT WORK ###
### CURRENTLY OUT OF DATE ###

BOOTMACHINE_FABFILE = os.path.join(os.path.dirname(bootmachine.__file__), "fabfile_dist.py")
BOOTMACHINE_SETTINGS = os.path.join(os.path.dirname(bootmachine.__file__), "settings_dist.py")


class Command(BaseCommand):
    option_list = BaseCommand.option_list + [
        make_option("--format", default="json", dest="format",
            help="Specifies the output serialization format for fixtures."),
        make_option("--indent", default=None, dest="indent", type="int",
            help="Specifies the indent level to use when pretty-printing output"),
    ]
    help = "Output the server details as a fixture of the given format."
    args = "[appname appname.ModelName ...]"

    def handle(self, *args, **options):
        format = options.get("format")
        indent = options.get("indent")

        if not os.path.exists("fabfile.py"):
            raise CommandError("`fabfile.py` does not exists in the current directory.")
        if not os.path.exists("bootmachine_settings.py"):
            raise CommandError("`bootmachine_settings.py` does not exists in the current directory.")

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        serializers = Serializers()
        if format not in serializers.get_public_serializer_formats():
            raise CommandError("Unknown serialization format: %s" % format)

        # try:
        #     serializers.get_serializer(format)
        # except KeyError:
        #     raise CommandError("Unknown serialization format: %s" % format)

        # # Now collate the objects to be serialized.
        # objects = []
        # for model in sort_dependencies(app_list.items()):
        #     if model in excluded_models:
        #         continue
        #     if not model._meta.proxy and router.allow_syncdb(using, model):
        #         if use_base_manager:
        #             objects.extend(model._base_manager.using(using).all())
        #         else:
        #             objects.extend(model._default_manager.using(using).all())

        # try:
        #     return serializers.serialize(format, objects, indent=indent,
        #                 use_natural_keys=use_natural_keys)
        # except Exception, e:
        #     if show_traceback:
        #         raise
        #     raise CommandError("Unable to serialize database: %s" % e)

# Built-in serializers
BUILTIN_SERIALIZERS = {
    "xml" : "django.core.serializers.xml_serializer",
    "python" : "django.core.serializers.python",
    "json" : "django.core.serializers.json",
}

# Check for PyYaml and register the serializer if it's available.
try:
    import yaml
    BUILTIN_SERIALIZERS["yaml"] = "django.core.serializers.pyyaml"
except ImportError:
    pass

_serializers = {}


class Serializers(object):
    def serialize(self, format, queryset, **options):
        """
        Serialize a queryset (or any iterator that returns database objects) using
        a certain serializer.
        """
        s = get_serializer(format)()
        s.serialize(queryset, **options)
        return s.getvalue()

    def get_public_serializer_formats(self):
        if not _serializers:
            self._load_serializers()
        return [k for k, v in _serializers.iteritems() if not v.Serializer.internal_use_only]

    def _load_serializers(self):
        """
        Register built-in and settings-defined serializers. This is done lazily so
        that user code has a chance to (e.g.) set up custom settings without
        needing to be careful of import order.
        """
        global _serializers
        serializers = {}
        for format in BUILTIN_SERIALIZERS:
            self.register_serializer(format, BUILTIN_SERIALIZERS[format], serializers)
        if hasattr(settings, "SERIALIZATION_MODULES"):
            for format in settings.SERIALIZATION_MODULES:
                self.register_serializer(format, settings.SERIALIZATION_MODULES[format], serializers)
        _serializers = serializers

    def register_serializer(self, format, serializer_module, serializers=None):
        """Register a new serializer.

        ``serializer_module`` should be the fully qualified module name
        for the serializer.

        If ``serializers`` is provided, the registration will be added
        to the provided dictionary.

        If ``serializers`` is not provided, the registration will be made
        directly into the global register of serializers. Adding serializers
        directly is not a thread-safe operation.
        """
        if serializers is None and not _serializers:
            _load_serializers()
        module = importlib.import_module(serializer_module)
        if serializers is None:
            _serializers[format] = module
        else:
            serializers[format] = module
