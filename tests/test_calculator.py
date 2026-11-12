# """ tests/test_calculator.py """
import sys
# import pytest
from io import StringIO
# from app.calculator import display_help, display_history, calculator

from colorama import Fore, Back, Style
import re
import datetime
from pathlib import Path
import pandas as pd
import pytest
from colorama import Fore, Back, Style
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory, Operations
from app.logger import Logger
from app.calculator_repl import calculator_repl

@pytest.fixture
def isolated_calculator(tmp_path, monkeypatch):
    monkeypatch.delenv("CALCULATOR_HISTORY_FILE", raising=False)
    monkeypatch.delenv("CALCULATOR_HISTORY_DIR", raising=False)
    monkeypatch.delenv("CALCULATOR_BASE_DIR", raising=False)

    config = CalculatorConfig(
        base_dir=tmp_path,
        max_history_size=3
    )

    return Calculator(config)

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator_instance():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator_instance):
    assert calculator_instance.history == []
    assert calculator_instance.undo_stack == []
    assert calculator_instance.redo_stack == []
    assert calculator_instance.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# Test Adding and Removing Observers

def test_add_observer(calculator_instance):
    logger = Mock(spec=Logger)
    observer = LoggingObserver(logger)
    calculator_instance.add_observer(observer)
    assert observer in calculator_instance.observers

def test_remove_observer(calculator_instance):
    logger = Mock(spec=Logger)
    observer = LoggingObserver(logger)
    calculator_instance.add_observer(observer)
    calculator_instance.remove_observer(observer)
    assert observer not in calculator_instance.observers

# Test Setting Operations

def test_set_operation(calculator_instance):
    operation = OperationFactory.create_operation('add')
    calculator_instance.set_operation(operation)
    assert calculator_instance.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator_instance):
    operation = OperationFactory.create_operation('add')
    calculator_instance.set_operation(operation)
    result = calculator_instance.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator_instance: Calculator):
    calculator_instance.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator_instance.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator_instance: Calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator_instance.perform_operation(2, 3)

def test_incorrect_command(monkeypatch, capsys):
        inputs = iter(["add", "2", "3", "cancel", "exit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        calc = Calculator()
        calculator_repl(calc)
        captured = capsys.readouterr()
        assert "Unknown command: 'cancel'. Type 'help' for available commands." in captured.out

def test_exit(monkeypatch, capsys):
    inputs = iter(["help", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    calc = Calculator()
    calculator_repl(calc)

    captured = capsys.readouterr()

    assert "Goodbye!" in captured.out
    assert "History saved successfully" in captured.out

# Test Undo/Redo Functionality

def test_redo_success(monkeypatch, capsys):
    inputs = iter([
        "add",
        "2",
        "3",
        "undo",
        "redo",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Operation undone" in captured.out
    assert "Operation redone" in captured.out

@patch("app.calculator_repl.Calculator")
def test_redo_command_success(mock_calculator, capsys):
    """Test the redo command when redo succeeds."""
    calculator_instance = mock_calculator.return_value
    calculator_instance.redo.return_value = True
    with patch("builtins.input", side_effect=["redo", "exit"]):
        calc = mock_calculator()
        calculator_repl(calc)
    calculator_instance.redo.assert_called_once_with()
    captured = capsys.readouterr()
    assert "Operation redone" in captured.out
    assert "Goodbye!" in captured.out

@patch("app.calculator.Calculator")
def test_redo_command_nothing_to_redo(mock_calculator, capsys):
    """Test the redo command when there is nothing to redo."""
    calculator_instance = mock_calculator.return_value
    calculator_instance.redo.return_value = False
    with patch("builtins.input", side_effect=["redo", "exit"]):
        calc = mock_calculator()
        calculator_repl(calc)
    calculator_instance.redo.assert_called_once_with()
    captured = capsys.readouterr()
    assert "Nothing to redo" in captured.out
    assert "Goodbye!" in captured.out

def test_redo(calculator_instance: Calculator):
    operation = OperationFactory.create_operation('add')
    calculator_instance.set_operation(operation)
    calculator_instance.perform_operation(2, 3)
    calculator_instance.undo()
    calculator_instance.redo()
    assert len(calculator_instance.history) == 1

def test_redo_nothing_to_redo(monkeypatch, capsys):
    inputs = iter(["clear",
        "redo",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Nothing to redo" in captured.out

def test_undo(calculator_instance: Calculator):
    operation = OperationFactory.create_operation('add')
    calculator_instance.set_operation(operation)
    calculator_instance.perform_operation(2, 3)
    calculator_instance.undo()
    assert calculator_instance.history == []

def test_undo_operation(monkeypatch, capsys):
    inputs = iter([
        "add",
        "2",
        "3",
        "undo",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Operation undone" in captured.out

def test_undo_nothing_to_undo(monkeypatch, capsys):
    inputs = iter(["clear",
        "undo",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Nothing to undo" in captured.out

@patch("app.calculator_repl.Calculator")
def test_undo_command_success(mock_calculator, capsys):
    """Test the undo command when undo succeeds."""
    calculator_instance = mock_calculator.return_value
    calculator_instance.undo.return_value = True
    with patch("builtins.input", side_effect=["undo", "exit"]):
        calc = mock_calculator()
        calculator_repl(calc)
    calculator_instance.undo.assert_called_once_with()
    captured = capsys.readouterr()
    assert "Operation undone" in captured.out
    assert "Goodbye!" in captured.out

@patch("app.calculator_repl.Calculator")
def test_undo_command_nothing_to_undo(mock_calculator, capsys):
    """Test the undo command when there is nothing to undo."""
    calculator_instance = mock_calculator.return_value
    calculator_instance.undo.return_value = False
    with patch("builtins.input", side_effect=["undo", "exit"]):
        calc = mock_calculator()
        calculator_repl(calc)
    calculator_instance.undo.assert_called_once_with()
    captured = capsys.readouterr()
    assert "Nothing to undo" in captured.out
    assert "Goodbye!" in captured.out

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator_instance):
    operation = OperationFactory.create_operation('add')
    calculator_instance.set_operation(operation)
    calculator_instance.perform_operation(2, 3)
    calculator_instance.save_history()
    mock_to_csv.assert_called_once()

def test_save_message(monkeypatch, capsys):
    inputs = iter(["save", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "History saved successfully." in captured.out

def test_exit_saves_history(monkeypatch, capsys):
    inputs = iter(["exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "History saved successfully." in captured.out
    assert "Goodbye!" in captured.out

def test_save_history_error(monkeypatch, capsys):
    def mock_save_history(self):
        raise Exception("Save failed")
    monkeypatch.setattr(
        "app.calculator.Calculator.save_history",
        mock_save_history
    )
    inputs = iter([
        "save",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Error: Save failed" in captured.out
    assert "Warning: Could not save history: Save failed" in captured.out

def test_save_command_success(monkeypatch, capsys):
    """Test the save command when history saves successfully."""

    inputs = iter(["save", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    calc = Calculator()
    with patch.object(calc, "save_history") as mock_save:
        calculator_repl(calc)

    # Once for save and once for automatic saving on exit
    assert mock_save.call_count == 2

    captured = capsys.readouterr()
    assert "History saved successfully" in captured.out
    assert "Goodbye!" in captured.out

def test_save_command_failure(monkeypatch, capsys):
    """Test the save command when saving history fails."""
    inputs = iter(["save", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    error_message = "Unable to write history file"
    with patch.object(
        calc,
        "save_history",
        side_effect=OperationError(error_message)
    ) as mock_save:
        calculator_repl(calc)
    # save command and exit command both attempt to save
    assert mock_save.call_count == 2
    captured = capsys.readouterr()
    # Check the save command error message
    expected_message = (
        Fore.RED
        + f"Error saving history: {error_message}"
        + Style.RESET_ALL
    )
    assert expected_message in captured.out
    # Check the exit command warning
    assert "Warning: Could not save history" in captured.out
    # Verify the calculator exits
    assert "Goodbye!" in captured.out

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator_instance):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator_instance.load_history()
        # Verify history length after loading
        assert len(calculator_instance.history) == 1
        # Verify the loaded values
        assert calculator_instance.history[0].operation == "Addition"
        assert calculator_instance.history[0].operand1 == Decimal("2")
        assert calculator_instance.history[0].operand2 == Decimal("3")
        assert calculator_instance.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")
        
def test_load_history_success(monkeypatch, capsys):
    inputs = iter(["load", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "History loaded successfully" in captured.out

def test_load_history_error(monkeypatch, capsys):
    def mock_load_history(self):
        raise Exception("Load failed")
    monkeypatch.setattr(
        "app.calculator.Calculator.load_history",
        mock_load_history
    )
    inputs = iter([
        "load",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Error: Load failed" in captured.out

def test_load_command_success(monkeypatch, capsys):
    """Test the load command when loading history succeeds."""
    inputs = iter(["load", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    with patch.object(calc, "load_history", return_value=True) as mock_load:
        calculator_repl(calc)
    # Verify load_history was called once
    mock_load.assert_called_once_with()
    # Verify the success message was printed
    captured = capsys.readouterr()
    assert "History loaded successfully" in captured.out

def test_load_command_failure(monkeypatch, capsys):
    """Test the load command when loading history fails."""
    inputs = iter(["load", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    error_message = "Unable to read history file"
    with patch.object(
        calc,
        "load_history",
        side_effect=OperationError(error_message)
    ) as mock_load:
        calculator_repl(calc)
    # Verify load_history was called once
    mock_load.assert_called_once_with()
    # Verify the error message was displayed
    captured = capsys.readouterr()
    assert f"Error loading history: {error_message}" in captured.out
    # Verify the calculator exits successfully
    assert "Goodbye!" in captured.out

# Test Clearing History

def test_clear_history(calculator_instance: Calculator):
    operation = OperationFactory.create_operation('add')
    calculator_instance.set_operation(operation)
    calculator_instance.perform_operation(2, 3)
    calculator_instance.clear_history()
    assert calculator_instance.history == []
    assert calculator_instance.undo_stack == []
    assert calculator_instance.redo_stack == []

def test_clear_command(monkeypatch, capsys):
    """Test that the clear command clears calculation history."""
    inputs = iter(["clear", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    with patch.object(calc, "clear_history") as mock_clear:
        calculator_repl(calc)
    # Verify clear_history() was called exactly once
    mock_clear.assert_called_once_with()
    # Verify the success message was printed
    captured = capsys.readouterr()
    expected_message = (
        Fore.GREEN + "History cleared" + Style.RESET_ALL
    )
    assert expected_message in captured.out
    # Verify the calculator exits successfully
    assert "Goodbye!" in captured.out

# Test REPL Commands (using patches for input/output handling)

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calc = Calculator()
        calculator_repl(calc)
        mock_save_history.assert_called_once()
        mock_print.assert_any_call(Fore.GREEN + "History saved successfully." + Style.RESET_ALL)
        mock_print.assert_any_call(Fore.BLUE + Back.WHITE + Style.BRIGHT + "Goodbye!" + Style.RESET_ALL)

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calc = Calculator()
    calculator_repl(calc)
    mock_print.assert_any_call(Fore.WHITE + Back.MAGENTA + Style.BRIGHT + "\nAvailable commands:" + Style.RESET_ALL)

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    config = CalculatorConfig(precision=2)
    calc = Calculator(config)
    calculator_repl(calc)
    mock_print.assert_any_call(Fore.GREEN + Back.WHITE + Style.BRIGHT + "\nResult: 5.00" + Style.RESET_ALL)

@patch("app.calculator_repl.Calculator")
def test_history_command(mock_calculator, capsys):
    """Test that the history command displays calculation history."""

    calculator_instance = mock_calculator.return_value
    calculator_instance.show_history.return_value = []

    with patch("builtins.input", side_effect=["history", "exit"]):
        calculator_repl(calculator_instance)

    calculator_instance.show_history.assert_called_once_with()

    captured = capsys.readouterr()
    assert "No calculations in history" in captured.out

def test_history_command_calculator(monkeypatch, capsys):
    """Test the history command in calculator_repl."""
    inputs = iter(["history", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    with patch.object(
        calc,
        "show_history",
        return_value=[]
    ) as mock_history:
        calculator_repl(calc)

    # Verify show_history was called once
    mock_history.assert_called_once_with()

    # Verify the empty history message
    captured = capsys.readouterr()
    assert "No calculations in history" in captured.out

    # Verify the calculator exited
    assert "Goodbye!" in captured.out

def test_history_empty(monkeypatch, capsys):
    inputs = iter(["clear","history", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "No calculations in history" in captured.out

def test_history_print(monkeypatch, capsys):
    inputs = iter(["add", "2", "3", "history", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Calculation History:" in captured.out

def test_cancelled_operation_first(monkeypatch, capsys):
    inputs = iter(["add", "cancel", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Operation cancelled" in captured.out

def test_cancelled_operation_second(monkeypatch, capsys):
    inputs = iter(["add", "4", "cancel", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Operation cancelled" in captured.out

def test_display_help(monkeypatch, capsys):
    """Test that the correct help message is displayed."""

    inputs = iter(["help", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    calc = Calculator()
    calculator_repl(calc)

    captured = capsys.readouterr()

    # Check that the help message contains the supported commands
    assert "Available commands:" in captured.out
    assert "add, subtract, multiply, divide" in captured.out
    assert "history" in captured.out
    assert "clear" in captured.out
    assert "undo" in captured.out
    assert "redo" in captured.out
    assert "save" in captured.out
    assert "load" in captured.out
    assert "exit" in captured.out

def test_display_history_empty(monkeypatch, capsys):
    """Test the message displayed when calculation history is empty."""
    inputs = iter(["history", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    with patch.object(calc, "show_history", return_value=[]):
        calculator_repl(calc)
    captured = capsys.readouterr()

    # Remove ANSI colour codes
    output = re.sub(r'\x1b\[[0-9;]*m', '', captured.out)
    assert "No calculations in history" in output

def test_display_history(monkeypatch, capsys):
    """Test that calculation history is displayed correctly."""
    history = [
        "addition: 1.0 add 1.0 = 2.0",
        "subtraction: 5.0 subtract 2.0 = 3.0",
        "multiplication: 2.0 multiply 4.0 = 8.0",
        "division: 10.0 divide 2.0 = 5.0"
    ]
    inputs = iter(["history", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    with patch.object(calc, "show_history", return_value=history):
        calculator_repl(calc)
    captured = capsys.readouterr()

    # Remove ANSI colour codes
    output = re.sub(r'\x1b\[[0-9;]*m', '', captured.out)

    expected_output = """Calculation History:
1. addition: 1.0 add 1.0 = 2.0
2. subtraction: 5.0 subtract 2.0 = 3.0
3. multiplication: 2.0 multiply 4.0 = 8.0
4. division: 10.0 divide 2.0 = 5.0"""

    assert expected_output in output

def test_validation_error(monkeypatch, capsys):
    def mock_perform_operation(self, a, b):
        raise ValidationError("Invalid input")
    monkeypatch.setattr(
        "app.calculator.Calculator.perform_operation",
        mock_perform_operation
    )
    inputs = iter([
        "add",
        "2",
        "3",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Error: Invalid input" in captured.out

def test_unexpected_calculation_error(monkeypatch, capsys):
    def mock_perform_operation(self, a, b):
        raise Exception("Something went wrong")
    monkeypatch.setattr(
        "app.calculator.Calculator.perform_operation",
        mock_perform_operation
    )
    inputs = iter([
        "add",
        "2",
        "3",
        "exit"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    calc = Calculator()
    calculator_repl(calc)
    captured = capsys.readouterr()
    assert "Unexpected error: Something went wrong" in captured.out

@patch('builtins.input', side_effect=['divide', '1', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_precision_2(mock_print, mock_input):
    config = CalculatorConfig(precision=2)
    calc = Calculator(config)

    calculator_repl(calc)

    mock_print.assert_any_call(
        Fore.GREEN + Back.WHITE + Style.BRIGHT +
        "\nResult: 0.33" +
        Style.RESET_ALL
    )

@patch('builtins.input', side_effect=['divide', '1', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_precision_4(mock_print, mock_input):
    config = CalculatorConfig(precision=4)
    calc = Calculator(config)

    calculator_repl(calc)

    mock_print.assert_any_call(
        Fore.GREEN + Back.WHITE + Style.BRIGHT +
        "\nResult: 0.3333" +
        Style.RESET_ALL
    )

@patch('builtins.input', side_effect=['divide', '1', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_default_precision(
    mock_print, mock_input, monkeypatch
):
    monkeypatch.delenv("CALCULATOR_PRECISION", raising=False)

    calc = Calculator()

    calculator_repl(calc)

    mock_print.assert_any_call(
        Fore.GREEN + Back.WHITE + Style.BRIGHT +
        "\nResult: 0.3333333333" +
        Style.RESET_ALL
    )

@patch('builtins.input', side_effect=['divide', '1', '2', 'exit'])
@patch('builtins.print')
def test_calculator_repl_preserves_trailing_zeros(mock_print, mock_input):
    config = CalculatorConfig(precision=2)
    calc = Calculator(config)

    calculator_repl(calc)

    mock_print.assert_any_call(
        Fore.GREEN + Back.WHITE + Style.BRIGHT +
        "\nResult: 0.50" +
        Style.RESET_ALL
    )

@patch('builtins.input', side_effect=['divide', '1', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_environment_precision(
    mock_print, mock_input, monkeypatch
):
    monkeypatch.setenv("CALCULATOR_PRECISION", "2")

    config = CalculatorConfig()
    calc = Calculator(config)

    calculator_repl(calc)

    mock_print.assert_any_call(
        Fore.GREEN + Back.WHITE + Style.BRIGHT +
        "\nResult: 0.33" +
        Style.RESET_ALL
    )

@patch('builtins.input', side_effect=['multiply', '12.5', '16.7', 'exit'])
@patch('builtins.print')
def test_calculator_repl_precision_with_exact_result(
    mock_print, mock_input
):
    config = CalculatorConfig(precision=3)
    calc = Calculator(config)

    calculator_repl(calc)

    mock_print.assert_any_call(
        Fore.GREEN + Back.WHITE + Style.BRIGHT +
        "\nResult: 208.750" +
        Style.RESET_ALL
    )

def test_load_history_respects_max_history_size(isolated_calculator):
    calculator = isolated_calculator

    df = pd.DataFrame([
        {
            'operation': 'Addition',
            'operand1': str(i),
            'operand2': '1',
            'result': str(i + 1),
            'timestamp': f'2026-01-0{i}T10:00:00'
        }
        for i in range(1, 6)
    ])

    df.to_csv(calculator.config.history_file, index=False)

    calculator.load_history()

    assert len(calculator.history) == 3
    assert calculator.history[0].operand1 == Decimal("3")
    assert calculator.history[-1].operand1 == Decimal("5")

def test_load_history_below_limit(isolated_calculator):
    calculator = isolated_calculator

    df = pd.DataFrame([
        {
            'operation': 'Addition',
            'operand1': str(i),
            'operand2': '1',
            'result': str(i + 1),
            'timestamp': f'2026-01-0{i}T10:00:00'
        }
        for i in range(1, 3)
    ])

    df.to_csv(calculator.config.history_file, index=False)

    calculator.load_history()

    assert len(calculator.history) == 2
    assert calculator.history[0].operand1 == Decimal("1")
    assert calculator.history[1].operand1 == Decimal("2")

def test_load_history_with_zero_limit(tmp_path, monkeypatch):
    monkeypatch.delenv("CALCULATOR_HISTORY_FILE", raising=False)
    monkeypatch.delenv("CALCULATOR_HISTORY_DIR", raising=False)
    monkeypatch.delenv("CALCULATOR_BASE_DIR", raising=False)

    config = CalculatorConfig(
        base_dir=tmp_path,
        max_history_size=0
    )

    calculator = Calculator(config)

    df = pd.DataFrame([
        {
            'operation': 'Addition',
            'operand1': '1',
            'operand2': '2',
            'result': '3',
            'timestamp': '2026-01-01T10:00:00'
        }
    ])

    df.to_csv(config.history_file, index=False)

    calculator.load_history()

    assert calculator.history == []

def test_load_history_retains_newest_calculations(isolated_calculator):
    calculator = isolated_calculator

    df = pd.DataFrame([
        {
            'operation': 'Addition',
            'operand1': str(i),
            'operand2': '1',
            'result': str(i + 1),
            'timestamp': f'2026-01-0{i}T10:00:00'
        }
        for i in range(1, 6)
    ])

    df.to_csv(calculator.config.history_file, index=False)

    calculator.load_history()

    assert len(calculator.history) == 3

    assert calculator.history[0].operand1 == Decimal("3")
    assert calculator.history[1].operand1 == Decimal("4")
    assert calculator.history[2].operand1 == Decimal("5")

def test_load_history_exactly_at_limit(isolated_calculator):
    calculator = isolated_calculator

    df = pd.DataFrame([
        {
            'operation': 'Addition',
            'operand1': str(i),
            'operand2': '1',
            'result': str(i + 1),
            'timestamp': f'2026-01-0{i}T10:00:00'
        }
        for i in range(1, 4)
    ])

    df.to_csv(calculator.config.history_file, index=False)

    calculator.load_history()

    assert len(calculator.history) == 3

    assert calculator.history[0].operand1 == Decimal("1")
    assert calculator.history[1].operand1 == Decimal("2")
    assert calculator.history[2].operand1 == Decimal("3")

def test_perform_operation_respects_max_history_size(tmp_path):
    config = CalculatorConfig(
        base_dir=tmp_path,
        max_history_size=3
    )

    calculator = Calculator(config)
    calculator.set_operation(
        OperationFactory.create_operation('add')
    )

    for i in range(1, 5):
        calculator.perform_operation(i, 1)

    assert len(calculator.history) == 3

    assert calculator.history[0].operand1 == Decimal("2")
    assert calculator.history[1].operand1 == Decimal("3")
    assert calculator.history[2].operand1 == Decimal("4")

def test_load_history_missing_csv(isolated_calculator):
    calculator = isolated_calculator

    assert not calculator.config.history_file.exists()

    result = calculator.load_history()

    assert result is False
    assert calculator.history == []

def test_load_history_missing_csv_preserves_existing_history(
    isolated_calculator
):
    calculator = isolated_calculator

    calculator.set_operation(
        OperationFactory.create_operation('add')
    )

    calculator.perform_operation(2, 3)

    result = calculator.load_history()

    assert result is False
    assert len(calculator.history) == 1

    assert calculator.history[0].operand1 == Decimal("2")
    assert calculator.history[0].operand2 == Decimal("3")
    assert calculator.history[0].result == Decimal("5")

def test_load_history_empty_csv(isolated_calculator):
    calculator = isolated_calculator

    df = pd.DataFrame(
        columns=[
            'operation',
            'operand1',
            'operand2',
            'result',
            'timestamp'
        ]
    )

    df.to_csv(calculator.config.history_file, index=False)

    result = calculator.load_history()

    assert result is True
    assert calculator.history == []

def test_undo_restores_history_within_limit(isolated_calculator):
    calculator = isolated_calculator

    calculator.set_operation(
        OperationFactory.create_operation('add')
    )

    # Add three calculations
    calculator.perform_operation(1, 1)
    calculator.perform_operation(2, 2)
    calculator.perform_operation(3, 3)

    assert len(calculator.history) == 3

    # Add a fourth calculation
    calculator.perform_operation(4, 4)

    assert len(calculator.history) == 3

    # Undo the fourth calculation
    calculator.undo()

    assert len(calculator.history) == 3

    assert calculator.history[0].operand1 == Decimal("1")
    assert calculator.history[1].operand1 == Decimal("2")
    assert calculator.history[2].operand1 == Decimal("3")

def test_redo_restores_history_within_limit(isolated_calculator):
    calculator = isolated_calculator

    calculator.set_operation(
        OperationFactory.create_operation('add')
    )

    # Perform three calculations
    calculator.perform_operation(1, 1)
    calculator.perform_operation(2, 2)
    calculator.perform_operation(3, 3)

    # Perform a fourth calculation
    calculator.perform_operation(4, 4)

    assert len(calculator.history) == 3

    # Undo the fourth calculation
    calculator.undo()

    assert len(calculator.history) == 3

    # Redo the fourth calculation
    calculator.redo()

    assert len(calculator.history) == 3

    assert calculator.history[0].operand1 == Decimal("2")
    assert calculator.history[1].operand1 == Decimal("3")
    assert calculator.history[2].operand1 == Decimal("4")