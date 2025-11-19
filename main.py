"""
PushTutor - Main Entry Point
Runs both Userbot and Bot API simultaneously
"""
import asyncio
import signal
import sys
from pathlib import Path

from config import settings
from logger import setup_logging, get_logger
from database import db_manager
from userbot import userbot
from bot import bot
from channel_indexer import init_indexer


logger = get_logger(__name__)


class PushTutor:
    """Main application class"""
    
    def __init__(self):
        self.is_running = False
        self.tasks = []
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("=" * 80)
        logger.info("Initializing PushTutor Bot...")
        logger.info("=" * 80)
        
        # Setup database
        logger.info("Setting up database...")
        db_manager.create_tables()
        logger.info("Database ready")
        
        # Check configuration
        self._check_config()
        
        logger.info("Initialization complete")
    
    def _check_config(self):
        """Check and log configuration status"""
        logger.info("Configuration check:")
        logger.info(f"  - Userbot enabled: {settings.enable_userbot}")
        logger.info(f"  - Bot API enabled: {settings.enable_bot}")
        logger.info(f"  - Admin IDs: {settings.admin_ids}")
        logger.info(f"  - Default LLM: {settings.default_llm_provider}")
        
        # Check API keys
        if settings.gemini_api_key:
            logger.info("  - Gemini API: ✓ Configured")
        if settings.openai_api_key:
            logger.info("  - OpenAI API: ✓ Configured")
        if settings.openrouter_api_key:
            logger.info("  - OpenRouter API: ✓ Configured")
        
        if not any([settings.gemini_api_key, settings.openai_api_key, settings.openrouter_api_key]):
            logger.warning("  - No LLM API keys configured!")
        
        # Check Telegram credentials
        if settings.enable_userbot:
            if all([settings.telegram_api_id, settings.telegram_api_hash, settings.telegram_phone]):
                logger.info("  - Userbot credentials: ✓ Configured")
            else:
                logger.warning("  - Userbot credentials: ✗ Missing")
        
        if settings.enable_bot:
            if settings.bot_token:
                logger.info("  - Bot token: ✓ Configured")
            else:
                logger.warning("  - Bot token: ✗ Missing")
    
    async def start(self):
        """Start all components"""
        self.is_running = True
        logger.info("=" * 80)
        logger.info("Starting PushTutor Bot...")
        logger.info("=" * 80)
        
        # Start userbot
        if settings.enable_userbot:
            logger.info("Starting Telethon userbot...")
            try:
                await userbot.start()
                if userbot.is_running:
                    # Initialize channel indexer with userbot client
                    indexer = init_indexer(userbot.client)
                    logger.info("Channel indexer initialized")

                    # Create task for userbot
                    task = asyncio.create_task(userbot.run_until_disconnected())
                    self.tasks.append(task)
                    logger.info("Userbot task created")
            except Exception as e:
                logger.error(f"Failed to start userbot: {e}", exc_info=True)
        
        # Start bot
        if settings.enable_bot:
            logger.info("Starting Telegram Bot API...")
            try:
                await bot.start()
                if bot.is_running:
                    logger.info("Bot API started successfully")
            except Exception as e:
                logger.error(f"Failed to start bot: {e}", exc_info=True)
        
        if not self.tasks and not bot.is_running:
            logger.error("No components running! Check your configuration.")
            return False
        
        logger.info("=" * 80)
        logger.info("🚀 PushTutor is now running!")
        logger.info("=" * 80)
        
        return True
    
    async def stop(self):
        """Stop all components"""
        logger.info("=" * 80)
        logger.info("Shutting down PushTutor...")
        logger.info("=" * 80)
        
        self.is_running = False
        
        # Stop bot
        if bot.is_running:
            logger.info("Stopping bot...")
            await bot.stop()
        
        # Stop userbot
        if userbot.is_running:
            logger.info("Stopping userbot...")
            await userbot.stop()
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("=" * 80)
        logger.info("PushTutor stopped")
        logger.info("=" * 80)
    
    async def run(self):
        """Run the application"""
        await self.initialize()
        
        if not await self.start():
            logger.error("Failed to start application")
            return
        
        try:
            # Keep running
            if self.tasks:
                # If we have tasks (userbot), wait for them
                await asyncio.gather(*self.tasks)
            else:
                # If only bot is running, keep alive
                while self.is_running:
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
        finally:
            await self.stop()


def setup_signal_handlers(app: PushTutor):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        asyncio.create_task(app.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main entry point"""
    # Setup logging
    setup_logging(
        log_file=settings.log_file,
        log_level=settings.log_level
    )
    
    # Create application
    app = PushTutor()
    
    # Setup signal handlers
    setup_signal_handlers(app)
    
    # Run
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
