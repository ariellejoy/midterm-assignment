########################
# Input Validation     #
########################

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

@dataclass
class InputValidator:
    """Validates and sanitizes calculator inputs."""

    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        """
        Validate and convert input to Decimal.

        Args:
            value: Input value to validate.
            config: Calculator configuration.

        Returns:
            Decimal: Validated and normalized number.

        Raises:
            ValidationError: If input is invalid.
        """

        # Check for missing input
        if value is None:
            raise ValidationError("Input cannot be empty.")

        try:
            # Convert input to a string and remove whitespace
            value = str(value).strip()

            # Check for empty strings
            if not value:
                raise ValidationError("Input cannot be empty. Please enter a number.")

            # Convert input to Decimal
            number = Decimal(value)

            # Reject NaN and Infinity
            if not number.is_finite():
                raise ValidationError("Input must be a finite number.")

            # Check maximum permitted input value
            if abs(number) > config.max_input_value:
                raise ValidationError(
                    f"Value exceeds maximum allowed: {config.max_input_value}"
                )

            # Return normalized Decimal
            return number.normalize()

        except ValidationError:
            # Preserve validation errors without changing their messages
            raise

        except (InvalidOperation, TypeError, ValueError) as e:
            # Convert unexpected conversion errors into ValidationError
            raise ValidationError(
                f"Invalid number format: {value}"
            ) from e
