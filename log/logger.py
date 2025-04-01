import copy
import logging
import os

import colorama
from colorama import Fore, Style

# CONFIGURACOES PADROES
LOG_TO_FILE = True
LOG_FILE_PATH = "logs/app.log"
LOG_LEVEL = logging.DEBUG

# Inicializar colorama (necessário no Windows)
colorama.init()

# Adicionar nível SUCCESS personalizado
SUCCESS = 25
logging.addLevelName(SUCCESS, "SUCCESS")


class ColoredFormatter(logging.Formatter):
    """Formatter personalizado com cores para diferentes níveis de log"""

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.BLUE,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record):
        # Criar uma cópia do record para não afetar outros formatadores
        record_copy = copy.copy(record)
        levelname = record_copy.levelname
        if levelname in self.COLORS:
            record_copy.levelname = self.COLORS[levelname] + levelname + Style.RESET_ALL
        return super().format(record_copy)


class Logger:
    _instance = None
    # Inicializar com os valores padrão
    _log_to_file = LOG_TO_FILE
    _log_file_path = LOG_FILE_PATH
    _log_level = LOG_LEVEL

    def __new__(cls, name=__name__):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, name=__name__):
        if not hasattr(self, "_initialized") or not self._initialized:
            self._logger = logging.getLogger(name)
            self._logger.setLevel(Logger._log_level)

            # Limpar handlers existentes para evitar duplicação
            if self._logger.handlers:
                for handler in list(self._logger.handlers):
                    self._logger.removeHandler(handler)

            # Adicionar console handler com cores
            console_handler = logging.StreamHandler()
            color_formatter = ColoredFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(color_formatter)
            self._logger.addHandler(console_handler)

            # Adicionar file handler se configurado
            if Logger._log_to_file:
                # Criar o diretório de log se não existir
                log_dir = os.path.dirname(Logger._log_file_path)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)

                try:
                    # Criar o file handler com formatação SEM cores
                    file_handler = logging.FileHandler(Logger._log_file_path)
                    file_formatter = logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )
                    file_handler.setFormatter(file_formatter)
                    self._logger.addHandler(file_handler)
                    print(
                        f"Log será gravado em: {os.path.abspath(Logger._log_file_path)}"
                    )
                except Exception as e:
                    print(f"ERRO ao configurar log em arquivo: {e}")

            # Adicionar o método success
            def success(msg, *args, **kwargs):
                self._logger.log(SUCCESS, msg, *args, **kwargs)

            self._logger.success = success
            self._initialized = True

    @classmethod
    def configure(
        cls, log_to_file=LOG_TO_FILE, log_file_path=LOG_FILE_PATH, log_level=LOG_LEVEL
    ):
        """Configura as opções de logging antes de obter o logger"""
        cls._log_to_file = log_to_file
        cls._log_file_path = log_file_path
        cls._log_level = log_level

        # Resetar a instância para aplicar as novas configurações
        if cls._instance is not None:
            cls._instance._initialized = False

    @classmethod
    def get_logger(cls, name=__name__):
        return cls(name)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message):
        self._logger.error(message)

    def success(self, message):
        self._logger.success(message)

    def debug(self, message):
        self._logger.debug(message)

    def critical(self, message):
        self._logger.critical(message)
