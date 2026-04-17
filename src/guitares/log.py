import logging

root_logger = logging.getLogger("guitares")


def init_logging():
    """Initialize logging for guitares."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def set_log_level(level):
    """Set the log level for all guitares loggers."""
    root_logger.setLevel(level)
