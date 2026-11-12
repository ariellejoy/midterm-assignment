########################
# Calculation Model    #
########################

from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation
import logging
from typing import Any, Dict
from app.exceptions import OperationError

@dataclass
class Calculation:
    """
    Value Object representing a single calculation.

    This class encapsulates the details of a mathematical calculation, including the
    operation performed, operands involved, the result, and the timestamp of the
    calculation. It provides methods for performing the calculation, serializing
    the data for storage, and deserializing data to recreate a Calculation instance.
    """

    # Required fields
    operation: str          # The name of the operation (e.g., "Addition")
    operand1: Decimal       # The first operand in the calculation
    operand2: Decimal       # The second operand in the calculation

    # Fields with default values
    result: Decimal # The result of the calculation, computed post-initialization
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)  # Time when the calculation was performed

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert calculation to dictionary for serialization.

        This method transforms the Calculation instance into a dictionary format,
        facilitating easy storage and retrieval (e.g., saving to a file).

        Returns:
            Dict[str, Any]: A dictionary containing the calculation data in a serializable format.
        """
        return {
            'operation': self.operation,
            'operand1': str(self.operand1),
            'operand2': str(self.operand2),
            'result': str(self.result),
            'timestamp': self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Calculation':
        """
        Create calculation from dictionary.
        Reconstructs a Calculation instance from saved data.
        """
        try:
            return Calculation(
                operation=data['operation'],
                operand1=Decimal(data['operand1']),
                operand2=Decimal(data['operand2']),
                result=Decimal(data['result']),
                timestamp=datetime.datetime.fromisoformat(data['timestamp'])
            )

        except (KeyError, InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid calculation data: {str(e)}")

    def __str__(self) -> str:
        """
        Return string representation of calculation.

        Provides a human-readable representation of the calculation,
        displaying numbers in standard decimal notation.
        """
        operand1 = format(self.operand1, 'f')
        operand2 = format(self.operand2, 'f')
        result = format(self.result, 'f')

        return f"{self.operation}({operand1}, {operand2}) = {result}"
    
    def __repr__(self) -> str:
        """
        Return detailed string representation of calculation.

        Provides a detailed and unambiguous string representation of the Calculation
        instance, useful for debugging.

        Returns:
            str: Detailed string showing all calculation attributes.
        """
        return (
            f"Calculation(operation='{self.operation}', "
            f"operand1={self.operand1}, "
            f"operand2={self.operand2}, "
            f"result={self.result}, "
            f"timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        """
        Check if two calculations are equal.

        Compares two Calculation instances to determine if they represent the same
        operation with identical operands and results.

        Args:
            other (object): Another calculation to compare with.

        Returns:
            bool: True if calculations are equal, False otherwise.
        """
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation and
            self.operand1 == other.operand1 and
            self.operand2 == other.operand2 and
            self.result == other.result
        )

    def format_result(self, precision: int = 10) -> str:
        """
        Format the calculation result with specified precision.

        This method formats the result to a fixed number of decimal places,
        removing any trailing zeros for a cleaner presentation.

        Args:
            precision (int, optional): Number of decimal places to show. Defaults to 10.

        Returns:
            str: Formatted string representation of the result.
        """
        try:
            # Remove trailing zeros and format to specified precision
            return str(self.result.normalize().quantize(
                Decimal('0.' + '0' * precision)
            ).normalize())
        except InvalidOperation:  # pragma: no cover
            return str(self.result)