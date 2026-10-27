import logging
import os
import sys

from harness import config


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",     # cyan
    logging.INFO: "\033[32m",      # green
    logging.WARNING: "\033[33m",   # yellow
    logging.ERROR: "\033[31m",     # red
    logging.CRITICAL: "\033[1;41m",  # bold on red background
}


class ColorFormatter(logging.Formatter):
    def __init__(self, use_color: bool) -> None:
        super().__init__(datefmt="%H:%M:%S")
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        time = self.formatTime(record, self.datefmt)
        level = f"{record.levelname:<8}"
        name = record.name
        message = record.getMessage()

        if self.use_color:
            color = LEVEL_COLORS.get(record.levelno, "")
            time = f"{DIM}{time}{RESET}"
            level = f"{color}{BOLD}{level}{RESET}"
            name = f"{DIM}{name}{RESET}"
            if record.levelno >= logging.WARNING:
                message = f"{color}{message}{RESET}"

        line = f"{time} {level} {name}: {message}"
        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        return line


def configure_logging() -> None:
    use_color = sys.stderr.isatty() and os.environ.get("NO_COLOR") is None
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(ColorFormatter(use_color))

    root = logging.getLogger()
    root.setLevel(config.LOG_LEVEL)
    root.handlers.clear()
    root.addHandler(handler)

    # Silence noisy HTTP libraries used by the anthropic client
    for name in ("httpx", "httpx2", "httpcore", "httpcore2", "anthropic"):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
