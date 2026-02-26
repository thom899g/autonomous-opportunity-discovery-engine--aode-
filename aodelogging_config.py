"""
Centralized logging configuration for AODE.
Architectural Rationale: Consistent logging format and level across all modules
enables effective debugging and system monitoring.
"""
import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Configure system-wide logging with proper formatting and handlers.
    
    Args:
        log_level: Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to file
        log_dir: Directory for log files
    
    Returns:
        Configured root logger
    """
    # Create log directory if needed
    if log_to_file:
        Path(log_dir).mkdir(exist_ok=True)
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(