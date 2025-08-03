# 🤖 Telegram Anonymous Chat Bot

A comprehensive Telegram bot for anonymous chat with advanced features including profile management, smart partner matching, content moderation, and gamification elements.

## ✨ Features

### 🔥 Core Features
- **Anonymous 1-on-1 Chat** - Connect with random users anonymously
- **Smart Partner Matching** - Advanced algorithm to find compatible partners
- **User Profiles** - Complete profile system with photos, bio, hobbies
- **Multi-language Support** - English and Indonesian language support
- **Real-time Messaging** - Support for text, images, voice, video, stickers

### 🎯 Advanced Features
- **Pro Search** - Premium users can search by gender, hobbies, and age
- **Background Matching** - Continuous search for partners when queue is empty
- **Secret Mode** - Temporary messages that disappear after reading
- **Content Moderation** - Automatic filtering of inappropriate content
- **User Reports & Blocking** - Community moderation tools
- **Points System** - Gamification with user points and leaderboard

### 🎮 Gamification
- **Quiz Games** - Interactive quizzes with point rewards
- **Leaderboard** - Top users by points
- **Daily Statistics** - Usage analytics and reporting
- **Achievement System** - User engagement tracking

### 🔧 Technical Features
- **Database Management** - Efficient SQLite database with proper indexing
- **Error Handling** - Comprehensive error handling and logging
- **Rate Limiting** - Protection against spam and abuse
- **Modular Architecture** - Clean, maintainable code structure

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd bot-tele
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your bot token and configuration
```

**Important**: Edit the `.env` file with your actual bot token:
```env
BOT_TOKEN=123456789:ABCDEF...  # Your actual bot token from @BotFather
OWNER_ID=your_telegram_user_id  # Your Telegram user ID
```

4. **Install additional dependencies (optional)**
```bash
pip install python-dotenv  # For .env file support
```

5. **Run the bot**
```bash
python bot.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
BOT_TOKEN=your_bot_token_here
OWNER_ID=your_telegram_user_id
DB_PATH=bot_database.db
NSFW_API_KEY=your_moderatecontent_api_key
PRO_WEEK_PRICE=1000
PRO_MONTH_PRICE=3500
QUIZ_LIMIT_WINNERS=5
```

### Getting Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the bot token to your `.env` file

### Finding Your User ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your user ID to the `OWNER_ID` field in `.env`

## 📁 Project Structure

```
bot-tele/
├── bot.py                 # Main bot application
├── config.py             # Configuration and constants
├── database.py           # Database operations and models
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # Project documentation
├── handlers/            # Command and message handlers
│   ├── __init__.py
│   ├── decorators.py    # Function decorators
│   └── chat_handlers.py # Chat-related handlers
└── utils/               # Utility functions
    ├── __init__.py
    └── keyboards.py     # Telegram keyboard layouts
```

## 🎮 Bot Commands

### User Commands
- `/start` - Start the bot and show main menu
- `/help` - Show help information
- `/profile` - Create/edit user profile
- `/find` - Start searching for a chat partner
- `/stop` - End current chat or cancel search
- `/next` - Find a new partner (end current chat)
- `/stats` - Show bot statistics

### Admin Commands
- `/admin` - Admin panel with detailed statistics

### Menu Buttons
- **Find a partner** - Start random chat
- **Search Pro** - Advanced search (Pro users)
- **My Profile** - View/edit profile
- **Play Quiz** - Interactive quiz games
- **Join Group** - Group chat feature
- **Next/Stop** - Chat controls
- **Secret Mode** - Enable disappearing messages

## 💾 Database Schema

The bot uses SQLite with the following main tables:

- `user_profiles` - User information and settings
- `sessions` - Active chat sessions
- `chat_queue` - Users waiting for partners
- `block_list` - Blocked user relationships
- `reports` - User reports and moderation
- `feedback` - Chat ratings and feedback
- `quiz_winners` - Quiz game results
- `polls` - Polling data

## 🔒 Security Features

- **User Ban System** - Temporary and permanent bans
- **Content Moderation** - Automatic filtering of inappropriate content
- **Report System** - Users can report problematic behavior
- **Block System** - Users can block unwanted contacts
- **Rate Limiting** - Protection against spam and abuse

## 🎯 Matching Algorithm

The bot uses an intelligent matching system:

1. **Immediate Matching** - Instant connection if compatible partner is available
2. **Queue System** - Users wait in queue with preferences
3. **Background Search** - Continuous partner search for queued users
4. **Priority Matching** - Pro users get priority and advanced filters
5. **Compatibility Scoring** - Match based on shared interests and preferences

## 🛠️ Development

### Adding New Features

1. **Handlers** - Add new command handlers in `handlers/`
2. **Database** - Add new database operations in `database.py`
3. **Configuration** - Add new settings in `config.py`
4. **Keyboards** - Add new button layouts in `utils/keyboards.py`

### Database Migrations

The bot automatically creates required tables on first run. For schema changes:

1. Update table definitions in `database.py`
2. The bot will create new tables automatically
3. For existing table modifications, manual migration may be required

### Testing

Before deploying:

1. Test all commands and features
2. Verify database operations
3. Check error handling
4. Test with multiple users

## 📈 Monitoring

The bot includes comprehensive logging and monitoring:

- **Daily Reports** - Automated daily statistics to admin
- **Error Logging** - Detailed error tracking
- **User Analytics** - Usage patterns and engagement metrics
- **Performance Monitoring** - Database and response time tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information
4. Contact the admin if configured

## 🔄 Updates

### Recent Changes (Refactored Version)

- ✅ **Modular Architecture** - Separated into logical modules
- ✅ **Improved Partner Search** - Fixed matching algorithm with background search
- ✅ **Better Error Handling** - Comprehensive error management
- ✅ **Environment Configuration** - Secure configuration management
- ✅ **Code Cleanup** - Removed duplications and improved readability
- ✅ **Enhanced Database** - Optimized database operations
- ✅ **Better Logging** - Improved logging and monitoring

### Planned Features

- 🔲 Advanced Pro features
- 🔲 Group chat enhancements
- 🔲 Quiz system expansion
- 🔲 Payment integration
- 🔲 Mobile app companion
- 🔲 Advanced analytics dashboard

---

**Built with ❤️ for the Telegram community**