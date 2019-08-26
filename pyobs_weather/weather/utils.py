import importlib
import logging

log = logging.getLogger(__name__)


def get_class(class_name):
    # get module and class name
    module = class_name[:class_name.rfind('.')]
    class_name = class_name[class_name.rfind('.') + 1:]

    # import
    return getattr(importlib.import_module(module), class_name)
