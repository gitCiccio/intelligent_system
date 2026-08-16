import logging as l
from pathlib import Path

def setup_logger(name: str, log_file="logs/output.log", level=l.INFO):

    log = l.getLogger(name)
    log.setLevel(level)

    # avoiding calling this function twice
    if log.hasHandlers():
        log.handlers.clear()

    # creating the mask
    formatter = l.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # creating the StreamHandler
    console_handler = l.StreamHandler()
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler) # Attaching the handler to the logger

    # File handler
    if log_file:
        log_path = Path(log_file)
        # if dir logs doesn't exist we'll create it
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # even the file doesn't exist we'll create it, but the directory must exist now
        file_handler = l.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

    return log