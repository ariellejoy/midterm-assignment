########################
# Calculator Config    #
########################

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from numbers import Number
from pathlib import Path
import os
from typing import Optional

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

# helper functions
def get_int_config(name: str, default: int) -> int:
    """Read an integer environment variable safely."""
    value = os.getenv(name, str(default))

    try:
        return int(value)
    except (ValueError, TypeError) as exc:
        raise ConfigurationError(
            f"Invalid {name} value: expected an integer, got '{value}'"
        ) from exc

def get_decimal_config(name: str, default: str) -> Decimal:
    """Read a decimal environment variable safely."""
    value = os.getenv(name, default)
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ConfigurationError(
            f"Invalid {name} value: expected a number, got '{value}'"
        ) from exc
    if not result.is_finite():
        raise ConfigurationError(
            f"Invalid {name} value: must be a finite number"
        )
    return result

# Load environment variables from a .env file into the program's environment
load_dotenv()


def get_project_root() -> Path:
    """
    Get the project root directory.

    This function determines the root directory of the project by navigating up
    the directory hierarchy from the current file's location.

    Returns:
        Path: The root directory path of the project.
    """
    # Get the directory of the current file (app/calculator_config.py)
    current_file = Path(__file__)
    # Navigate up two levels to reach the project root (from app/calculator_config.py to project root)
    return current_file.parent.parent


@dataclass
class CalculatorConfig:
    """
    Calculator configuration settings.

    This class manages all configuration parameters required by the calculator
    application, including directory paths, history size, auto-save preferences,
    calculation precision, maximum input values, and default encoding.

    Configuration can be set via environment variables or by passing parameters
    directly to the class constructor.
    """

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        max_history_size: Optional[int] = None,
        auto_save: Optional[bool] = None,
        precision: Optional[int] = None,
        max_input_value: Optional[Number] = None,
        default_encoding: Optional[str] = None
    ):
        """
        Initialize configuration with environment variables and defaults.

        Args:
            base_dir (Optional[Path], optional): Base directory for the calculator. Defaults to None.
            max_history_size (Optional[int], optional): Maximum number of history entries. Defaults to None.
            auto_save (Optional[bool], optional): Whether to auto-save history. Defaults to None.
            precision (Optional[int], optional): Number of decimal places for calculations. Defaults to None.
            max_input_value (Optional[Number], optional): Maximum allowed input value. Defaults to None.
            default_encoding (Optional[str], optional): Default encoding for file operations. Defaults to None.
        """
        # Set base directory to project root by default
        project_root = get_project_root()
        self.base_dir = base_dir or Path(
            os.getenv('CALCULATOR_BASE_DIR', str(project_root))
        ).resolve()

        # Maximum history size
        self.max_history_size = (
            max_history_size
            if max_history_size is not None
            else get_int_config('CALCULATOR_MAX_HISTORY_SIZE', 1000)
        )

        # Auto-save preference
        auto_save_env = os.getenv('CALCULATOR_AUTO_SAVE', 'true').lower()
        if auto_save is not None:
            self.auto_save = auto_save
        elif auto_save_env in ('true', '1'):
            self.auto_save = True
        elif auto_save_env in ('false', '0'):
            self.auto_save = False
        else:
            raise ConfigurationError(
                f"Invalid CALCULATOR_AUTO_SAVE value: {auto_save_env}"
            )

        # Calculation precision
        self.precision = (
            precision
            if precision is not None
            else get_int_config('CALCULATOR_PRECISION', 10)
        )

        # Maximum input value allowed
        self.max_input_value = (
            max_input_value
            if max_input_value is not None
            else get_decimal_config('CALCULATOR_MAX_INPUT_VALUE', '1e999')
        )

        # Default encoding for file operations
        self.default_encoding = default_encoding or os.getenv(
            'CALCULATOR_DEFAULT_ENCODING', 'utf-8'
        )

    @property
    def log_dir(self) -> Path:
        """
        Get log directory path.

        Determines the directory path where log files will be stored.

        Returns:
            Path: The log directory path.
        """
        return Path(os.getenv(
            'CALCULATOR_LOG_DIR',
            str(self.base_dir / "logs")
        )).resolve()

    @property
    def history_dir(self) -> Path:
        """
        Get history directory path.

        Determines the directory path where calculation history files will be stored.

        Returns:
            Path: The history directory path.
        """
        return Path(os.getenv(
            'CALCULATOR_HISTORY_DIR',
            str(self.base_dir / "history")
        )).resolve()

    @property
    def history_file(self) -> Path:
        """
        Get history file path.

        Determines the file path for storing calculation history in CSV format.

        Returns:
            Path: The history file path.
        """
        return Path(os.getenv(
            'CALCULATOR_HISTORY_FILE',
            str(self.history_dir / "calculator_history.csv")
        )).resolve()

    @property
    def log_file(self) -> Path:
        """
        Get log file path.

        Determines the file path for storing log entries.

        Returns:
            Path: The log file path.
        """
        return Path(os.getenv(
            'CALCULATOR_LOG_FILE',
            str(self.log_dir / "calculator.log")
        )).resolve()

    def validate(self) -> None:
        """Validate configuration settings."""
        if (
            not isinstance(self.max_history_size, int)
            or isinstance(self.max_history_size, bool)
            or self.max_history_size < 0
        ):
            raise ConfigurationError(
                "max_history_size must be a non-negative integer"
            )

        if (
            not isinstance(self.precision, int)
            or isinstance(self.precision, bool)
            or self.precision <= 0
        ):
            raise ConfigurationError(
                "precision must be positive"
            )

        try:
            max_value = Decimal(str(self.max_input_value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ConfigurationError(
                "max_input_value must be a valid number"
            ) from exc

        if not max_value.is_finite() or max_value <= 0:
            raise ConfigurationError(
                "max_input_value must be a positive finite number"
            )