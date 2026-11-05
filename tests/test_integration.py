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