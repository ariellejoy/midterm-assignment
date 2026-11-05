########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging
from colorama import Fore, Back, Style 

from app.calculator import Calculator, calculator, display_help, display_history
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory
from app.logger import Logger
from app.input_validators import InputValidator

def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()

        # initializing logger
        logger = Logger()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver(logger))
        calc.add_observer(AutoSaveObserver(calc))

        print("Calculator started. Type 'help' for commands.")

        while True:
            try:
                # Prompt the user for a command
                command = input("\nEnter command: ").lower().strip()

                if command == 'help':
                    # Display available commands
                    print("\nAvailable commands:")
                    print("  add, subtract, multiply, divide, power, root, modulus, int_divide, percentage, abs_diff - Perform calculations")
                    print("  history - Show calculation history")
                    print("  clear - Clear calculation history")
                    print("  undo - Undo the last calculation")
                    print("  redo - Redo the last undone calculation")
                    print("  save - Save calculation history to file")
                    print("  load - Load calculation history from file")
                    print("  exit - Exit the calculator")
                    continue #pragma: no cover

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print("History saved successfully.")
                    except Exception as e:
                        print(f"Warning: Could not save history: {e}")
                    print("Goodbye!")
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print("No calculations in history")
                    else:
                        print("\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print("History cleared")
                    continue #pragma: no cover

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print("Operation undone")
                    else:
                        print("Nothing to undo")
                    continue #pragma: no cover

                if command == 'redo':
                    # Redo the last undone calculation
                    if calc.redo():
                        print("Operation redone")
                    else:
                        print("Nothing to redo")
                    continue #pragma: no cover

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print("History saved successfully")
                    except OperationError as e:
                        print(f"Error saving history: {e}")
                    continue #pragma: no cover

                if command == 'load':
                    # Load calculation history from file
                    try:
                        if calc.load_history():
                            print("History loaded successfully")
                        else:
                            print("No saved history file found.")
                    except OperationError as e:
                        print(f"Error loading history: {e}")
                    continue #pragma: no cover
               
                
                
                if command in ['add', 'subtract', 'multiply', 'divide',
               'power', 'root', 'modulus', 'int_divide',
               'percentage', 'abs_diff']:

                    try:
                        print("\nEnter numbers (or 'cancel' to abort):")

                        # Get and validate the first number
                        while True:
                            a = input("First number: ")

                            if a.lower().strip() == 'cancel':
                                print("Operation cancelled")
                                break

                            try:
                                validated_a = InputValidator.validate_number(a, calc.config)
                                break
                            except ValidationError as e:
                                print(f"Invalid first number: {e}")
                        else:
                            continue

                        # Get and validate the second number
                        while True:
                            b = input("Second number: ")

                            if b.lower().strip() == 'cancel':
                                print("Operation cancelled")
                                break

                            try:
                                validated_b = InputValidator.validate_number(b, calc.config)
                                break
                            
                            except ValidationError as e:
                                print(f"Invalid second number: {e}")
                        else:
                            continue
                

                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        result = calc.perform_operation(validated_a, validated_b)

                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(f"\nResult: {result}")

                    except (ValidationError, OperationError) as e:
                        print(f"Error: {e}")

                    except Exception as e:
                        print(f"Unexpected error: {e}")

                    continue

                # Handle unknown commands
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt: #pragma: no cover
                # Handle Ctrl+C interruption gracefully
                print("\nOperation cancelled")
                continue #pragma: no cover
            except EOFError: #pragma: no cover
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print("\nInput terminated. Exiting...")
                break
            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"Error: {e}")
                continue #pragma: no cover

    except Exception as e:
        # Handle fatal errors during initialization
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise