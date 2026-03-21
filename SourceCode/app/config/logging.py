
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = (
	"%(asctime)s | %(levelname)s | %(name)s | "
	"%(filename)s:%(lineno)d | %(message)s"
)
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _parse_log_level(level_name: str) -> int:
	"""Convert a level name to `logging` level with safe fallback."""
	level = getattr(logging, level_name.upper(), None)
	if isinstance(level, int):
		return level
	return logging.INFO


def _build_file_handler(
	log_file: Path,
	level: int,
	log_format: str,
	date_format: str,
) -> RotatingFileHandler:
	"""Create a rotating file handler and ensure parent directory exists."""
	log_file.parent.mkdir(parents=True, exist_ok=True)
	handler = RotatingFileHandler(
		filename=log_file,
		maxBytes=5 * 1024 * 1024,
		backupCount=3,
		encoding="utf-8",
	)
	handler.setLevel(level)
	handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
	return handler


def setup_logging(
	*,
	log_level: Optional[str] = None,
	log_format: Optional[str] = None,
	date_format: Optional[str] = None,
	log_file: Optional[str] = None,
	enable_file_logging: Optional[bool] = None,
) -> None:
	"""Initialize application logging.

	Environment variables (optional):
	- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR/CRITICAL
	- `LOG_FORMAT`: Python logging format string
	- `LOG_DATE_FORMAT`: Date format for logs
	- `LOG_FILE`: path to log file (default: logs/app.log)
	- `LOG_TO_FILE`: true/false, 1/0, yes/no (default: true)
	"""
	level_name = log_level or os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)
	resolved_level = _parse_log_level(level_name)
	resolved_format = log_format or os.getenv("LOG_FORMAT", DEFAULT_LOG_FORMAT)
	resolved_date_format = date_format or os.getenv("LOG_DATE_FORMAT", DEFAULT_DATE_FORMAT)

	# Keep setup idempotent to avoid duplicate handlers when imported multiple times.
	root_logger = logging.getLogger()
	root_logger.setLevel(resolved_level)
	root_logger.handlers.clear()

	console_handler = logging.StreamHandler()
	console_handler.setLevel(resolved_level)
	console_handler.setFormatter(
		logging.Formatter(resolved_format, datefmt=resolved_date_format)
	)
	root_logger.addHandler(console_handler)

	if enable_file_logging is None:
		file_logging_env = os.getenv("LOG_TO_FILE", "true").strip().lower()
		file_logging_enabled = file_logging_env in {"1", "true", "yes", "on"}
	else:
		file_logging_enabled = enable_file_logging

	if file_logging_enabled:
		file_path = Path(log_file or os.getenv("LOG_FILE", "logs/app.log"))
		file_handler = _build_file_handler(
			log_file=file_path,
			level=resolved_level,
			log_format=resolved_format,
			date_format=resolved_date_format,
		)
		root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
	"""Return a logger instance with the provided name."""
	return logging.getLogger(name)
