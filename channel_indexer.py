"""
Channel Message Indexer - Scrapes and indexes channel content
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from telethon import TelegramClient
from telethon.tl.types import Channel, Message

from logger import get_logger, LoggerMixin
from database import db_manager
from config import settings

logger = get_logger(__name__)


class ChannelIndexer(LoggerMixin):
    """Indexes messages from Telegram channels for search"""

    def __init__(self, client: TelegramClient):
        self.client = client
        self.is_running = False

    async def index_channel(self, channel_id: str, limit: int = 1000,
                           offset_date: datetime = None) -> dict:
        """
        Index messages from a channel

        Args:
            channel_id: Channel ID or username
            limit: Maximum number of messages to fetch
            offset_date: Start from this date (None = from latest)

        Returns:
            Statistics dict
        """
        try:
            self.logger.info(f"Starting to index channel: {channel_id}")

            # Get channel entity
            channel = await self.client.get_entity(channel_id)

            if not isinstance(channel, Channel):
                self.logger.error(f"{channel_id} is not a channel")
                return {'success': False, 'error': 'Not a channel'}

            # Fetch messages
            messages_indexed = 0
            messages_skipped = 0
            messages_updated = 0

            async for message in self.client.iter_messages(
                channel,
                limit=limit,
                offset_date=offset_date,
                reverse=False  # Start from newest
            ):
                if not isinstance(message, Message):
                    continue

                # Extract message data
                message_data = self._extract_message_data(message, channel_id)

                if message_data:
                    # Add to database
                    db_message = db_manager.add_message(**message_data)

                    if db_message:
                        if db_message.last_updated > db_message.indexed_at:
                            messages_updated += 1
                        else:
                            messages_indexed += 1
                    else:
                        messages_skipped += 1

                # Avoid rate limiting
                if (messages_indexed + messages_updated) % 100 == 0:
                    self.logger.info(f"Indexed {messages_indexed} messages, updated {messages_updated}")
                    await asyncio.sleep(1)

            stats = {
                'success': True,
                'channel_id': channel_id,
                'channel_title': channel.title,
                'messages_indexed': messages_indexed,
                'messages_updated': messages_updated,
                'messages_skipped': messages_skipped,
                'total_processed': messages_indexed + messages_updated + messages_skipped,
            }

            self.logger.info(f"Indexing complete for {channel_id}: {stats}")
            return stats

        except Exception as e:
            self.logger.error(f"Error indexing channel {channel_id}: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _extract_message_data(self, message: Message, channel_id: str) -> Optional[dict]:
        """Extract relevant data from a message"""
        try:
            # Skip messages without text
            if not message.text or not message.text.strip():
                return None

            # Extract media info
            has_media = message.media is not None
            media_type = None
            if has_media:
                if message.photo:
                    media_type = 'photo'
                elif message.video:
                    media_type = 'video'
                elif message.document:
                    media_type = 'document'

            return {
                'channel_id': str(channel_id),
                'message_id': message.id,
                'text': message.text,
                'date': message.date,
                'views': message.views or 0,
                'forwards': message.forwards or 0,
                'has_media': has_media,
                'media_type': media_type,
            }

        except Exception as e:
            self.logger.error(f"Error extracting message data: {e}")
            return None

    async def index_all_curated_channels(self, limit_per_channel: int = 1000) -> List[dict]:
        """Index all curated channels"""
        channels = db_manager.get_curated_channels(active_only=True)

        self.logger.info(f"Indexing {len(channels)} curated channels...")

        results = []
        for channel in channels:
            result = await self.index_channel(
                channel.channel_id,
                limit=limit_per_channel
            )
            results.append(result)

            # Sleep between channels to avoid rate limiting
            await asyncio.sleep(3)

        return results

    async def update_channel_index(self, channel_id: str, days: int = 7) -> dict:
        """Update index for a channel (only recent messages)"""
        offset_date = datetime.utcnow() - timedelta(days=days)

        self.logger.info(f"Updating index for {channel_id} (last {days} days)")

        return await self.index_channel(
            channel_id,
            limit=500,
            offset_date=offset_date
        )

    async def run_periodic_update(self, interval_hours: int = 6):
        """Run periodic updates for all channels"""
        self.is_running = True
        self.logger.info(f"Starting periodic indexer (every {interval_hours} hours)")

        while self.is_running:
            try:
                channels = db_manager.get_curated_channels(active_only=True)

                for channel in channels:
                    if not self.is_running:
                        break

                    # Update recent messages
                    await self.update_channel_index(channel.channel_id, days=7)

                    # Sleep between channels
                    await asyncio.sleep(5)

                # Sleep until next run
                self.logger.info(f"Waiting {interval_hours} hours until next update")
                await asyncio.sleep(interval_hours * 3600)

            except Exception as e:
                self.logger.error(f"Error in periodic update: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute before retry

    def stop(self):
        """Stop periodic updates"""
        self.is_running = False
        self.logger.info("Stopping periodic indexer")


# Global indexer instance (will be initialized with client)
channel_indexer: Optional[ChannelIndexer] = None


def init_indexer(client: TelegramClient):
    """Initialize global indexer with Telegram client"""
    global channel_indexer
    channel_indexer = ChannelIndexer(client)
    return channel_indexer
