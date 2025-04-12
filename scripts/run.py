#!/usr/bin/env python
"""
Run script for TeleGraphite.

This script provides a simple way to run the TeleGraphite tool.
It can be used to fetch posts from Telegram channels once or continuously.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path to allow importing telegraphite
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegraphite.cli import run_once, run_continuous, parse_args
from telegraphite.logging_config import configure_logging


def main():
    """Run the TeleGraphite tool."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch posts from Telegram channels")
    parser.add_argument(
        "mode",
        choices=["once", "continuous"],
        help="Run once or continuously with a specified interval",
    )
    parser.add_argument(
        "-c", "--channels-file", default="channels.txt", help="Path to file containing channel usernames"
    )
    parser.add_argument(
        "-d", "--data-dir", default="data", help="Directory to store posts and media"
    )
    parser.add_argument(
        "-e", "--env-file", default=".env", help="Path to .env file with API credentials"
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=10, help="Maximum number of posts to fetch per channel"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "-i", "--interval", type=int, default=3600, help="Interval between fetches in seconds (only for continuous mode)"
    )
    parser.add_argument(
        "--log-file", help="Path to log file"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logging(verbose=args.verbose, log_file=args.log_file)
    logger = logging.getLogger(__name__)
    
    try:
        if args.mode == "once":
            asyncio.run(run_once(args))
        elif args.mode == "continuous":
            asyncio.run(run_continuous(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()