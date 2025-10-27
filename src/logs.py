import logging


log_format = "%(asctime) %(module)"
date_format = "%Y-%m-%s"

def get_logger(module_name: str) -> logging.Logger:
    return logging.getLogger(module_name)
  
def configure_logging() -> None:
    logging.basicConfig(
        filename="test.log",
        filemode='w',
        format=log_format,
        datefmt=date_format,
        encoding='utf-8',
        level=logging.DEBUG,
    )