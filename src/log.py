import sys
from config import LogConfig, CliLogConfig, FileLogConfig

from loguru import logger


class LoggerConfigurator():
    
    @classmethod
    def configure(cls, config: LogConfig):
        cls._delete_default()
        if config.cli.is_enabled:
            cls._add_cli(config.cli)
        if config.file.is_enabled:
            cls._add_file(config.file)

    @staticmethod
    def _delete_default():
        logger.remove()
    
    @staticmethod
    def _add_cli(cli_config: CliLogConfig):
        fmt_cli = "<level>{level: <8}</level> {message} <fg #00005f>{name}:{function} [{time:HH:mm:ss.SSS}]</fg #00005f>"
        logger.add(sys.stderr, level=cli_config.level.upper(), format=fmt_cli)
    
    @staticmethod
    def _add_file(file_config: FileLogConfig):
        fmt_file = "[{time:HH:mm:ss.SSS}] {level: <8} {message} - {name}:{function}"
        file_log = file_config.folder + file_config.name
        logger.add(
            file_log,
            level = file_config.level.upper(),
            format = fmt_file,
            rotation = file_config.rotation,
            retention = file_config.retention
        )
