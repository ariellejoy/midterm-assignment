import subprocess
import sys


def run_calculator(user_input):
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=user_input,
        capture_output=True,
        text=True,
        timeout=10
    )

    return result

def test_calculator_starts_and_exits():
    result = run_calculator("exit\n")

    assert result.returncode == 0
    assert "Calculator started." in result.stdout
    assert "Goodbye!" in result.stdout

def test_calculator_addition():
    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 5" in result.stdout

def test_calculator_subtraction():
    result = run_calculator(
        "subtract\n"
        "10\n"
        "4\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 6" in result.stdout

def test_calculator_multiplication():
    result = run_calculator(
        "multiply\n"
        "5\n"
        "3\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 15" in result.stdout

def test_calculator_division():
    result = run_calculator(
        "divide\n"
        "10\n"
        "2\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 5" in result.stdout

def test_calculator_invalid_command():
    result = run_calculator(
        "hello\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Unknown command: 'hello'" in result.stdout

def test_calculator_power():
    result = run_calculator(
        "power\n"
        "2\n"
        "3\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 8" in result.stdout

def test_calculator_root():
    result = run_calculator(
        "root\n"
        "9\n"
        "2\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 3" in result.stdout

def test_calculator_modulus():
    result = run_calculator(
        "modulus\n"
        "10\n"
        "3\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 1" in result.stdout

def test_calculator_integer_division():
    result = run_calculator(
        "int_divide\n"
        "10\n"
        "3\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 3" in result.stdout

def test_calculator_percentage():
    result = run_calculator(
        "percentage\n"
        "50\n"
        "200\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 25" in result.stdout

def test_calculator_absolute_difference():
    result = run_calculator(
        "abs_diff\n"
        "4\n"
        "10\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 6" in result.stdout

def test_calculator_multiple_operations():
    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "subtract\n"
        "10\n"
        "4\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 5" in result.stdout
    assert "Result: 6" in result.stdout
    assert "Goodbye!" in result.stdout

def test_calculator_help():
    result = run_calculator(
        "help\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Available commands:" in result.stdout
    assert "add" in result.stdout
    assert "subtract" in result.stdout
    assert "history" in result.stdout
    assert "undo" in result.stdout
    assert "redo" in result.stdout

def test_calculator_history():
    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "history\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 5" in result.stdout
    assert "Calculation History:" in result.stdout

def test_calculator_clear_history():
    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "clear\n"
        "history\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "History cleared" in result.stdout
    assert "No calculations in history" in result.stdout

def test_calculator_undo():
    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "undo\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Result: 5" in result.stdout
    assert "Operation undone" in result.stdout

def test_calculator_redo():
    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "undo\n"
        "redo\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Operation undone" in result.stdout
    assert "Operation redone" in result.stdout

def test_calculator_save():
    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "save\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "History saved successfully" in result.stdout

def test_calculator_load():
    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "save\n"
        "clear\n"
        "load\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "History loaded successfully" in result.stdout

def test_calculator_cancel_operation():
    result = run_calculator(
        "add\n"
        "cancel\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Operation cancelled" in result.stdout
    assert "Goodbye!" in result.stdout