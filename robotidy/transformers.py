import inspect
import sys

from robot.parsing import ModelTransformer

from robotidy.decorators import transformer, configurable


def load_transformers(allowed_transformers):
    """ Dynamically load all classess from this file with attribute `name` defined in allowed_transformers """
    transformer_classes = {}
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for transfomer_class in classes:
        if not allowed_transformers:
            if getattr(transfomer_class[1], 'is_transformer', False):
                transformer_classes[transfomer_class[1].__name__] = transfomer_class[1]()
        elif transfomer_class[1].__name__ in allowed_transformers:
            transformer_classes[transfomer_class[1].__name__] = transfomer_class[1]()
    return transformer_classes


@transformer
class DummyTransformer(ModelTransformer):
    def __init__(self):
        self.some_value = 10

    @configurable
    def some_value(self, value):
        """ configurable property with name `some_value`. Parse and return expected value to save it """
        return int(value) + 1


@transformer
class AnotherTransformer(ModelTransformer):
    def __init__(self):
        self.other_value = 5

    @configurable
    def other_value(self, value):
        """ configurable property with name `other_value`. Parse and return expected value to save it """
        value = value * 10
        return value


class NotATransformer(ModelTransformer):
    pass