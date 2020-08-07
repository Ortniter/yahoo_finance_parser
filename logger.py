import logging
import os


class Logger:
    """
    Initialize the logger with a name and an optional level.
    """

    def __init__(self, name):
        if not os.path.exists('logs'):
            os.mkdir('logs')

        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

        fh = logging.FileHandler('logs/error.log')
        fh.setLevel(logging.ERROR)
        fh.setFormatter(formatter)
        self._logger.addHandler(fh)

        ch = logging.FileHandler(f'logs/{name}.log')
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        self._logger.addHandler(sh)

    def info(self, message: str):
        """
        Log 'message' with severity 'INFO'.
        """
        self._logger.info(message)

    def debug(self, message: str):
        """
        Log 'message' with severity 'DEBUG'.
        """
        self._logger.debug(message)

    def warning(self, message: str):
        """
        Log 'message' with severity 'WARNING'.
        """
        self._logger.warning(message)

    def error(self, message: str):
        """
        Log 'message' with severity 'ERROR'.
        """
        self._logger.error(message)

    def critical(self, message: str):
        """
        Log 'message' with severity 'CRITICAL'.
        """
        self._logger.critical(message)
