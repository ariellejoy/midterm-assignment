import subprocess
import sys
from pathlib import Path
import csv
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_FILE = PROJECT_ROOT / "main.py"

def run_calculator(user_input, env=None):
    result = subprocess.run(
        [sys.executable, str(MAIN_FILE)],
        input=user_input,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=PROJECT_ROOT,
        env=env if env is not None else os.environ.copy()
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

def test_calculator_rejects_division_by_zero():
    result = run_calculator(
        "divide\n"
        "10\n"
        "0\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Error:" in result.stdout

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
        "history\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Operation undone" in result.stdout
    assert "No calculations in history" in result.stdout

def test_calculator_redo():
    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "undo\n"
        "history\n"
        "redo\n"
        "history\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Operation undone" in result.stdout
    assert "No calculations in history" in result.stdout
    assert "Operation redone" in result.stdout
    assert "Calculation History:" in result.stdout
    assert "Addition(2, 3) = 5" in result.stdout


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

def test_calculator_load(tmp_path):

    history_file = tmp_path / "calculator_history.csv"

    with open(history_file, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "operation",
            "operand1",
            "operand2",
            "result",
            "timestamp"
        ])

        writer.writerow([
            "Addition",
            2,
            3,
            5,
            "2026-11-04 10:00:00"
        ])

    env = os.environ.copy()
    env["CALCULATOR_HISTORY_FILE"] = str(history_file)

    result = run_calculator(
        "load\n"
        "history\n"
        "exit\n",
        env=env
    )

    assert result.returncode == 0
    assert "History loaded successfully" in result.stdout
    assert "Addition(2, 3) = 5" in result.stdout

def test_calculator_cancel_operation():
    result = run_calculator(
        "add\n"
        "cancel\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Operation cancelled" in result.stdout
    assert "Goodbye!" in result.stdout

def test_calculator_autosaves_history(tmp_path):
    history_file = tmp_path / "calculator_history.csv"

    env = os.environ.copy()
    env["CALCULATOR_HISTORY_FILE"] = str(history_file)
    env["CALCULATOR_AUTO_SAVE"] = "true"

    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "exit\n",
        env=env
    )

    assert result.returncode == 0
    assert history_file.exists()

    content = history_file.read_text()

    assert "Addition" in content
    assert "2" in content
    assert "3" in content

def test_calculator_autosave_disabled(tmp_path):
    history_file = tmp_path / "calculator_history.csv"

    env = os.environ.copy()
    env["CALCULATOR_HISTORY_FILE"] = str(history_file)
    env["CALCULATOR_AUTO_SAVE"] = "false"

    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "exit\n",
        env=env
    )

    assert result.returncode == 0
    assert history_file.exists()

    with open(history_file, newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1

def test_calculator_logs_calculations(tmp_path):
    log_file = tmp_path / "calculator.log"

    env = os.environ.copy()
    env["CALCULATOR_LOG_FILE"] = str(log_file)

    result = run_calculator(
        "add\n"
        "2\n"
        "3\n"
        "exit\n",
        env=env
    )

    assert result.returncode == 0
    assert log_file.exists()

    log_content = log_file.read_text()

    assert "Calculation:" in log_content
    assert "Addition" in log_content
    assert "operands=(2, 3)" in log_content
    assert "result=5" in log_content

def test_calculator_rejects_invalid_first_number():
    result = run_calculator(
        "add\n"
        "hello\n"
        "2\n"
        "3\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Invalid first number" in result.stdout
    assert "Result: 5" in result.stdout

def test_calculator_rejects_invalid_second_number():
    result = run_calculator(
        "add\n"
        "2\n"
        "hello\n"
        "3\n"
        "exit\n"
    )

    assert result.returncode == 0
    assert "Invalid second number" in result.stdout
    assert "Result: 5" in result.stdout

def test_calculator_loads_multiple_csv_entries(tmp_path):

    history_file = tmp_path / "calculator_history.csv"

    with open(history_file, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "operation",
            "operand1",
            "operand2",
            "result",
            "timestamp"
        ])

        writer.writerow([
            "Addition", 2, 3, 5,
            "2026-11-04 10:00:00"
        ])

        writer.writerow([
            "Subtraction", 10, 4, 6,
            "2026-11-04 10:01:00"
        ])

    env = os.environ.copy()
    env["CALCULATOR_HISTORY_FILE"] = str(history_file)

    result = run_calculator(
        "load\n"
        "history\n"
        "exit\n",
        env=env
    )

    assert result.returncode == 0
    assert "History loaded successfully" in result.stdout
    assert "Addition(2, 3) = 5" in result.stdout
    assert "Subtraction(10, 4) = 6" in result.stdout