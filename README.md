# shell_holy_prompt
A concise, light-weight prompt additions for use in development in command line.

## Features

### Shell Prompt Customizations
- Git-aware color prompt
- SSH agent management
- Streamlined bash prompt configuration

### Options Trading Script
A Python-based options trading script with ThinkorSwim/TD Ameritrade API integration.

**Features:**
- Secure OAuth 2.0 authentication
- Credential storage using system keyring
- Real-time quotes and option chains
- Position and order management
- Risk management tools
- Multiple trading strategies

**Quick Start:**
```bash
# Install dependencies
pip install -r requirements.txt

# Setup credentials
python3 options_trader.py --setup

# Get a quote
python3 options_trader.py --quote AAPL
```

**Documentation:**
- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Complete Documentation](OPTIONS_TRADING_GUIDE.md) - Full API reference and trading guide

**⚠️ Risk Warning:** Options trading involves substantial risk. Only trade with capital you can afford to lose. See documentation for full risk disclosure.
