import importlib
import inspect
import pkgutil

import pytest

import openfga_sdk.models

from openfga_sdk.configuration import Configuration


def _generated_model_classes():
    classes = []
    for module_info in pkgutil.iter_modules(openfga_sdk.models.__path__):
        if module_info.name.startswith("_"):
            continue

        module = importlib.import_module(f"openfga_sdk.models.{module_info.name}")
        classes.extend(
            model_class
            for _, model_class in inspect.getmembers(module, inspect.isclass)
            if model_class.__module__ == module.__name__
            and hasattr(model_class, "openapi_types")
        )

    return sorted(classes, key=lambda model_class: model_class.__name__)


GENERATED_MODEL_CLASSES = _generated_model_classes()


def _sample_value(openapi_type):
    if openapi_type.startswith("list["):
        return ["sample"]
    if openapi_type.startswith("dict["):
        return {"key": "sample"}
    if openapi_type == "bool":
        return True
    if openapi_type in ("int", "float"):
        return 1
    return "sample"


def _different_value(value):
    if isinstance(value, list):
        return [*value, "different"]
    if isinstance(value, dict):
        return {**value, "different": "value"}
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value + 1
    return "different"


@pytest.mark.parametrize(
    "model_class",
    GENERATED_MODEL_CLASSES,
    ids=lambda model_class: model_class.__name__,
)
def test_generated_model_common_contract(model_class):
    configuration = Configuration(api_url="http://api.fga.example")
    configuration.client_side_validation = False
    instance = model_class(local_vars_configuration=configuration)
    equal_instance = model_class(local_vars_configuration=configuration)
    expected = {}

    for attribute, openapi_type in model_class.openapi_types.items():
        value = _sample_value(openapi_type)
        setattr(instance, attribute, value)
        setattr(equal_instance, attribute, value)
        expected[attribute] = value

    assert instance.to_dict() == expected
    assert instance.to_dict(serialize=True) == {
        model_class.attribute_map.get(attribute, attribute): value
        for attribute, value in expected.items()
    }
    assert instance.to_str() == repr(instance)
    assert instance == equal_instance
    assert not instance != equal_instance
    assert instance != object()
    assert not instance == object()

    first_attribute = next(iter(model_class.openapi_types), None)
    if first_attribute is None:
        return

    setattr(
        equal_instance,
        first_attribute,
        _different_value(getattr(equal_instance, first_attribute)),
    )
    assert instance != equal_instance
    assert not instance == equal_instance
