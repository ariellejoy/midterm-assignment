# This line is importing the "calculator" function from another file.
# Imagine that "calculator" is like a tool or recipe that we've already written somewhere else,
# and now we are telling the computer, "Go and find that calculator tool for us."
# The "app" part is like a folder, and inside that folder, there's another file called "calculator.py",
# which has the tool (function) called "calculator" that we need.

import config

from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.logger import Logger
from app.history import LoggingObserver, AutoSaveObserver


def main():
    logger = Logger()
    calc = Calculator()

    calc.add_observer(LoggingObserver(logger))
    calc.add_observer(AutoSaveObserver(calc))

    logger.info("Starting the REPL calculator.")

    calculator_repl(calc)


if __name__ == "__main__":
    main()