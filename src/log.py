import sys
from loguru import logger

fmt = "<level>{level: <8}</level> {message} <fg #00005f>{name}:{function} [{time:HH:mm:ss.SSS}]</fg #00005f>"
logger.remove()
logger.add(sys.stderr, format=fmt)