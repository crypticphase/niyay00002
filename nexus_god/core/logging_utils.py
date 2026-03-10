from __future__ import annotations

import logging
import threading
import traceback
from datetime import datetime
from pathlib import Path


def configure_logging(log_dir_name: str = "nexus_god_logs") -> Path:
    """Configure file logging and return the log file path."""
    log_dir = Path(log_dir_name)
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"nexus_log_{datetime.now().strftime('%Y%m%d')}.txt"

    # If logging is already configured, basicConfig is a no-op.
    logging.basicConfig(
        filename=str(log_file),
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )
    return log_file


def log_error(msg: str) -> None:
    logging.error(msg)
    print(f"ERROR: {msg}")


def log_debug(msg: str) -> None:
    logging.debug(msg)
    print(f"DEBUG: {msg}")


def log_info(msg: str) -> None:
    logging.info(msg)
    print(f"INFO: {msg}")


def _thread_exception_handler(args: threading.ExceptHookArgs) -> None:
    err_msg = "".join(
        traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)
    )
    log_error(f"Thread Exception: {err_msg}")


def install_thread_excepthook() -> None:
    """Install a global exception hook for background threads."""
    threading.excepthook = _thread_exception_handler
