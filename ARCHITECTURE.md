# PushTutor - نمای کلی پروژه

## ساختار پروژه

```
pushtutor/
├── main.py                 # Entry point اصلی - اجرای Userbot + Bot
├── config.py               # مدیریت تنظیمات از .env
├── logger.py               # سیستم لاگینگ حرفه‌ای
├── database.py             # Models و مدیریت دیتابیس
├── llm_manager.py          # مدیریت Gemini/OpenAI/OpenRouter
├── userbot.py              # Telethon userbot handler
├── bot.py                  # Telegram Bot API handler
├── system_prompt.txt       # System prompt برای LLM
│
├── .env.example            # نمونه فایل تنظیمات
├── requirements.txt        # Dependencies پایتون
├── .gitignore              # Git ignore rules
│
├── README.md               # مستندات اصلی
├── QUICKSTART.md           # راهنمای سریع شروع
├── DEPLOYMENT.md           # راهنمای deploy و production
│
├── setup.sh                # اسکریپت نصب
├── run.sh                  # اسکریپت اجرا
│
├── Dockerfile              # برای Docker
├── docker-compose.yml      # Docker Compose config
└── pushtutor.service       # Systemd service file
```

## معماری

### ۱. Core Components

#### Config Manager (`config.py`)
- خواندن تنظیمات از `.env`
- Validation با Pydantic
- Runtime config برای تغییرات توسط ادمین

#### Logger (`logger.py`)
- File logging با rotation (10MB chunks)
- Colored console output
- سطوح مختلف (DEBUG, INFO, WARNING, ERROR)
- فرمت استاندارد برای debug

#### Database (`database.py`)
- SQLAlchemy ORM
- Models:
  - `CuratedChannel`: کانال‌های تایید‌شده
  - `ChannelSuggestion`: پیشنهادات کاربران
  - `LearningPlan`: برنامه‌های یادگیری
  - `UserInteraction`: تاریخچه تعاملات
- Context manager برای session management

#### LLM Manager (`llm_manager.py`)
- پشتیبانی از چند provider:
  - Google Gemini
  - OpenAI (GPT-4)
  - OpenRouter (Claude, etc.)
- Conversation history management
- Async/sync interfaces

### ۲. Telegram Handlers

#### Userbot (`userbot.py`)
- Telethon برای اکانت شخصی
- کار در گروه‌ها
- Mention detection
- Admin commands
- Context-aware conversations

#### Bot API (`bot.py`)
- python-telegram-bot
- کار در خصوصی و گروه‌ها
- Commands system
- Forward handling برای suggestions
- Conversation management

### ۳. Main Application (`main.py`)
- اجرای همزمان Userbot + Bot
- Signal handling برای graceful shutdown
- Initialization و health checks
- Task management

## Flow Diagram

```
User Message
    ↓
[Telegram] → Userbot/Bot Handler
    ↓
Context Manager (conversation history)
    ↓
LLM Manager → Gemini/OpenAI/OpenRouter
    ↓
Response Generation
    ↓
[Telegram] → User
```

## Data Flow

```
.env → Config Manager → Runtime Config
                           ↓
                    Components Access Config
                           ↓
User Interaction → Database → Analytics
                           ↓
Admin Actions → Update Database → Notify Users
```

## ویژگی‌های کلیدی

### ✅ Dual Mode Operation
- **Userbot**: اکانت شخصی در گروه‌ها
- **Bot API**: ربات عمومی

### ✅ Multi-LLM Support
- Auto-fallback اگر provider در دسترس نباشد
- Runtime switching
- Cost optimization (cheap models for simple tasks)

### ✅ Channel Management
- Curated list توسط ادمین
- User suggestions with approval flow
- Metadata: topics, level, language

### ✅ Conversation Management
- Per-user/per-chat context
- History truncation (last 20 messages)
- Clear command برای reset

### ✅ Admin Features
- دستورات مدیریتی کامل
- Suggestion approval/rejection
- Status monitoring
- Runtime configuration

### ✅ Logging & Monitoring
- Structured logging
- File + Console output
- Log rotation
- Debug information

### ✅ Production Ready
- Systemd service
- Docker support
- Health checks
- Error handling
- Graceful shutdown

## Security

- API keys در `.env` (never commit)
- Admin-only commands با user ID check
- Session files secure permissions
- Database access control

## Scalability

- SQLite برای شروع
- PostgreSQL برای production
- Redis cache (optional)
- Multiple instances با load balancer
- Vector search برای بهبود جستجو (optional)

## Extensibility

### اضافه کردن LLM Provider جدید

```python
# در llm_manager.py
if settings.new_provider_key:
    self.providers['new_provider'] = NewProvider(
        api_key=settings.new_provider_key
    )
```

### اضافه کردن Command جدید

```python
# در bot.py یا userbot.py
async def _cmd_new_command(self, event):
    # implementation
    pass

# در _register_handlers()
app.add_handler(CommandHandler("newcmd", self._cmd_new_command))
```

### اضافه کردن Model جدید

```python
# در database.py
class NewModel(Base):
    __tablename__ = 'new_table'
    # columns
```

## Performance

### Optimization Tips

1. **Database**: استفاده از indexes
2. **LLM**: Cache برای سوالات مشابه
3. **Memory**: محدود کردن conversation history
4. **Network**: Connection pooling

### Monitoring

```bash
# CPU & Memory
ps aux | grep python

# Logs
tail -f logs/pushtutor.log

# Database size
ls -lh *.db
```

## Deployment Options

1. **Direct**: `python main.py`
2. **Systemd**: Service در background
3. **Docker**: Container isolated
4. **Screen/Tmux**: Manual session management

## Testing

### Manual Testing
```bash
# در Telegram
/start
می‌خوام پایتون یاد بگیرم
```

### Log Verification
```bash
tail -f logs/pushtutor.log
# باید ببینی:
# - Connection logs
# - Message processing
# - LLM requests
# - No errors
```

## Common Workflows

### نصب و راه‌اندازی
```bash
./setup.sh
nano .env  # configure
./run.sh
```

### اضافه کردن کانال (Admin)
```
1. Forward از کانال
2. /addchannel [metadata]
```

### بررسی پیشنهادات (Admin)
```
/suggestions
/approve <id>
```

### تغییر Provider (Admin)
```
/setprovider openai
```

### Deploy Production
```bash
# Systemd
sudo cp pushtutor.service /etc/systemd/system/
sudo systemctl start pushtutor

# یا Docker
docker-compose up -d
```

## Troubleshooting

| مشکل | علت | راه حل |
|------|------|--------|
| Bot respond نمی‌کنه | API key | چک `.env` |
| Userbot connect نمی‌شه | Session | حذف `.session` file |
| Database lock | Multiple instances | Kill processes |
| Memory زیاد | History | `/clear` یا restart |

## Future Enhancements

- [ ] TGStat API integration
- [ ] Vector search با ChromaDB
- [ ] File processing (PDF, ZIP)
- [ ] Learning plan tracking
- [ ] Progress monitoring
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Voice message handling
- [ ] Image generation integration
- [ ] Calendar integration
- [ ] Notification system

## Contributing

### Code Style
- Python 3.9+
- Type hints
- Docstrings
- Meaningful names

### Logging Convention
```python
logger.info("Action completed successfully")
logger.warning("Non-critical issue")
logger.error("Error occurred", exc_info=True)
```

### Git Workflow
```bash
git checkout -b feature/new-feature
# make changes
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

## Support

- **Documentation**: README.md, QUICKSTART.md, DEPLOYMENT.md
- **Logs**: `logs/pushtutor.log`
- **Issues**: GitHub Issues
- **Contact**: facksten@pushrsP team

## License

Developed by facksten for PushRSP team
