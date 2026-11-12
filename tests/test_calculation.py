# tests/test_calculation.py

"""
Unit tests for the calculator_calculations module using pytest.

This test suite covers both positive and negative scenarios for the Calculation
classes and the CalculationFactory. It ensures that calculations execute correctly,
the factory creates appropriate instances, and error handling behaves as expected.

Tests are organized following the AAA (Arrange, Act, Assert) pattern and adhere
to PEP8 standards for code style and formatting.
"""

import pytest
from unittest.mock import patch
from app.operations import Division, Operations, Power, Root
from app.calculation import Calculation
from app.exceptions import OperationError, ValidationError
from app.operations import OperationFactory
from decimal import Decimal, InvalidOperation
from datetime import datetime
import logging

def test_addition():
    calc = Calculation(operation="Addition", 
    operand1=Decimal("2"), 
    operand2=Decimal("3"), 
    result=Decimal("5"))
    assert calc.result == Decimal("5")

def test_subtraction():
    calc = Calculation(operation="Subtraction", 
    operand1=Decimal("5"), 
    operand2=Decimal("3"),
    result=Decimal("2"))
    assert calc.result == Decimal("2")

def test_multiplication():
    calc = Calculation(operation="Multiplication", 
    operand1=Decimal("4"), 
    operand2=Decimal("2"),
    result=Decimal("8"))
    assert calc.result == Decimal("8")

def test_division():
    calc = Calculation(operation="Division", 
    operand1=Decimal("8"), 
    operand2=Decimal("2"),
    result=Decimal("4"))
    assert calc.result == Decimal("4")

def test_division_by_zero():
    with pytest.raises(ValidationError, match="Division by zero is not allowed"):
        Division().execute(Decimal("8"), Decimal("0"))

def test_power():
    calc = Calculation(operation="Power", 
    operand1=Decimal("2"), 
    operand2=Decimal("3"),
    result=Decimal("8"))
    assert calc.result == Decimal("8")

def test_negative_power():
    with pytest.raises(ValidationError, match="Negative exponents not supported"):
        Power().execute(Decimal("2"), Decimal("-3"))

def test_root():
    calc = Calculation(operation="Root", 
    operand1=Decimal("16"), 
    operand2=Decimal("2"),
    result=Decimal("4"))
    assert calc.result == Decimal("4")

def test_invalid_root():
    with pytest.raises(ValidationError, match="Cannot calculate root of negative number"):
        Root().execute(Decimal("-16"), Decimal("2"))

def test_unknown_operation():
    with pytest.raises(ValueError, match="Unknown operation"):
        OperationFactory.create_operation("unknown")

def test_to_dict():
    calc = Calculation(operation="Addition", 
    operand1=Decimal("2"), 
    operand2=Decimal("3"),
    result=Decimal("5"))
    result_dict = calc.to_dict()
    assert result_dict == {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": calc.timestamp.isoformat()
    }

def test_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    calc = Calculation.from_dict(data)
    assert calc.operation == "Addition"
    assert calc.operand1 == Decimal("2")
    assert calc.operand2 == Decimal("3")
    assert calc.result == Decimal("5")


def test_invalid_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "invalid",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)

def test_format_result():
    calc = Calculation(operation="Division",
    operand1=Decimal("1"), 
    operand2=Decimal("3"),
    result=Decimal("0.33333333333333333333")
    )
    assert calc.format_result(precision=2) == "0.33"
    assert calc.format_result(precision=10) == "0.3333333333"

def test_equality():
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"), result=Decimal("5"))
    calc2 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"), result=Decimal("5"))
    calc3 = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"), result=Decimal("2"))
    assert calc1 == calc2
    assert calc1 != calc3