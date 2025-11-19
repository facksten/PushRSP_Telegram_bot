# 🚀 PushTutor v2.0 - Cyberspace Edition

```
╔═══════════════════════════════╗
║  ██████╗ ██╗   ██╗███████╗██╗ ║
║  ██╔══██╗██║   ██║██╔════╝██║ ║
║  ██████╔╝██║   ██║███████╗██║ ║
║  ██╔═══╝ ██║   ██║╚════██║██║ ║
║  ██║     ╚██████╔╝███████║██║ ║
║  ╚═╝      ╚═════╝ ╚══════╝╚═╝ ║
║      [ PUSHTUTOR v2.0 ]       ║
║    [:: CYBERSPACE EDITION ::]  ║
╚═══════════════════════════════╝
```

Advanced Telegram learning assistant with **cyberpunk-themed UI**, **full-text search**, and **AI-powered responses**.

Developed by **facksten** for the **PushRSP** team.

---

## ⚡ F34TUR3S

### 🎨 Cyberpunk UI & UX
- **L33T SP34K** text styling and command aliases
- **ASCII art** banners and visual elements
- **Glass-morphism** inline keyboards
- **Animated loading** bars and progress indicators
- **Glitch effects** and retro terminal aesthetics

### 🔍 Advanced Search Engine
- **Full-text search** across indexed channel messages
- **Fast database** indexing with SQLite/PostgreSQL
- **Multi-channel** content aggregation
- **Relevance ranking** by views, forwards, and date
- Search filters by channel, date, and topic

### 🤖 AI Integration
- **Multiple LLM providers**: Gemini, OpenAI, OpenRouter
- **Conversation context** management
- **Smart responses** to user queries
- **Dynamic provider switching**

### 📡 Dual Mode Operation
- **Userbot mode** (Telethon) - for personal account interactions
- **Bot API mode** (python-telegram-bot) - for public bot
- Run both simultaneously or independently

### 🛠️ Admin Features
- Channel curation and management
- Message indexing and scraping
- User suggestion system with approval workflow
- Statistics and analytics
- LLM provider configuration

---

## 📦 1N574££471ON

### Prerequisites
```bash
# Python 3.10+
python3 --version

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies
```
python-telegram-bot>=20.0
telethon>=1.36.0
sqlalchemy>=2.0
langchain>=0.3.0
langchain-google-genai>=2.0.0
langchain-openai>=0.2.0
python-dotenv>=1.0.0
```

---

## ⚙️ C0NF16UR471ON

### 1. Create `.env` file

```bash
cp .env.example .env
nano .env
```

### 2. Configure Environment Variables

```env
# Telegram Bot Token (from @BotFather)
BOT_TOKEN=your_bot_token_here

# Telegram API Credentials (from my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890

# Admin User IDs (comma-separated)
ADMIN_IDS=123456789,987654321

# LLM API Keys
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
OPENROUTER_API_KEY=your_openrouter_key

# Default LLM Provider
DEFAULT_LLM_PROVIDER=gemini

# Enable/Disable Components
ENABLE_USERBOT=true
ENABLE_BOT=true

# Database
DATABASE_URL=sqlite:///pushtutor.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pushtutor.log
```

---

## 🚀 U54G3

### Start the Bot

```bash
# Normal mode
python3 main.py

# With proxychains (for Tor/SOCKS proxy)
proxychains python3 main.py
```

### First Time Setup
1. Run the bot - it will ask for phone verification
2. Enter the code sent to your Telegram
3. Bot will start automatically

---

## 🎯 C0MM4ND5

### User Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `/start` | - | Initialize system and show welcome |
| `/help` | `/h3lp` | Display command reference |
| `/search <query>` | `/s34rch` | Search indexed content |
| `/channels` | `/ch4nn3ls` | List curated channels |
| `/stats` | - | Display statistics |
| `/suggest` | - | Submit new channel suggestion |
| `/clear` | - | Wipe conversation context |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/status` | Show bot status and configuration |
| `/addchannel` | Add channel to curated list |
| `/listchannels` | List all curated channels |
| `/removechannel <id>` | Remove channel from list |
| `/suggestions` | List pending suggestions |
| `/approve <id>` | Approve channel suggestion |
| `/reject <id>` | Reject channel suggestion |
| `/setprovider <name>` | Change LLM provider |
| `/indexchannel <id> [limit]` | Index specific channel |
| `/indexall [limit]` | Index all curated channels |

---

## 🏗️ 4RCH1T3C7UR3

```
pushtutor_bot/
├── main.py                 # Entry point
├── config.py              # Configuration management
├── database.py            # SQLAlchemy models & DB operations
├── logger.py              # Logging setup
├── llm_manager.py         # LLM provider management
├── userbot.py             # Telethon userbot handler
├── bot.py                 # Bot API handler
├── channel_indexer.py     # Channel message scraper/indexer
├── cyberpunk_ui.py        # UI utilities and styling
├── system_prompt.txt      # LLM system prompt
├── .env                   # Environment variables
└── requirements.txt       # Python dependencies
```

### Database Schema

**Tables:**
- `curated_channels` - Admin-approved channels
- `channel_suggestions` - User-submitted suggestions
- `channel_messages` - Indexed channel content
- `search_index` - Full-text search tokens
- `learning_plans` - User learning roadmaps
- `user_interactions` - Analytics data

---

## 🎨 CYBERPUNK UI EXAMPLES

### Welcome Message
```
╔═══════════════════════════════╗
║      [ PUSHTUTOR v2.0 ]       ║
║    [:: CYBERSPACE EDITION ::]  ║
╚═══════════════════════════════╝

> SYS INIT... OK
> LOADING NEURAL INTERFACE... OK
> CONNECTING TO CYBERSPACE... OK

[ SYSTEM STATUS: ONLINE ]
[ NEURAL LINK: ACTIVE ]
```

### Search Results
```
╔══════════════════════════════════╗
║  [S34RCH R3SU£75]               ║
║  > Scanning database...          ║
╚══════════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ #1 » Python Tutorial Channel
┃ [2025-01-15]
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Complete Python course for...
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Progress Bar
```
[████████████████░░░░] 80%
╾━━━━━━━━━━━━━━━━━━─╼ 75%
【▓▓▓▓▓▓▓▓▓▓▓▓▓░░░】 85%
```

---

## 🔧 D3V3£0PM3N7

### Features to Add
- [ ] Semantic search with embeddings
- [ ] Voice message transcription
- [ ] PDF/document parsing
- [ ] Multi-language support
- [ ] User learning analytics
- [ ] Scheduled content recommendations
- [ ] Integration with more LLM providers

### Code Style
- Follow PEP 8
- Use type hints
- Document with docstrings
- Log important events

---

## 📝 L1C3NS3

This project is developed for educational purposes by the **PushRSP** team.

**Developer**: facksten
**Version**: 2.0 - Cyberspace Edition
**Status**: Active Development

---

## 🆘 7R0U8L35H007ING

### Common Issues

**Issue**: `AttributeError: 'NoneType' object has no attribute 'id'`
**Fix**: Updated in v2.0 - now skips messages without senders

**Issue**: `Gemini API error: No content messages found`
**Fix**: Updated in v2.0 - filters empty messages before API call

**Issue**: Bot not responding
**Fix**: Check LLM API keys and network connectivity

**Issue**: Database errors
**Fix**: Delete `pushtutor.db` and restart to recreate

### Getting Help
- Check logs in `logs/pushtutor.log`
- Enable debug mode: `LOG_LEVEL=DEBUG`
- Contact: facksten on Telegram

---

## 🌟 CR3D175

**Created by**: facksten
**Team**: PushRSP
**Inspired by**: Cyberpunk aesthetics, hacker culture, and the pursuit of knowledge

```
> J4CK 1N, 57UDY H4RD, H4CK TH3 W0R£D
> [SYSTEM READY FOR INPUT]
```

---

**[END OF TRANSMISSION]**
# PushRSP_Telegram_bot
