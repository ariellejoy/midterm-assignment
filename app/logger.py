
import logging
from pathlib import Path

import config


class Logger:
    """Centralized logging for the REPL calculator."""

    def __init__(self) -> None:
        """Configure the calculator's file logger."""
        log_dir = Path(config.CALCULATOR_LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "calculator.log"
        # Create the parent directory if it does not exist.
        #log_file.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("calculator")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # Avoid adding duplicate handlers if initialized more than once.
        if not self.logger.handlers:
            file_handler = logging.FileHandler(
                log_file,
                encoding="utf-8"
            )

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - "
                "%(levelname)s - %(message)s"
            )

            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        """Log an informational event/important app event."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log an errors and/or failed operations."""
        self.logger.error(message)

    def log_calculation(
        self,
        operation: str,
        a: object,
        b: object,
        result: object
    ) -> None:
        """Log a successful calculation."""
        self.logger.info(
            "Calculation: %s | operands=(%s, %s) | result=%s",
            operation,
            a,
            b,
            result
        )

    def log_exception(self, message: str) -> None:
        """Log an exception with its traceback."""
        self.logger.exception(message)
