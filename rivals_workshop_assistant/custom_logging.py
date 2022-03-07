import sys
from pathlib import Path

from loguru import logger

from rivals_workshop_assistant.modes import Mode

from rivals_workshop_assistant.paths import ASSISTANT_FOLDER, LOGS_FOLDER

log_lines = []
has_encountered_error = False


def setup_logger(root_dir: Path):
    logger.add(
        root_dir / ASSISTANT_FOLDER / LOGS_FOLDER / f"assistant_{{time}}.log",
        retention="2 days",
        backtrace=True,
        diagnose=True,
    )
    logger.add(sys.stdout, level="WARNING")
    logger.add(lambda message: log_lines.append(message))
    logger.add(lambda _: set_encountered_error(), level="ERROR")


def set_encountered_error():
    global has_encountered_error
    has_encountered_error = True


def log_startup_context(version: str, exe_dir: Path, root_dir: Path, mode: Mode):
    version_message = f"Assistant Version: {version}"
    logger.info(version_message)
    print(version_message)  # So that it always displays in the editor console.
    logger.info(f"Exe dir: {exe_dir}")
    logger.info(f"Root dir: {root_dir}")
    logger.info(f"Mode: {mode.name}")
