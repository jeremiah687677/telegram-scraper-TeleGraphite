\"""Configuration module for TeleGraphite.

This module handles loading and validating configuration settings.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Union

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for TeleGraphite."""

    def __init__(
        self,
        config_file: Optional[str] = None,
        env_file: Optional[str] = None,
        data_dir: Optional[str] = None,
        channels_file: Optional[str] = None,
    ):
        """Initialize the configuration manager.

        Args:
            config_file: Path to the YAML configuration file.
            env_file: Path to the .env file with API credentials.
            data_dir: Directory to store posts and media.
            channels_file: Path to the file containing channel usernames.
        """
        self.config_file = config_file
        self.env_file = env_file or ".env"
        self.config = {}

        # Load configuration from file if provided
        if config_file and os.path.exists(config_file):
            self._load_config_file()

        # Load environment variables
        load_dotenv(self.env_file)

        # Override with provided values
        if data_dir:
            self.config["data_dir"] = data_dir
        if channels_file:
            self.config["channels_file"] = channels_file

        # Set defaults if not provided
        self.config.setdefault("data_dir", "data")
        self.config.setdefault("channels_file", "channels.txt")
        self.config.setdefault("limit", 10)
        self.config.setdefault("interval", 3600)
        
        # Filters defaults
        self.config.setdefault("filters", {})
        self.config.get("filters").setdefault("keywords", [])
        self.config.get("filters").setdefault("media_only", False)
        self.config.get("filters").setdefault("text_only", False)
        
        # Schedule defaults
        self.config.setdefault("schedule", {})
        self.config.get("schedule").setdefault("days", [])
        self.config.get("schedule").setdefault("times", [])

        # Validate configuration
        self._validate_config()

    def _load_config_file(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                file_config = yaml.safe_load(f)
                if file_config and isinstance(file_config, dict):
                    self.config.update(file_config)
                    logger.info(f"Loaded configuration from {self.config_file}")
                else:
                    logger.warning(f"Invalid configuration in {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration from {self.config_file}: {e}")

    def _validate_config(self) -> None:
        """Validate the configuration."""
        # Check API credentials
        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")

        if not api_id or not api_hash:
            logger.warning(
                "API_ID and API_HASH not found in environment variables. "
                "These are required for connecting to Telegram."
            )

        # Check channels file
        channels_file = self.get("channels_file")
        if not os.path.exists(channels_file):
            logger.warning(
                f"Channels file not found: {channels_file}. "
                "Create a text file with one channel username per line."
            )

        # Create data directory if it doesn't exist
        data_dir = Path(self.get("data_dir"))
        data_dir.mkdir(exist_ok=True, parents=True)

    def get(self, key: str, default: Optional[Union[str, int, bool]] = None) -> Union[str, int, bool]:
        """Get a configuration value.

        Args:
            key: The configuration key.
            default: Default value if key is not found.

        Returns:
            The configuration value.
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Union[str, int, bool]) -> None:
        """Set a configuration value.

        Args:
            key: The configuration key.
            value: The configuration value.
        """
        self.config[key] = value

    def as_dict(self) -> Dict[str, Union[str, int, bool]]:
        """Get the configuration as a dictionary.

        Returns:
            The configuration dictionary.
        """
        return self.config.copy()