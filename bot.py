"""
Telegram Bot API Handler
Handles bot interactions via Bot API
"""
import asyncio
from telegram import Update, Message, ForceReply
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from config import settings
from logger import get_logger, LoggerMixin
from llm_manager import llm_manager
from database import db_manager
from cyberpunk_ui import ui

logger = get_logger(__name__)


class BotHandler(LoggerMixin):
    """Handles Telegram Bot API functionality"""
    
    def __init__(self):
        self.application: Application = None
        self.conversation_context = {}
        self.is_running = False
    
    async def start(self):
        """Initialize and start bot"""
        if not settings.enable_bot:
            self.logger.info("Bot API is disabled in config")
            return
        
        if not settings.bot_token:
            self.logger.error("Bot token missing in .env file")
            return
        
        try:
            self.logger.info("Initializing Telegram Bot API...")
            
            # Create application
            self.application = Application.builder().token(settings.bot_token).build()
            
            # Register handlers
            self._register_handlers()
            
            # Initialize and start
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)
            
            bot_info = await self.application.bot.get_me()
            self.logger.info(f"Bot started successfully: @{bot_info.username} ({bot_info.id})")
            self.is_running = True
            
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}", exc_info=True)
    
    def _register_handlers(self):
        """Register command and message handlers"""
        app = self.application
        
        # Commands
        app.add_handler(CommandHandler("start", self._cmd_start))
        app.add_handler(CommandHandler("help", self._cmd_help))
        app.add_handler(CommandHandler("h3lp", self._cmd_help))  # Leet version
        app.add_handler(CommandHandler("search", self._cmd_search))
        app.add_handler(CommandHandler("s34rch", self._cmd_search))  # Leet version
        app.add_handler(CommandHandler("channels", self._cmd_channels))
        app.add_handler(CommandHandler("ch4nn3ls", self._cmd_channels))  # Leet version
        app.add_handler(CommandHandler("suggest", self._cmd_suggest))
        app.add_handler(CommandHandler("clear", self._cmd_clear))
        app.add_handler(CommandHandler("stats", self._cmd_stats))
        
        # Admin commands
        app.add_handler(CommandHandler("status", self._cmd_status, filters=filters.User(settings.admin_ids)))
        app.add_handler(CommandHandler("addchannel", self._cmd_add_channel, filters=filters.User(settings.admin_ids)))
        app.add_handler(CommandHandler("listchannels", self._cmd_list_channels, filters=filters.User(settings.admin_ids)))
        app.add_handler(CommandHandler("removechannel", self._cmd_remove_channel, filters=filters.User(settings.admin_ids)))
        app.add_handler(CommandHandler("suggestions", self._cmd_list_suggestions, filters=filters.User(settings.admin_ids)))
        app.add_handler(CommandHandler("approve", self._cmd_approve, filters=filters.User(settings.admin_ids)))
        app.add_handler(CommandHandler("reject", self._cmd_reject, filters=filters.User(settings.admin_ids)))
        app.add_handler(CommandHandler("setprovider", self._cmd_set_provider, filters=filters.User(settings.admin_ids)))
        app.add_handler(CommandHandler("indexchannel", self._cmd_index_channel, filters=filters.User(settings.admin_ids)))
        app.add_handler(CommandHandler("indexall", self._cmd_index_all, filters=filters.User(settings.admin_ids)))
        
        # Message handlers
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        app.add_handler(MessageHandler(filters.FORWARDED, self._handle_forwarded))
    
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        self.logger.info(f"User {user.id} started bot")

        # Send cyberpunk welcome message
        welcome = ui.create_welcome_message(user.first_name or user.username)
        await update.message.reply_text(f"```\n{welcome}\n```", parse_mode='Markdown')
    
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
╔══════════════════════════════════════╗
║      [[ C0MM4ND R3F3R3NC3 ]]        ║
╚══════════════════════════════════════╝

┏━━ USER COMMANDS ━━━━━━━━━━━━━━━━━━┓
┃
┃  /start      » Initialize system
┃  /help       » Display this menu
┃  /search     » Search indexed content
┃  /channels   » List curated feeds
┃  /stats      » Display statistics
┃  /suggest    » Submit new channel
┃  /clear      » Wipe conversation
┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━ LEET ALIASES ━━━━━━━━━━━━━━━━━━┓
┃
┃  /h3lp       » Same as /help
┃  /s34rch     » Same as /search
┃  /ch4nn3ls   » Same as /channels
┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

> You can also just send messages directly
> LLM will process and respond

[SYSTEM READY]
"""
        await update.message.reply_text(f"```\n{help_text}\n```", parse_mode='Markdown')
    
    async def _cmd_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show curated channels"""
        channels = db_manager.get_curated_channels()
        
        if not channels:
            await update.message.reply_text("هنوز کانالی اضافه نشده است.")
            return
        
        text = "📚 **کانال‌های آموزشی پیشنهادی**\n\n"
        for ch in channels[:15]:
            text += f"🔹 **{ch.title}**\n"
            if ch.username:
                text += f"   @{ch.username}\n"
            if ch.description:
                text += f"   {ch.description[:100]}\n"
            if ch.topics:
                text += f"   🏷 {', '.join(ch.topics[:3])}\n"
            if ch.level:
                text += f"   📊 سطح: {ch.level}\n"
            text += "\n"
        
        if len(channels) > 15:
            text += f"\n... و {len(channels) - 15} کانال دیگر"
        
        await update.message.reply_text(text)
    
    async def _cmd_suggest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle channel suggestion"""
        await update.message.reply_text(
            "لطفاً یک پیام از کانال مورد نظر را فوروارد کنید یا لینک کانال را بفرستید.\n"
            "اگر می‌خواهید توضیح اضافه کنید، بعد از فوروارد بنویسید."
        )
    
    async def _cmd_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear conversation context"""
        user_id = update.effective_user.id
        if user_id in self.conversation_context:
            self.conversation_context[user_id] = []
        await update.message.reply_text("```\n> M3M0RY W1P3D\n> C0NT3XT CL34R3D\n> R34DY F0R N3W 1NPU7\n```", parse_mode='Markdown')

    async def _cmd_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Search indexed channel content"""
        if not context.args:
            await update.message.reply_text(
                "```\n> Usage: /search <query>\n> Example: /search python tutorial\n```",
                parse_mode='Markdown'
            )
            return

        query = ' '.join(context.args)
        self.logger.info(f"User {update.effective_user.id} searching: {query}")

        # Show loading message
        loading_msg = await update.message.reply_text(
            f"```\n{ui.create_loading_message('Searching database')}\n```",
            parse_mode='Markdown'
        )

        try:
            # Search in database
            results = db_manager.search_messages(query, limit=10)

            if not results:
                await loading_msg.edit_text(
                    f"```\n> N0 R3SU£75 F0UND\n> Try different keywords\n```",
                    parse_mode='Markdown'
                )
                return

            # Format results
            response = ui.create_search_header()
            response += f"\n> Found {len(results)} results for: {query}\n\n"

            for idx, result in enumerate(results, 1):
                # Get channel info
                channels = db_manager.get_curated_channels()
                channel_name = "Unknown"
                for ch in channels:
                    if ch.channel_id == result.channel_id:
                        channel_name = ch.title
                        break

                date_str = result.date.strftime("%Y-%m-%d") if result.date else None

                response += ui.format_search_result(
                    idx,
                    channel_name,
                    result.text,
                    date_str
                )

            # Split if too long
            if len(response) > 4000:
                chunks = [response[i:i+3900] for i in range(0, len(response), 3900)]
                await loading_msg.edit_text(f"```\n{chunks[0]}\n```", parse_mode='Markdown')
                for chunk in chunks[1:]:
                    await update.message.reply_text(f"```\n{chunk}\n```", parse_mode='Markdown')
            else:
                await loading_msg.edit_text(f"```\n{response}\n```", parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Search error: {e}", exc_info=True)
            await loading_msg.edit_text(
                f"```\n> 3RR0R: Search failed\n> {str(e)[:50]}\n```",
                parse_mode='Markdown'
            )

    async def _cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user statistics"""
        try:
            # Get statistics
            total_channels = len(db_manager.get_curated_channels())

            stats = {
                'INDEXED_CHANNELS': total_channels,
                'CONVERSATIONS': len(self.conversation_context),
                'YOUR_MESSAGES': len(self.conversation_context.get(update.effective_user.id, [])),
                'STATUS': 'ONLINE',
            }

            stats_display = ui.create_stats_display(stats)

            await update.message.reply_text(f"```\n{stats_display}\n```", parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Stats error: {e}", exc_info=True)
            await update.message.reply_text(f"```\n> 3RR0R: Cannot load stats\n```", parse_mode='Markdown')
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user = update.effective_user
        message_text = update.message.text
        
        self.logger.info(f"Message from {user.id}: {message_text[:100]}")
        
        # Get or create conversation context
        user_id = user.id
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = []
        
        # Add user message
        self.conversation_context[user_id].append({
            'role': 'user',
            'content': message_text
        })
        
        # Keep only last 20 messages
        if len(self.conversation_context[user_id]) > 40:
            self.conversation_context[user_id] = self.conversation_context[user_id][-40:]
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        try:
            # Generate response
            self.logger.debug("Generating LLM response...")
            response = await llm_manager.generate_response(
                user_message=message_text,
                conversation_history=self.conversation_context[user_id][:-1]
            )
            
            # Add assistant response
            self.conversation_context[user_id].append({
                'role': 'assistant',
                'content': response
            })
            
            # Send response (split if too long)
            if len(response) > 4000:
                # Split into chunks
                chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(response)
            
            self.logger.info(f"Sent response to {user.id}: {len(response)} chars")
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}", exc_info=True)
            await update.message.reply_text("متأسفم، در پردازش پیام مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")
    
    async def _handle_forwarded(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle forwarded messages (for channel suggestions)"""
        user = update.effective_user
        message = update.message
        
        if not message.forward_from_chat:
            return
        
        chat = message.forward_from_chat
        
        if chat.type in ['channel', 'supergroup']:
            # User is suggesting a channel
            channel_id = str(chat.id)
            title = chat.title
            username = chat.username
            
            # Add to suggestions
            db_manager.add_suggestion(
                channel_id=channel_id,
                username=username,
                title=title,
                suggested_by=user.id,
                reason=message.caption or None
            )
            
            await update.message.reply_text(
                f"✅ کانال **{title}** به لیست پیشنهادات اضافه شد.\n"
                f"پس از بررسی توسط ادمین‌ها، به لیست کانال‌های آموزشی اضافه خواهد شد."
            )
            
            self.logger.info(f"User {user.id} suggested channel: {title} ({channel_id})")
    
    # Admin commands
    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot status"""
        from config import runtime_config
        
        providers = llm_manager.list_providers()
        current_provider = runtime_config.get('current_llm_provider')
        
        status = f"""🤖 **وضعیت PushTutor Bot**

✅ Bot API: Active
🧠 LLM Provider: {current_provider}
📊 Available Providers: {', '.join(providers)}
💾 Database: Connected
🗂 Curated Channels: {len(db_manager.get_curated_channels())}
📝 Pending Suggestions: {len(db_manager.get_pending_suggestions())}
👥 Active Conversations: {len(self.conversation_context)}
"""
        await update.message.reply_text(status)
    
    async def _cmd_add_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add channel (admin only)"""
        if not update.message.reply_to_message or not update.message.reply_to_message.forward_from_chat:
            await update.message.reply_text("لطفاً روی یک پیام فوروارد‌شده از کانال reply کنید.")
            return
        
        chat = update.message.reply_to_message.forward_from_chat
        channel_id = str(chat.id)
        title = chat.title
        username = chat.username
        
        # Parse metadata from command
        args = ' '.join(context.args) if context.args else ""
        
        db_manager.add_curated_channel(
            channel_id=channel_id,
            title=title,
            username=username,
            added_by=update.effective_user.id,
            description=args if args else None
        )
        
        await update.message.reply_text(f"✅ کانال **{title}** به لیست اضافه شد.")
    
    async def _cmd_list_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List curated channels (admin)"""
        channels = db_manager.get_curated_channels()
        
        if not channels:
            await update.message.reply_text("هیچ کانالی در لیست نیست.")
            return
        
        text = "📚 **لیست کامل کانال‌های آموزشی**\n\n"
        for ch in channels:
            text += f"🔹 **{ch.title}**\n"
            text += f"   ID: `{ch.channel_id}`\n"
            if ch.username:
                text += f"   @{ch.username}\n"
            if ch.topics:
                text += f"   Topics: {', '.join(ch.topics)}\n"
            text += "\n"
            
            # Send in chunks if too long
            if len(text) > 3500:
                await update.message.reply_text(text)
                text = ""
        
        if text:
            await update.message.reply_text(text)
    
    async def _cmd_remove_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove channel (admin)"""
        if not context.args:
            await update.message.reply_text("Usage: /removechannel <channel_id>")
            return
        
        channel_id = context.args[0]
        if db_manager.remove_curated_channel(channel_id):
            await update.message.reply_text(f"✅ کانال {channel_id} حذف شد.")
        else:
            await update.message.reply_text(f"❌ کانال پیدا نشد.")
    
    async def _cmd_list_suggestions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List pending suggestions (admin)"""
        suggestions = db_manager.get_pending_suggestions()
        
        if not suggestions:
            await update.message.reply_text("پیشنهادی در صف نیست.")
            return
        
        text = "📋 **پیشنهادات در انتظار**\n\n"
        for sug in suggestions:
            text += f"🆔 ID: {sug.id}\n"
            text += f"📢 {sug.title or sug.channel_id}\n"
            text += f"👤 User: {sug.suggested_by}\n"
            if sug.reason:
                text += f"💬 {sug.reason}\n"
            text += "\n"
        
        text += "\n/approve <id> - تایید\n/reject <id> - رد"
        await update.message.reply_text(text)
    
    async def _cmd_approve(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Approve suggestion (admin)"""
        if not context.args:
            await update.message.reply_text("Usage: /approve <suggestion_id>")
            return
        
        try:
            suggestion_id = int(context.args[0])
            if db_manager.approve_suggestion(suggestion_id, update.effective_user.id):
                await update.message.reply_text(f"✅ پیشنهاد {suggestion_id} تایید شد.")
            else:
                await update.message.reply_text("❌ پیشنهاد پیدا نشد.")
        except ValueError:
            await update.message.reply_text("❌ ID نامعتبر")
    
    async def _cmd_reject(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reject suggestion (admin)"""
        if not context.args:
            await update.message.reply_text("Usage: /reject <suggestion_id> [note]")
            return
        
        try:
            suggestion_id = int(context.args[0])
            note = ' '.join(context.args[1:]) if len(context.args) > 1 else None
            
            if db_manager.reject_suggestion(suggestion_id, update.effective_user.id, note):
                await update.message.reply_text(f"✅ پیشنهاد {suggestion_id} رد شد.")
            else:
                await update.message.reply_text("❌ پیشنهاد پیدا نشد.")
        except ValueError:
            await update.message.reply_text("❌ ID نامعتبر")
    
    async def _cmd_set_provider(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set LLM provider (admin)"""
        if not context.args:
            providers = llm_manager.list_providers()
            await update.message.reply_text(f"Usage: /setprovider <provider>\nAvailable: {', '.join(providers)}")
            return

        from config import runtime_config
        provider = context.args[0].lower()
        available = llm_manager.list_providers()

        if provider in available:
            runtime_config.set('current_llm_provider', provider)
            await update.message.reply_text(f"✅ Provider changed to {provider}")
        else:
            await update.message.reply_text(f"❌ Invalid provider. Available: {', '.join(available)}")

    async def _cmd_index_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Index a specific channel (admin)"""
        if not context.args:
            await update.message.reply_text("Usage: /indexchannel <channel_id> [limit]")
            return

        from channel_indexer import channel_indexer

        if not channel_indexer:
            await update.message.reply_text("❌ Channel indexer not initialized")
            return

        channel_id = context.args[0]
        limit = int(context.args[1]) if len(context.args) > 1 else 1000

        progress_msg = await update.message.reply_text(
            f"```\n{ui.create_loading_message(f'Indexing {channel_id}')}\n```",
            parse_mode='Markdown'
        )

        try:
            result = await channel_indexer.index_channel(channel_id, limit=limit)

            if result.get('success'):
                stats = ui.create_stats_display({
                    'CHANNEL': result.get('channel_title', channel_id),
                    'INDEXED': result.get('messages_indexed', 0),
                    'UPDATED': result.get('messages_updated', 0),
                    'SKIPPED': result.get('messages_skipped', 0),
                    'TOTAL': result.get('total_processed', 0),
                })
                await progress_msg.edit_text(f"```\n{stats}\n```", parse_mode='Markdown')
            else:
                await progress_msg.edit_text(
                    f"```\n> 3RR0R: {result.get('error', 'Unknown error')}\n```",
                    parse_mode='Markdown'
                )

        except Exception as e:
            self.logger.error(f"Indexing error: {e}", exc_info=True)
            await progress_msg.edit_text(
                f"```\n> 3RR0R: {str(e)[:100]}\n```",
                parse_mode='Markdown'
            )

    async def _cmd_index_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Index all curated channels (admin)"""
        from channel_indexer import channel_indexer

        if not channel_indexer:
            await update.message.reply_text("❌ Channel indexer not initialized")
            return

        limit = int(context.args[0]) if context.args else 500

        progress_msg = await update.message.reply_text(
            f"```\n{ui.create_loading_message('Indexing all channels')}\n```",
            parse_mode='Markdown'
        )

        try:
            results = await channel_indexer.index_all_curated_channels(limit_per_channel=limit)

            # Summarize results
            total_indexed = sum(r.get('messages_indexed', 0) for r in results if r.get('success'))
            total_updated = sum(r.get('messages_updated', 0) for r in results if r.get('success'))
            channels_processed = len([r for r in results if r.get('success')])
            channels_failed = len([r for r in results if not r.get('success')])

            stats = ui.create_stats_display({
                'CHANNELS_PROCESSED': channels_processed,
                'CHANNELS_FAILED': channels_failed,
                'MESSAGES_INDEXED': total_indexed,
                'MESSAGES_UPDATED': total_updated,
                'TOTAL_MESSAGES': total_indexed + total_updated,
            })

            await progress_msg.edit_text(f"```\n{stats}\n```", parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Index all error: {e}", exc_info=True)
            await progress_msg.edit_text(
                f"```\n> 3RR0R: {str(e)[:100]}\n```",
                parse_mode='Markdown'
            )
    
    async def stop(self):
        """Stop bot"""
        if self.application:
            self.logger.info("Stopping bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            self.is_running = False
            self.logger.info("Bot stopped")


# Global bot instance
bot = BotHandler()
