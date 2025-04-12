"""Error handling module for TeleGraphite.

This module provides custom exceptions and error handling utilities.
"""

import logging
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic function return type
T = TypeVar('T')


class TeleGraphiteError(Exception):
    """Base exception class for TeleGraphite."""
    pass


class ConfigurationError(TeleGraphiteError):
    """Raised when there is an error in the configuration."""
    pass


class AuthenticationError(TeleGraphiteError):
    """Raised when there is an error with Telegram authentication."""
    pass


class FetchError(TeleGraphiteError):
    """Raised when there is an error fetching posts from Telegram."""
    pass


class StorageError(TeleGraphiteError):
    """Raised when there is an error storing posts or media."""
    pass


def handle_errors(default_return: Optional[Any] = None) -> Callable:
    """Decorator to handle exceptions in functions.
    
    Args:
        default_return: Value to return if an exception occurs.
        
    Returns:
        Decorated function that handles exceptions.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                return default_return
        return wrapper
    return decorator


async def handle_async_errors(func: Callable, *args, **kwargs) -> Any:
    """Handle exceptions in async functions.
    
    Args:
        func: Async function to execute.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.
        
    Returns:
        Result of the function or None if an exception occurs.
        
    Raises:
        Exception: Re-raises any exception that occurs during execution.
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in async function {func.__name__}: {str(e)}")
        raise