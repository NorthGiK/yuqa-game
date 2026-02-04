import logging


log_format = "%(levelname)s: %(asctime)s `%(name)s` - %(message)s"
date_format = "%m/%d/%Y %I:%M:%S %p"


def get_logger(module_name: str) -> logging.Logger:
    return logging.getLogger(module_name)


def dev_configure() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
    )


def configure_logging() -> None:
    logging.basicConfig(
        filename="test.log",
        filemode="w",
        format=log_format,
        datefmt=date_format,
        encoding="utf-8",
        level=logging.DEBUG,
    )
