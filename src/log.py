import sys
from loguru import logger
from config import config

fmt_cli = "<level>{level: <8}</level> {message} <fg #00005f>{name}:{function} [{time:HH:mm:ss.SSS}]</fg #00005f>"
fmt_file = "[{time:HH:mm:ss.SSS}] {level: <8} {message} - {name}:{function}"
file_log = config.log.file.folder + config.log.file.name
logger.remove()

if config.log.cli.is_enabled:
    logger.add(sys.stderr, level=config.log.cli.level.upper(), format=fmt_cli)

if config.log.file.is_enabled:
    logger.add(file_log, level=config.log.file.level.upper(), format=fmt_file)