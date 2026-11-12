from unittest.mock import Mock

from app.logger import Logger

def test_warning():
    logger = Logger.__new__(Logger)
    logger.logger = Mock()
    message = "This is a warning message"
    logger.warning(message)
    logger.logger.warning.assert_called_once_with(message)

def test_error():
    logger = Logger.__new__(Logger)
    logger.logger = Mock()
    message = "This is an error message"
    logger.error(message)
    logger.logger.error.assert_called_once_with(message)

def test_info():
    logger = Logger.__new__(Logger)
    logger.logger = Mock()
    message = "This is an info message"
    logger.info(message)
    logger.logger.info.assert_called_once_with(message)

def test_log_exception():
    logger = Logger.__new__(Logger)
    logger.logger = Mock()
    message = "This is an exception message"
    logger.log_exception(message)
    logger.logger.exception.assert_called_once_with(message)