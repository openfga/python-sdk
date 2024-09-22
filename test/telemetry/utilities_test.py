from mock import MagicMock

from openfga_sdk.telemetry.utilities import doesInstanceHaveCallable


def test_instance_has_callable():
    mock_instance = MagicMock(spec_set=["some_callable", "some_attribute"])
    mock_instance.some_callable = lambda: "I am callable"

    assert doesInstanceHaveCallable(mock_instance, "some_callable")

    assert not doesInstanceHaveCallable(mock_instance, "missing_callable")

    mock_instance.some_attribute = "not callable"
    assert not doesInstanceHaveCallable(mock_instance, "some_attribute")
