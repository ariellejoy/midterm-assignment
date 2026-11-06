import pytest
import os
from decimal import Decimal
from pathlib import Path
from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError

@pytest.fixture
def configured_environment(monkeypatch):
    monkeypatch.setenv('CALCULATOR_MAX_HISTORY_SIZE', '500')
    monkeypatch.setenv('CALCULATOR_AUTO_SAVE', 'false')
    monkeypatch.setenv('CALCULATOR_PRECISION', '8')
    monkeypatch.setenv('CALCULATOR_MAX_INPUT_VALUE', '1000')
    monkeypatch.setenv('CALCULATOR_DEFAULT_ENCODING', 'utf-16')
    monkeypatch.setenv('CALCULATOR_LOG_DIR', './test_logs')
    monkeypatch.setenv('CALCULATOR_HISTORY_DIR', './test_history')
    monkeypatch.setenv(
        'CALCULATOR_HISTORY_FILE',
        './test_history/test_history.csv'
    )
    monkeypatch.setenv(
        'CALCULATOR_LOG_FILE',
        './test_logs/test_log.log'
    )

def test_default_configuration(configured_environment):
    config = CalculatorConfig()

    assert config.max_history_size == 500
    assert config.auto_save is False
    assert config.precision == 8
    assert config.max_input_value == Decimal("1000")
    assert config.default_encoding == 'utf-16'
    assert config.log_dir == Path('./test_logs').resolve()
    assert config.history_dir == Path('./test_history').resolve()
    assert config.history_file == Path('./test_history/test_history.csv').resolve()
    assert config.log_file == Path('./test_logs/test_log.log').resolve()

def test_custom_configuration():
    config = CalculatorConfig(
        max_history_size=300,
        auto_save=True,
        precision=5,
        max_input_value=Decimal("500"),
        default_encoding="ascii"
    )
    assert config.max_history_size == 300
    assert config.auto_save is True
    assert config.precision == 5
    assert config.max_input_value == Decimal("500")
    assert config.default_encoding == "ascii"

def test_directory_properties(monkeypatch):
    monkeypatch.delenv('CALCULATOR_LOG_DIR', raising=False)
    monkeypatch.delenv('CALCULATOR_HISTORY_DIR', raising=False)
    
    config = CalculatorConfig(base_dir=Path('/custom_base_dir'))
   
    assert config.log_dir == Path('/custom_base_dir/logs').resolve()
    assert config.history_dir == Path('/custom_base_dir/history').resolve()

def test_file_properties(monkeypatch):
    monkeypatch.delenv('CALCULATOR_HISTORY_FILE', raising=False)
    monkeypatch.delenv('CALCULATOR_LOG_FILE', raising=False)
    monkeypatch.delenv('CALCULATOR_HISTORY_DIR', raising=False)
    monkeypatch.delenv('CALCULATOR_LOG_DIR', raising=False)

    config = CalculatorConfig(base_dir=Path('/custom_base_dir'))

    assert config.history_file == Path(
        '/custom_base_dir/history/calculator_history.csv'
    ).resolve()

    assert config.log_file == Path(
        '/custom_base_dir/logs/calculator.log'
    ).resolve()

def test_invalid_max_history_size():
    with pytest.raises(ConfigurationError, match="max_history_size cannot be negative"):
        config = CalculatorConfig(max_history_size=-1)
        config.validate()

def test_invalid_precision():
    with pytest.raises(ConfigurationError, match="precision must be positive"):
        config = CalculatorConfig(precision=-1)
        config.validate()

def test_invalid_max_input_value():
    with pytest.raises(ConfigurationError, match="max_input_value must be positive"):
        config = CalculatorConfig(max_input_value=Decimal("-1"))
        config.validate()

def test_auto_save_env_var_true():
    os.environ['CALCULATOR_AUTO_SAVE'] = 'true'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is True

def test_auto_save_env_var_one():
    os.environ['CALCULATOR_AUTO_SAVE'] = '1'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is True

def test_auto_save_env_var_false():
    os.environ['CALCULATOR_AUTO_SAVE'] = 'false'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is False

def test_auto_save_env_var_zero():
    os.environ['CALCULATOR_AUTO_SAVE'] = '0'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is False

def test_environment_overrides(configured_environment):
    config = CalculatorConfig()

    assert config.max_history_size == 500
    assert config.auto_save is False
    assert config.precision == 8
    assert config.max_input_value == Decimal("1000")
    assert config.default_encoding == 'utf-16'

def test_default_fallbacks(monkeypatch):
    monkeypatch.delenv('CALCULATOR_MAX_HISTORY_SIZE', raising=False)
    monkeypatch.delenv('CALCULATOR_AUTO_SAVE', raising=False)
    monkeypatch.delenv('CALCULATOR_PRECISION', raising=False)
    monkeypatch.delenv('CALCULATOR_MAX_INPUT_VALUE', raising=False)
    monkeypatch.delenv('CALCULATOR_DEFAULT_ENCODING', raising=False)
    config = CalculatorConfig()
    assert config.max_history_size == 1000
    assert config.auto_save is True
    assert config.precision == 10
    assert config.max_input_value == Decimal("1e999")
    assert config.default_encoding == 'utf-8'

def test_get_project_root():
    # Test that get_project_root() points to the correct path
    from app.calculator_config import get_project_root
    assert (get_project_root() / "app").exists()  # Adjust the path check as needed based on your file structure

def test_log_dir_property(monkeypatch):
    monkeypatch.delenv('CALCULATOR_LOG_DIR', raising=False)

    config = CalculatorConfig(base_dir=Path('/new_base_dir'))

    assert config.log_dir == Path('/new_base_dir/logs').resolve()

def test_history_dir_property(monkeypatch):
    monkeypatch.delenv('CALCULATOR_HISTORY_DIR', raising=False)

    config = CalculatorConfig(base_dir=Path('/new_base_dir'))
    assert config.history_dir == Path('/new_base_dir/history').resolve()

def test_log_file_property(monkeypatch):
    monkeypatch.delenv('CALCULATOR_LOG_FILE', raising=False)
    monkeypatch.delenv('CALCULATOR_LOG_DIR', raising=False)

    config = CalculatorConfig(base_dir=Path('/new_base_dir'))

    assert config.log_file == Path(
        '/new_base_dir/logs/calculator.log'
    ).resolve()

def test_history_file_property(monkeypatch):
    monkeypatch.delenv('CALCULATOR_HISTORY_FILE', raising=False)
    monkeypatch.delenv('CALCULATOR_HISTORY_DIR', raising=False)

    config = CalculatorConfig(base_dir=Path('/new_base_dir'))

    assert config.history_file == Path(
        '/new_base_dir/history/calculator_history.csv'
    ).resolve()

def test_default_precision(monkeypatch):
    monkeypatch.delenv("CALCULATOR_PRECISION", raising=False)

    config = CalculatorConfig()

    assert config.precision == 10

def test_precision_from_environment(monkeypatch):
    monkeypatch.setenv("CALCULATOR_PRECISION", "2")

    config = CalculatorConfig()

    assert config.precision == 2

def test_explicit_precision_overrides_environment(monkeypatch):
    monkeypatch.setenv("CALCULATOR_PRECISION", "2")

    config = CalculatorConfig(precision=4)

    assert config.precision == 4

def test_precision_zero_decimal_places(monkeypatch):
    monkeypatch.setenv("CALCULATOR_PRECISION", "0")

    config = CalculatorConfig()

    assert config.precision == 0

@pytest.mark.parametrize("precision", [1.5, "2", True, -1])
def test_invalid_precision_values(precision):
    config = CalculatorConfig(precision=precision)

    with pytest.raises(
        ConfigurationError,
        match="precision must be positive"
    ):
        config.validate()