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

def calculator_repl(calc):
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:

        print(Fore.BLUE + Back.WHITE + Style.BRIGHT + "Calculator started. Type 'help' for commands." + Style.RESET_ALL)

        while True:
            try:
                # Prompt the user for a command
                command = input(Style.BRIGHT + "\nEnter command: " + Style.RESET_ALL).lower().strip()

                if command == 'help':
                    # Display available commands
                    print(Fore.WHITE + Back.MAGENTA + Style.BRIGHT + "\nAvailable commands:" + Style.RESET_ALL)
                    print(Style.BRIGHT + "  add, subtract, multiply, divide, power, root, modulus, int_divide, percentage, abs_diff -" + Style.RESET_ALL + " Perform calculations")
                    print(Style.BRIGHT + "  history -" + Style.RESET_ALL + " Show calculation history")
                    print(Style.BRIGHT + "  clear -" + Style.RESET_ALL + " Clear calculation history")
                    print(Style.BRIGHT + "  undo -" + Style.RESET_ALL + " Undo the last calculation")
                    print(Style.BRIGHT + "  redo -" + Style.RESET_ALL + " Redo the last undone calculation")
                    print(Style.BRIGHT + "  save -" + Style.RESET_ALL + " Save calculation history to file")
                    print(Style.BRIGHT + "  load -" + Style.RESET_ALL + " Load calculation history from file")
                    print(Style.BRIGHT + "  exit -" + Style.RESET_ALL + " Exit the calculator")
                    continue #pragma: no cover

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully." + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"Warning: Could not save history: {e}" + Style.RESET_ALL)
                    print(Fore.BLUE + Back.WHITE + Style.BRIGHT + "Goodbye!" + Style.RESET_ALL)
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print(Fore.YELLOW + "No calculations in history" + Style.RESET_ALL)
                    else:
                        print(Fore.WHITE + Back.MAGENTA + Style.BRIGHT + "\nCalculation History:" + Style.RESET_ALL)
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print(Fore.GREEN + "History cleared" + Style.RESET_ALL)
                    continue #pragma: no cover

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print(Fore.GREEN + "Operation undone" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Nothing to undo" + Style.RESET_ALL)
                    continue #pragma: no cover

                if command == 'redo':
                    # Redo the last undone calculation
                    if calc.redo():
                        print(Fore.GREEN + "Operation redone" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Nothing to redo" + Style.RESET_ALL)
                    continue #pragma: no cover

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully" + Style.RESET_ALL)
                    except OperationError as e:
                        print(Fore.RED + f"Error saving history: {e}" + Style.RESET_ALL)
                    continue #pragma: no cover

                if command == 'load':
                    # Load calculation history from file
                    try:
                        if calc.load_history():
                            print(Fore.GREEN + "History loaded successfully" + Style.RESET_ALL)
                        else:
                            print(Fore.YELLOW + "No saved history file found." + Style.RESET_ALL)
                    except OperationError as e:
                        print(Fore.RED + f"Error loading history: {e}" + Style.RESET_ALL)
                    continue #pragma: no cover
               
                
                
                if command in ['add', 'subtract', 'multiply', 'divide',
               'power', 'root', 'modulus', 'int_divide',
               'percentage', 'abs_diff']:

                    try:
                        print(Back.CYAN + Style.BRIGHT + "\nEnter numbers (or 'cancel' to abort):" + Style.RESET_ALL)

                        # Get and validate the first number
                        while True:
                            a = input(Style.BRIGHT + "First number: " + Style.RESET_ALL)

                            if a.lower().strip() == 'cancel':
                                print(Fore.YELLOW + "Operation cancelled" + Style.RESET_ALL)
                                break
                            try:
                                validated_a = InputValidator.validate_number(a, calc.config)
                                break
                            except ValidationError as e:
                                print(Fore.RED + f"Invalid first number: {e}" + Style.RESET_ALL)
                        if a.lower().strip() == 'cancel':
                            continue

                        # Get and validate the second number
                        while True:
                            b = input(Style.BRIGHT + "Second number: " + Style.RESET_ALL)

                            if b.lower().strip() == 'cancel':
                                print(Fore.YELLOW + "Operation cancelled" + Style.RESET_ALL)
                                break

                            try:
                                validated_b = InputValidator.validate_number(b, calc.config)
                                break
                            
                            except ValidationError as e:
                                print(Fore.RED + f"Invalid second number: {e}" + Style.RESET_ALL)
                        if b.lower().strip() == 'cancel':
                            continue

                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        result = calc.perform_operation(validated_a, validated_b)

                        if isinstance(result, Decimal):
                            result = format(result.normalize(), 'f')

                        print(Fore.GREEN + Back.WHITE + Style.BRIGHT + f"\nResult: {result}" + Style.RESET_ALL)

                    except (ValidationError, OperationError) as e:
                        print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)

                    except Exception as e:
                        print(Fore.RED + f"Unexpected error: {e}" + Style.RESET_ALL)

                    continue

                # Handle unknown commands
                print(Fore.YELLOW + f"Unknown command: '{command}'. Type 'help' for available commands." + Style.RESET_ALL)

            except KeyboardInterrupt: #pragma: no cover
                # Handle Ctrl+C interruption gracefully
                print(Fore.YELLOW + "\nOperation cancelled" + Style.RESET_ALL)
                continue #pragma: no cover
            except EOFError: #pragma: no cover
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print(Fore.RED + "\nInput terminated. Exiting..." + Style.RESET_ALL)
                break
            except Exception as e:
                # Handle any other unexpected exceptions
                print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                continue #pragma: no cover

    except Exception as e:
        # Handle fatal errors during initialization
        print(Fore.RED + Style.BRIGHT + f"Fatal error: {e}" + Style.RESET_ALL)
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise