import logging
from logging.handlers import TimedRotatingFileHandler # <-- Importação nova aqui!
import os
from pathlib import Path


DIRETORIO_ATUAL = Path(__file__).parent


def configurar_logger():
    diretorio_raiz = DIRETORIO_ATUAL.parent
    pasta_logs = diretorio_raiz / "logs"

    if not pasta_logs.exists():
        os.makedirs(pasta_logs)

    logger = logging.getLogger("WhatsAppBot")
    logger.setLevel(logging.INFO) 

    if not logger.handlers:
        formato = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formato)

        arquivo_handler = TimedRotatingFileHandler(
            filename="logs/bot.log", 
            when="midnight", 
            interval=1, 
            backupCount=30, 
            encoding="utf-8"
        )

        arquivo_handler.setFormatter(formato)

        logger.addHandler(console_handler)
        logger.addHandler(arquivo_handler)

    return logger

logger = configurar_logger()