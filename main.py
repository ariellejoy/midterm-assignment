# This line is importing the "calculator" function from another file.
# Imagine that "calculator" is like a tool or recipe that we've already written somewhere else,
# and now we are telling the computer, "Go and find that calculator tool for us."
# The "app" part is like a folder, and inside that folder, there's another file called "calculator.py",
# which has the tool (function) called "calculator" that we need.

import sys
from app.exceptions import ConfigurationError

from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.logger import Logger
from app.history import LoggingObserver, AutoSaveObserver
from app.calculator_config import CalculatorConfig

def main():
    try:
        # Initialize and validate configuration
        calculator_config = CalculatorConfig()
        calculator_config.validate()

    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    # Initialize logger
    logger = Logger(calculator_config)

    # Initialize calculator
    calc = Calculator(config=calculator_config)

    calc.add_observer(LoggingObserver(logger))
    calc.add_observer(AutoSaveObserver(calc))

    logger.info("Starting the REPL calculator.")

    try:
        calculator_repl(calc)
    finally:
        logger.info("REPL Calculator session has ended.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
