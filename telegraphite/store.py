"""Store module for TeleGraphite.

This module handles storing posts and media files from Telegram channels.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument

logger = logging.getLogger(__name__)


class PostStore:
    """Stores posts and media files from Telegram channels."""

    def __init__(self, data_dir: str = "data"):
        """Initialize the post store.

        Args:
            data_dir: Directory to store posts and media files.
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True, parents=True)

    def get_channel_dir(self, channel: str) -> Path:
        """Get the directory for a channel.

        Args:
            channel: The channel username.

        Returns:
            Path to the channel directory.
        """
        # Remove @ if present and create directory
        channel_name = channel.lstrip("@")
        channel_dir = self.data_dir / channel_name
        channel_dir.mkdir(exist_ok=True)
        return channel_dir

    def get_existing_post_ids(self, channel: str) -> Set[int]:
        """Get IDs of existing posts for a channel.

        Args:
            channel: The channel username.

        Returns:
            Set of existing post IDs.
        """
        channel_dir = self.get_channel_dir(channel)
        posts_file = channel_dir / "posts.json"
        
        if not posts_file.exists():
            return set()
        
        try:
            with open(posts_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
                return {post.get("post_id") for post in posts if post.get("post_id")}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading existing posts for {channel}: {e}")
            return set()
            
    def _validate_post(self, post: Dict[str, Any]) -> bool:
        """Validate that a post has all required fields.
        
        Args:
            post: The post dictionary to validate.
            
        Returns:
            True if the post is valid, False otherwise.
        """
        # Required fields for a valid post
        required_fields = ["post_id"]
        
        # Check required fields
        for field in required_fields:
            if field not in post or post[field] is None:
                logger.warning(f"Post missing required field: {field}")
                return False
                
        # Ensure post has a channel name
        if not (post.get("channel_name") or post.get("channel") or post.get("source_channel")):
            logger.warning("Post missing channel information")
            return False
            
        # If post doesn't have a timestamp, add current time
        if not post.get("timestamp"):
            post["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            
        # Calculate content hash if not present
        if not post.get("content_hash"):
            post["content_hash"] = self._calculate_content_hash(post)
            
        return True
        
    def _calculate_content_hash(self, post: Dict[str, Any]) -> str:
        """Calculate a hash of the post content for deduplication.
        
        Args:
            post: The post dictionary.
            
        Returns:
            A hash string representing the post content.
        """
        # Create a string with the most important content
        content_parts = []
        
        # Add text content if available
        if post.get("text"):
            content_parts.append(str(post["text"]).strip())
            
        # Add media paths if available
        if post.get("media"):
            for media in post["media"]:
                if media.get("path"):
                    content_parts.append(str(media["path"]).strip())
        elif post.get("image_paths"):
            for path in post["image_paths"]:
                content_parts.append(str(path).strip())
                
        # If no content parts, use post_id
        if not content_parts and post.get("post_id"):
            content_parts.append(str(post["post_id"]))
            
        # Join all parts and create hash
        content_string = "|".join(content_parts)
        return hashlib.md5(content_string.encode("utf-8")).hexdigest()

    def save_posts(self, posts: List[Dict]) -> bool:
        """Save posts to JSON files.

        Args:
            posts: List of post dictionaries.

        Returns:
            True if successful, False otherwise.
        """
        if not posts:
            return True

        # Group posts by channel
        posts_by_channel: Dict[str, List[Dict]] = {}
        for post in posts:
            # Support both old and new post structure
            channel = post.get("source_channel") or post.get("channel") or post.get("channel_name")
            if not channel:
                logger.warning(f"Skipping post without channel information: {post.get('post_id')}")
                continue
                
            # Normalize channel name (remove @ prefix)
            channel = channel.lstrip("@")
            
            # Ensure post has all required fields
            if not self._validate_post(post):
                logger.warning(f"Skipping invalid post for channel {channel}: {post.get('post_id')}")
                continue
                
            if channel not in posts_by_channel:
                posts_by_channel[channel] = []
            posts_by_channel[channel].append(post)

        # Save posts for each channel
        success = True
        for channel, channel_posts in posts_by_channel.items():
            channel_dir = self.get_channel_dir(channel)
            posts_file = channel_dir / "posts.json"
            
            # Load existing posts if any
            existing_posts = []
            if posts_file.exists():
                try:
                    with open(posts_file, "r", encoding="utf-8") as f:
                        existing_posts = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    logger.error(f"Error loading existing posts for {channel}: {e}")
                    logger.info(f"Creating new posts file for {channel}")
            
            # Enhanced deduplication: check by post_id and content hash
            existing_post_ids = {post.get("post_id") for post in existing_posts if post.get("post_id")}
            existing_content_hashes = {post.get("content_hash") for post in existing_posts if post.get("content_hash")}
            
            # Track how many new posts were added
            new_posts_count = 0
            updated_posts_count = 0
            
            for post in channel_posts:
                post_id = post.get("post_id")
                content_hash = post.get("content_hash")
                
                # Check if this is a new post or an update to an existing post
                is_new_post = post_id and post_id not in existing_post_ids
                is_duplicate_content = content_hash and content_hash in existing_content_hashes
                
                if is_new_post:
                    # Add new post
                    existing_posts.append(post)
                    existing_post_ids.add(post_id)
                    if content_hash:
                        existing_content_hashes.add(content_hash)
                    new_posts_count += 1
                    logger.debug(f"Added new post {post_id} for channel {channel}")
                elif not is_duplicate_content and post_id in existing_post_ids:
                    # Update existing post (content changed)
                    for i, existing_post in enumerate(existing_posts):
                        if existing_post.get("post_id") == post_id:
                            existing_posts[i] = post
                            updated_posts_count += 1
                            logger.debug(f"Updated existing post {post_id} for channel {channel}")
                            break
            
            # Save all posts
            try:
                with open(posts_file, "w", encoding="utf-8") as f:
                    json.dump(existing_posts, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {new_posts_count} new posts and updated {updated_posts_count} posts for channel {channel} (total: {len(existing_posts)})")
            except Exception as e:
                logger.error(f"Error saving posts for {channel}: {e}")
                success = False

        return success

    async def save_media(self, channel: str, message: Message) -> List[Dict]:
        """Save media files from a message.

        Args:
            channel: The channel username.
            message: The Telegram message.

        Returns:
            List of dictionaries containing media information including path and metadata.
        """
        if not message.media:
            return []

        # Normalize channel name (remove @ prefix)
        channel_name = channel.lstrip("@")
        channel_dir = self.get_channel_dir(channel_name)
        
        # Create year/month based directory structure for better organization
        date = message.date
        year_month_dir = f"{date.year:04d}/{date.month:02d}"
        media_dir = channel_dir / "media" / year_month_dir
        media_dir.mkdir(exist_ok=True, parents=True)

        saved_media = []
        try:
            # Generate a filename based on message ID and date
            date_str = date.strftime("%Y%m%d_%H%M%S")
            filename_base = f"{date_str}_{message.id}"
            
            # Download the media file
            if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
                file_path = media_dir / f"{filename_base}"
                downloaded_path = await message.download_media(file=str(file_path))
                
                if downloaded_path:
                    # Convert to relative path for storage
                    rel_path = os.path.relpath(downloaded_path, start=str(channel_dir))
                    abs_path = os.path.abspath(downloaded_path)
                    
                    # Add media metadata to make it easier for external applications
                    media_type = "photo" if isinstance(message.media, MessageMediaPhoto) else "document"
                    file_ext = os.path.splitext(downloaded_path)[1].lstrip('.')
                    file_size = os.path.getsize(downloaded_path) if os.path.exists(downloaded_path) else 0
                    
                    # Create a detailed media info dictionary
                    media_info = {
                        "path": rel_path,
                        "absolute_path": abs_path,
                        "type": media_type,
                        "format": file_ext,
                        "size": file_size,
                        "filename": os.path.basename(downloaded_path),
                        "timestamp": message.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "year": date.year,
                        "month": date.month,
                        "day": date.day,
                        "channel": channel_name,
                        "message_id": message.id,
                        "media_id": hashlib.md5(rel_path.encode("utf-8")).hexdigest()[:10]
                    }
                    
                    saved_media.append(media_info)
                    logger.info(f"Saved media from post {message.id} to {rel_path}")
                    logger.debug(f"Media details: type={media_type}, size={file_size} bytes, format={file_ext}")
        
        except Exception as e:
            logger.error(f"Error saving media for message {message.id}: {e}")
        
        return saved_media