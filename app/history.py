########################
# History Management    #
########################

from abc import ABC, abstractmethod
from typing import Any, List
from app.calculation import Calculation

import logging
from app.logger import Logger


class HistoryObserver(ABC):
    """
    Abstract base class for calculator observers.

    This class defines the interface for observers that monitor and react to
    new calculation events. Implementing classes must provide an update method
    to handle the received Calculation instance.
    """

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """
        Handle new calculation event.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        pass  # pragma: no cover
    
    @abstractmethod
    def update_history(self, history: List[Calculation]) -> None:
        """
        Handle history change event.

        Args:
            history (List[Calculation]): The updated calculation history.
        """
        pass  # pragma: no cover


class LoggingObserver(HistoryObserver):
    """
    Observer that logs completed calculations to a file.

    Implements the Observer pattern by listening for new calculations and logging
    their details to a log file.
    """

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def update(self, calculation: Calculation) -> None:
        """
        Log calculation details.

        This method is called whenever a new calculation is performed. It records
        the operation, operands, and result in the log file.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        if calculation is None:
            self.logger.warning("Received an empty calculation.")
            raise AttributeError("Calculation cannot be None")
        
        self.logger.log_calculation(
            calculation.operation,
            calculation.operand1,
            calculation.operand2,
            calculation.result
        )
    
    def update_history(self, history: List[Calculation]) -> None:
        """
        Logs changes to calculation history

        Args:
            history (List[Calculation]): The updated calculation history.
        """
        if history is None: 
             raise AttributeError("History cannot be None") 
        
        logging.info(
            "Calculation history updated. "
            "Current number of calculations: %d",
            len(history)
        )

class AutoSaveObserver(HistoryObserver):
    """
    Observer that automatically saves calculations.

    Implements the Observer pattern by listening for new calculations and
    triggering an automatic save of the calculation history if the auto-save
    feature is enabled in the configuration.
    """

    def __init__(self, calculator: Any) -> None:
        """
        Initialize the AutoSaveObserver.

        Args:
            calculator (Any): The calculator instance to interact with.
                Must have 'config' and 'save_history' attributes.

        Raises:
            TypeError: If the calculator does not have the required attributes.
        """
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'save_history'):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:
        """
        Trigger auto-save.

        This method is called whenever a new calculation is performed. If the
        auto-save feature is enabled, it saves the current calculation history.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info("History auto-saved")

    def update_history(self, history: List[Calculation]) -> None:
        """
        Trigger auto-save after undo or redo.
        """
        if history is None:
            raise AttributeError("History cannot be None")

        self._auto_save()

    def _auto_save(self) -> None:
        """
        Save calculation history if auto-save is enabled.
        """
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info("History auto-saved")
