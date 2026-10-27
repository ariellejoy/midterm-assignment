# This line is importing the "calculator" function from another file.
# Imagine that "calculator" is like a tool or recipe that we've already written somewhere else,
# and now we are telling the computer, "Go and find that calculator tool for us."
# The "app" part is like a folder, and inside that folder, there's another file called "calculator.py",
# which has the tool (function) called "calculator" that we need.

import config

from app.calculator import calculator
from app.logger import Logger
from app.history import LoggingObserver, AutoSaveObserver

def main():
    logger = Logger()
    calculator = Calculator(config=config)

    logging_observer = LoggingObserver(logger)
    autosave_observer = AutoSaveObserver(calculator)

    calculator.add_observer(logging_observer)
    calculator.add_observer(autosave_observer)

    logger.info("Starting the REPL calculator.")
    calculator.run()

if __name__ == "__main__":
    calculator()
