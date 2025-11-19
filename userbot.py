"""
Telethon Userbot Handler
Handles user account interactions in groups/channels
"""
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Message, User, Channel

from config import settings
from logger import get_logger, LoggerMixin
from llm_manager import llm_manager
from database import db_manager

logger = get_logger(__name__)


class UserbotHandler(LoggerMixin):
    """Handles Telethon userbot functionality"""
    
    def __init__(self):
        self.client: TelegramClient = None
        self.conversation_context = {}  # Store conversation history per chat
        self.is_running = False
    
    async def start(self):
        """Initialize and start userbot"""
        if not settings.enable_userbot:
            self.logger.info("Userbot is disabled in config")
            return
        
        if not all([settings.telegram_api_id, settings.telegram_api_hash, settings.telegram_phone]):
            self.logger.error("Userbot credentials missing in .env file")
            return
        
        try:
            self.logger.info("Initializing Telethon userbot...")
            
            self.client = TelegramClient(
                'userbot_session',
                settings.telegram_api_id,
                settings.telegram_api_hash
            )
            
            # Register event handlers
            self._register_handlers()
            
            await self.client.start(phone=settings.telegram_phone)
            
            me = await self.client.get_me()
            self.logger.info(f"Userbot started successfully: @{me.username} ({me.id})")
            self.is_running = True
            
        except Exception as e:
            self.logger.error(f"Failed to start userbot: {e}", exc_info=True)
    
    def _register_handlers(self):
        """Register event handlers"""
        # Handle incoming messages mentioning the bot
        @self.client.on(events.NewMessage(incoming=True, func=lambda e: self._should_respond(e)))
        async def handle_message(event: events.NewMessage.Event):
            try:
                await self._handle_incoming_message(event)
            except Exception as e:
                self.logger.error(f"Error handling message: {e}", exc_info=True)
        
        # Handle admin commands
        @self.client.on(events.NewMessage(incoming=True, pattern=r'^/\w+', func=lambda e: self._is_admin(e)))
        async def handle_admin_command(event: events.NewMessage.Event):
            try:
                await self._handle_admin_command(event)
            except Exception as e:
                self.logger.error(f"Error handling admin command: {e}", exc_info=True)
    
    def _should_respond(self, event: events.NewMessage.Event) -> bool:
        """Check if bot should respond to this message"""
        if not event.is_private:
            # In groups, only respond if mentioned or replied to
            message: Message = event.message
            if message.mentioned or (message.reply_to and message.reply_to.reply_to_msg_id):
                return True
            return False
        return True
    
    def _is_admin(self, event: events.NewMessage.Event) -> bool:
        """Check if user is admin"""
        return event.sender_id in settings.admin_ids
    
    async def _handle_incoming_message(self, event: events.NewMessage.Event):
        """Handle incoming messages"""
        message: Message = event.message
        sender = await event.get_sender()
        chat = await event.get_chat()

        # Skip if sender is None (e.g., channel posts)
        if sender is None:
            self.logger.debug("Skipping message with no sender")
            return

        # Skip if message has no text content
        if not message.text or not message.text.strip():
            self.logger.debug(f"Skipping non-text message from {sender.id}")
            return

        self.logger.info(f"Message from {sender.id} in chat {chat.id}: {message.text[:100]}")

        # Get or create conversation context
        chat_id = event.chat_id
        if chat_id not in self.conversation_context:
            self.conversation_context[chat_id] = []

        # Add user message to context
        self.conversation_context[chat_id].append({
            'role': 'user',
            'content': message.text.strip()
        })
        
        # Keep only last 10 messages
        if len(self.conversation_context[chat_id]) > 20:
            self.conversation_context[chat_id] = self.conversation_context[chat_id][-20:]
        
        # Generate response
        try:
            self.logger.debug("Generating LLM response...")
            response = await llm_manager.generate_response(
                user_message=message.text,
                conversation_history=self.conversation_context[chat_id][:-1]
            )
            
            # Add assistant response to context
            self.conversation_context[chat_id].append({
                'role': 'assistant',
                'content': response
            })
            
            # Send response
            await event.reply(response)
            self.logger.info(f"Sent response: {len(response)} chars")
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}", exc_info=True)
            await event.reply("متأسفم، در پردازش پیام مشکلی پیش آمد.")
    
    async def _handle_admin_command(self, event: events.NewMessage.Event):
        """Handle admin commands"""
        message: Message = event.message
        text = message.text
        
        self.logger.info(f"Admin command from {event.sender_id}: {text}")
        
        # Parse command
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command == '/status':
            await self._cmd_status(event)
        elif command == '/addchannel':
            await self._cmd_add_channel(event, args)
        elif command == '/listchannels':
            await self._cmd_list_channels(event)
        elif command == '/removechannel':
            await self._cmd_remove_channel(event, args)
        elif command == '/suggestions':
            await self._cmd_list_suggestions(event)
        elif command == '/approve':
            await self._cmd_approve_suggestion(event, args)
        elif command == '/reject':
            await self._cmd_reject_suggestion(event, args)
        elif command == '/setprovider':
            await self._cmd_set_provider(event, args)
        elif command == '/clearcontext':
            await self._cmd_clear_context(event)
        elif command == '/help':
            await self._cmd_help(event)
        else:
            await event.reply("دستور نامعتبر. /help برای راهنما")
    
    async def _cmd_status(self, event):
        """Show bot status"""
        providers = llm_manager.list_providers()
        current_provider = runtime_config.get('current_llm_provider')
        
        status = f"""🤖 **وضعیت PushTutor**

✅ Userbot: Active
🧠 LLM Provider: {current_provider}
📊 Available Providers: {', '.join(providers)}
💾 Database: Connected
🗂 Curated Channels: {len(db_manager.get_curated_channels())}
📝 Pending Suggestions: {len(db_manager.get_pending_suggestions())}
"""
        await event.reply(status)
    
    async def _cmd_add_channel(self, event, args):
        """Add channel to curated list"""
        # Check if message is a forward
        message: Message = event.message
        
        if message.forward:
            # Extract channel info from forwarded message
            channel = message.forward.chat
            if hasattr(channel, 'id'):
                channel_id = str(channel.id)
                title = getattr(channel, 'title', 'Unknown')
                username = getattr(channel, 'username', None)
                
                # Parse additional info from args
                metadata = self._parse_channel_metadata(args)
                
                # Add to database
                db_manager.add_curated_channel(
                    channel_id=channel_id,
                    title=title,
                    username=username,
                    added_by=event.sender_id,
                    **metadata
                )
                
                await event.reply(f"✅ کانال **{title}** به لیست کانال‌های خوب اضافه شد.")
                self.logger.info(f"Admin {event.sender_id} added channel {channel_id}")
            else:
                await event.reply("❌ نمی‌توانم اطلاعات کانال را استخراج کنم.")
        else:
            await event.reply("لطفاً یک پیام از کانال مورد نظر را فوروارد کنید و دوباره این دستور را بزنید.")
    
    def _parse_channel_metadata(self, text: str) -> dict:
        """Parse channel metadata from text"""
        metadata = {
            'description': text if text else None,
            'topics': [],
            'level': None,
            'language': 'fa'
        }
        
        # Simple parsing (can be improved)
        if 'beginner' in text.lower() or 'مبتدی' in text:
            metadata['level'] = 'beginner'
        elif 'advanced' in text.lower() or 'پیشرفته' in text:
            metadata['level'] = 'advanced'
        elif 'intermediate' in text.lower() or 'متوسط' in text:
            metadata['level'] = 'intermediate'
        
        return metadata
    
    async def _cmd_list_channels(self, event):
        """List all curated channels"""
        channels = db_manager.get_curated_channels()
        
        if not channels:
            await event.reply("هیچ کانالی در لیست نیست.")
            return
        
        text = "📚 **لیست کانال‌های آموزشی**\n\n"
        for ch in channels[:20]:  # Limit to 20
            text += f"🔹 **{ch.title}**\n"
            if ch.username:
                text += f"   @{ch.username}\n"
            text += f"   ID: `{ch.channel_id}`\n"
            if ch.topics:
                text += f"   Topics: {', '.join(ch.topics)}\n"
            if ch.level:
                text += f"   Level: {ch.level}\n"
            text += "\n"
        
        if len(channels) > 20:
            text += f"\n... و {len(channels) - 20} کانال دیگر"
        
        await event.reply(text)
    
    async def _cmd_remove_channel(self, event, args):
        """Remove channel from curated list"""
        if not args:
            await event.reply("لطفاً channel_id را وارد کنید.")
            return
        
        channel_id = args.strip()
        if db_manager.remove_curated_channel(channel_id):
            await event.reply(f"✅ کانال {channel_id} حذف شد.")
        else:
            await event.reply(f"❌ کانال {channel_id} پیدا نشد.")
    
    async def _cmd_list_suggestions(self, event):
        """List pending channel suggestions"""
        suggestions = db_manager.get_pending_suggestions()
        
        if not suggestions:
            await event.reply("هیچ پیشنهادی در صف نیست.")
            return
        
        text = "📋 **پیشنهادات در انتظار بررسی**\n\n"
        for sug in suggestions:
            text += f"🆔 ID: {sug.id}\n"
            text += f"📢 Channel: {sug.title or sug.channel_id}\n"
            if sug.username:
                text += f"   @{sug.username}\n"
            text += f"👤 Suggested by: {sug.suggested_by}\n"
            if sug.reason:
                text += f"💬 Reason: {sug.reason}\n"
            text += "\n"
        
        text += "\n/approve <id> برای تایید\n/reject <id> برای رد"
        await event.reply(text)
    
    async def _cmd_approve_suggestion(self, event, args):
        """Approve a channel suggestion"""
        if not args:
            await event.reply("لطفاً ID پیشنهاد را وارد کنید.")
            return
        
        try:
            suggestion_id = int(args.strip().split()[0])
            if db_manager.approve_suggestion(suggestion_id, event.sender_id):
                await event.reply(f"✅ پیشنهاد {suggestion_id} تایید شد و به لیست اضافه شد.")
            else:
                await event.reply(f"❌ پیشنهاد {suggestion_id} پیدا نشد.")
        except ValueError:
            await event.reply("❌ ID نامعتبر است.")
    
    async def _cmd_reject_suggestion(self, event, args):
        """Reject a channel suggestion"""
        if not args:
            await event.reply("لطفاً ID پیشنهاد را وارد کنید.")
            return
        
        try:
            parts = args.strip().split(maxsplit=1)
            suggestion_id = int(parts[0])
            note = parts[1] if len(parts) > 1 else None
            
            if db_manager.reject_suggestion(suggestion_id, event.sender_id, note):
                await event.reply(f"✅ پیشنهاد {suggestion_id} رد شد.")
            else:
                await event.reply(f"❌ پیشنهاد {suggestion_id} پیدا نشد.")
        except ValueError:
            await event.reply("❌ ID نامعتبر است.")
    
    async def _cmd_set_provider(self, event, args):
        """Set LLM provider"""
        provider = args.strip().lower()
        available = llm_manager.list_providers()
        
        if provider in available:
            runtime_config.set('current_llm_provider', provider)
            await event.reply(f"✅ LLM provider به {provider} تغییر کرد.")
        else:
            await event.reply(f"❌ Provider نامعتبر. موجود: {', '.join(available)}")
    
    async def _cmd_clear_context(self, event):
        """Clear conversation context"""
        chat_id = event.chat_id
        if chat_id in self.conversation_context:
            self.conversation_context[chat_id] = []
        await event.reply("✅ تاریخچه گفتگو پاک شد.")
    
    async def _cmd_help(self, event):
        """Show help"""
        help_text = """🤖 **دستورات مدیریتی PushTutor**

**مدیریت کانال‌ها:**
/addchannel - اضافه کردن کانال (با forward)
/listchannels - لیست کانال‌های ثبت‌شده
/removechannel <id> - حذف کانال

**پیشنهادات:**
/suggestions - لیست پیشنهادات
/approve <id> - تایید پیشنهاد
/reject <id> [note] - رد پیشنهاد

**تنظیمات:**
/status - وضعیت ربات
/setprovider <name> - تغییر LLM provider
/clearcontext - پاک کردن تاریخچه گفتگو

/help - نمایش این راهنما
"""
        await event.reply(help_text)
    
    async def stop(self):
        """Stop userbot"""
        if self.client:
            self.logger.info("Stopping userbot...")
            await self.client.disconnect()
            self.is_running = False
            self.logger.info("Userbot stopped")
    
    async def run_until_disconnected(self):
        """Run userbot until disconnected"""
        if self.client:
            await self.client.run_until_disconnected()


# Global userbot instance
userbot = UserbotHandler()
