import logging


def get_logger(sheet_title):
    logger = logging.getLogger("exampleApp")
    logger.setLevel(logging.INFO)

    # create the logging file handler
    fh = logging.FileHandler(f"{sheet_title.replace('/', '.')}.log")
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
