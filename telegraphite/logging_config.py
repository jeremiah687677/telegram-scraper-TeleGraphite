"""
Logging configuration module for TeleGraphite.

This module provides centralized logging configuration for the application.
"""

import logging
from pathlib import Path
from typing import Optional


def configure_logging(verbose: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        verbose (bool): Whether to enable verbose (DEBUG) logging.
        log_file (Optional[str]): Optional path to a log file. If provided, logs will be written to this file
            in addition to the console.

    Returns:
        logging.Logger: The configured root logger.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    detailed_log_format = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create and add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)
    
    # Create file handlers if log_file is provided
    if log_file:
        log_path = Path(log_file)
        # Create directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler for detailed log output
        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(detailed_log_format))
        root_logger.addHandler(file_handler)
        
        # Error-specific file handler for ERROR and above messages
        error_log_path = log_path.with_name(f"{log_path.stem}_errors{log_path.suffix}")
        error_handler = logging.FileHandler(error_log_path, mode='a', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(detailed_log_format))
        root_logger.addHandler(error_handler)
    
    # Suppress verbose logging from third-party libraries
    logging.getLogger('telethon').setLevel(logging.INFO)
    logging.getLogger('asyncio').setLevel(logging.INFO)
    
    return root_logger


def configure_post_logger(log_dir: Optional[str] = None) -> logging.Logger:
    """
    Configure a specialized logger for tracking post fetching and media downloads.
    
    This creates a separate logger that tracks new posts, updates, and media downloads
    with channel-specific information.
    
    Args:
        log_dir (Optional[str]): Directory to store post logs. If None, logs will only be output to the console.
        
    Returns:
        logging.Logger: The configured post logger.
    """
    post_logger = logging.getLogger('telegraphite.posts')
    post_logger.setLevel(logging.INFO)
    
    post_log_format = "%(asctime)s - %(levelname)s - [%(channel)s] - %(message)s"
    post_formatter = logging.Formatter(post_log_format)
    
    # Remove any existing handlers to avoid duplicates
    for handler in post_logger.handlers[:]:
        post_logger.removeHandler(handler)
    
    # Create console handler for the post logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(post_formatter)
    post_logger.addHandler(console_handler)
    
    # Create file handlers if log_dir is provided
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Handler for logging all post-related messages
        posts_log_file = log_path / "posts.log"
        file_handler = logging.FileHandler(posts_log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(post_formatter)
        post_logger.addHandler(file_handler)
        
        # Handler for media-specific log messages only
        media_log_file = log_path / "media.log"
        media_handler = logging.FileHandler(media_log_file, mode='a', encoding='utf-8')
        media_handler.setLevel(logging.INFO)
        media_handler.setFormatter(post_formatter)
        media_handler.addFilter(lambda record: 'media' in record.getMessage().lower())
        post_logger.addHandler(media_handler)
    
    return post_logger
