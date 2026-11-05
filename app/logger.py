
import logging
from app.calculator_config import CalculatorConfig


class Logger:
    """Centralized logging for the REPL calculator."""

    def __init__(self, config: CalculatorConfig) -> None:
        """Configure the calculator's file logger using CalculatorConfig."""

        self.config = config

        # Ensure the configured log directory exists.
        self.config.log_dir.mkdir(parents=True, exist_ok=True)

        # Use the configured log file.
        log_file = self.config.log_file

        self.logger = logging.getLogger("calculator")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # Avoid duplicate handlers.
        if not self.logger.handlers:
            file_handler = logging.FileHandler(
                log_file,
                encoding=self.config.default_encoding
            )

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - "
                "%(levelname)s - %(message)s"
            )

            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def log_calculation(
        self,
        operation: str,
        a: object,
        b: object,
        result: object
    ) -> None:
        self.logger.info(
            "Calculation: %s | operands=(%s, %s) | result=%s",
            operation,
            a,
            b,
            result
        )

    def log_exception(self, message: str) -> None:
        self.logger.exception(message)
