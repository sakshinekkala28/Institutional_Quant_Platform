from pathlib import Path
import logging
import sys

class LogConfig:

    LOG_LEVEL = logging.INFO

    LOG_FORMAT = (
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )

    LOG_DIRECTORY = (
        Path("logs")
    )

class FileLogger:

    @staticmethod
    def create_file_handler():

        LogConfig.LOG_DIRECTORY.mkdir(
            exist_ok=True
        )

        file_handler = logging.FileHandler(

            LogConfig.LOG_DIRECTORY
            / "platform.log"

        )

        file_handler.setFormatter(

            logging.Formatter(
                LogConfig.LOG_FORMAT
            )

        )

        return file_handler
    
class ConsoleLogger:

    @staticmethod
    def create_console_handler():

        handler = logging.StreamHandler(
            sys.stdout
        )

        handler.setFormatter(

            logging.Formatter(
                LogConfig.LOG_FORMAT
            )

        )

        return handler
    
class LoggingManager:

    @staticmethod
    def get_logger(name):

        logger = logging.getLogger(name)

        if logger.handlers:
            return logger

        logger.setLevel(
            LogConfig.LOG_LEVEL
        )

        logger.addHandler(

            FileLogger
            .create_file_handler()

        )

        logger.addHandler(

            ConsoleLogger
            .create_console_handler()

        )

        logger.propagate = False

        return logger