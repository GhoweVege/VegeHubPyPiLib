"""Tests for helpers.py."""

import pytest
from vegehub.helpers import vh400_transform, therm200_transform  


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (0.005, 0.0),  # Below noise threshold
        (0.011, 0.09999),  # Just above the noise threshold
        (1, 9.09090909091),  # Within the first segment
        (1.1, 10.0),  # First segment boundary
        (1.2, 12.5),  # Within the second segment
        (1.3, 15.0),  # Second segment boundary
        (1.5, 24.615),  # Within the third segment
        (1.82, 40.0),  # Third segment boundary
        (2, 44.736),  # Within the fourth segment
        (2.2, 50.0),  # Fourth segment boundary
        (2.6, 75.0),  # Within the fifth segment
        (3, 100.0),  # Fifth segment boundary
        (3.5, 100.0),  # Beyond the last segment
        ("1.5", 24.615),  # String input, valid conversion
        ("invalid", None),  # Invalid string input
        (None, None),  # None input
        ([], None),  # Invalid type (list)
    ],
)
def test_vh400_transform(input_value, expected_output):
    """Test for basic values."""
    result = vh400_transform(input_value)
    assert pytest.approx(result, rel=1e-4) == expected_output


def test_vh400_transform_large_input():
    """Test values significantly larger than 3.0."""
    assert vh400_transform(10) == 100.0


def test_vh400_transform_negative_input():
    """Test negative input, which should result in 0.0."""
    assert vh400_transform(-1) == 0.0



@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (0, -40.0),              # Zero voltage
        (1, 1.6700),             # Integer input
        (2, 43.3400),            # Integer input
        (0.5, -19.165),          # Float input
        ("0.5", -19.165),        # String representation of a float
        ("2", 43.3400),          # String representation of an integer
        ("invalid", None),       # Invalid string input
        (None, None),            # None input
        ([], None),              # Invalid type (list)
        (True, 1.6700),          # Boolean input (interpreted as int)
        (-1, -81.6700),          # Negative input
        (1000, 41630.0),         # Large value input
    ],
)
def test_therm200_transform(input_value, expected_output):
    """Test basic input values."""
    result = therm200_transform(input_value)
    if expected_output is None:
        assert result is None
    else:
        assert pytest.approx(result, rel=1e-4) == expected_output


def test_therm200_transform_large_negative_input():
    """Test very large negative inputs."""
    assert therm200_transform(-1000) == -41710.0


def test_therm200_transform_non_numeric_types():
    """Test non-numeric inputs explicitly."""
    assert therm200_transform({"key": "value"}) is None
    assert therm200_transform([1, 2, 3]) is None
    assert therm200_transform((1, 2)) is None


def test_therm200_transform_extreme_floats():
    """Test extreme float values."""
    assert pytest.approx(therm200_transform(1e-10), rel=1e-4) == -40.0
    assert pytest.approx(therm200_transform(1e10), rel=1e1) == 416699999.960
