from unittest.mock import patch
from app.exceptions import ConfigurationError
from main import main


def test_main_handles_invalid_configuration(capsys):
    with patch(
        "main.CalculatorConfig",
        side_effect=ConfigurationError("Invalid precision")
    ):
        result = main()

    captured = capsys.readouterr()

    assert result == 1
    assert "Configuration error" in captured.err
    assert "Invalid precision" in captured.err