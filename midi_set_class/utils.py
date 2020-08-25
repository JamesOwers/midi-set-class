"""Utility functions."""
import logging


def log_and_raise(
    logger: logging.Logger,
    msg: str,
    logging_method: str = "error",
    ExceptionClass: Exception = ValueError,
) -> Exception:
    """Puts a message to the logger then raises an error with the same message.

    Args:
        logger: the logging logger to put the message to.
        msg: the message to log.
        logging_method: the method to call from the logger.
        ExceptionClass: the exception class to raise.

    Raises:
        Exception: of type ExceptionClass.
    """
    logging_function = getattr(logger, logging_method)
    logging_function(msg)
    raise ExceptionClass(msg)
