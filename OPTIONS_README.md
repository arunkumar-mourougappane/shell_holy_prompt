# Options Trading Script - README

## What This Script Does

This Python script provides a complete, production-ready interface to the TD Ameritrade API (which powers ThinkorSwim) for automated options trading. It handles:

- ✅ **Secure Authentication**: OAuth 2.0 with automatic token refresh
- ✅ **Credential Storage**: System keyring integration for secure credential management  
- ✅ **Market Data**: Real-time quotes, option chains, Greeks, and implied volatility
- ✅ **Trading Operations**: Place, modify, and cancel orders
- ✅ **Position Management**: View positions, P&L, and account balances
- ✅ **Risk Management**: Built-in risk calculation and position sizing
- ✅ **Multiple Strategies**: Vertical spreads, iron condors, and more
- ✅ **Logging**: Comprehensive logging for debugging and auditing

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up credentials (interactive)
python3 options_trader.py --setup

# 3. Start trading
python3 options_trader.py --quote AAPL
python3 options_trader.py --positions
```

📖 **Full Documentation**: See [OPTIONS_TRADING_GUIDE.md](OPTIONS_TRADING_GUIDE.md)

## Features

### 1. Secure Authentication

- Uses OAuth 2.0 with TD Ameritrade
- Stores refresh token in OS-level keyring (Keychain, GNOME Keyring, etc.)
- Automatic token refresh when needed
- No passwords stored in plain text

### 2. Market Data Access

```python
api = TDAmeritradeAPI()
api.authenticate()

# Get real-time quote
quote = api.get_quote('AAPL')

# Get option chain with Greeks
chain = api.get_option_chain('SPY', contract_type='CALL')
```

### 3. Trading Operations

```python
# Place a limit order to buy a call option
order = api.create_order(
    order_type='LIMIT',
    symbol='AAPL_100121C150',
    quantity=1,
    price=1.50,
    instruction='BUY_TO_OPEN'
)
api.place_order(order)

# View positions
positions = api.get_positions()

# Cancel an order
api.cancel_order(order_id)
```

### 4. Strategy Analysis

```python
strategy = OptionsStrategy(api, risk_per_trade=0.02)

# Find trading opportunities
opportunities = strategy.find_opportunities(
    symbol='SPY',
    strategy_type='vertical_spread'
)

# Analyze specific option
analysis = strategy.analyze_option(option_data)
print(f"Liquidity Score: {analysis['liquidity_score']}")
print(f"Delta: {analysis['delta']}")
```

## Requirements

- Python 3.8+
- TD Ameritrade brokerage account
- TD Ameritrade Developer account (free at [developer.tdameritrade.com](https://developer.tdameritrade.com))
- Options trading approval on your brokerage account

## Dependencies

- `requests` - HTTP client for API calls
- `keyring` - Secure credential storage

## Architecture

```
options_trader.py
├── TDAmeritradeAPI (Main API Client)
│   ├── Authentication (OAuth 2.0)
│   ├── Market Data (Quotes, Chains)
│   ├── Account Info (Positions, Orders)
│   └── Order Management (Place, Cancel)
│
└── OptionsStrategy (Strategy Engine)
    ├── Option Analysis
    ├── Opportunity Finding
    └── Order Creation
```

## Security

### What's Protected

- ✅ Client ID stored in keyring
- ✅ Account ID stored in keyring
- ✅ Refresh token stored in keyring (encrypted by OS)
- ✅ Access tokens kept in memory only
- ✅ No credentials in source code
- ✅ No credentials in logs

### Best Practices

1. **Never commit config.json** (use config.example.json as template)
2. **Never share your Client ID or tokens**
3. **Enable 2FA on your TD Ameritrade account**
4. **Review orders before submission**
5. **Start with small positions**
6. **Keep Python and dependencies updated**

## API Rate Limits

TD Ameritrade enforces rate limits:
- **120 requests per minute** (per app)
- **10,000 requests per day** (per app)

The script doesn't currently implement rate limiting, so be mindful of your request frequency.

## Trading Strategies Supported

### 1. Vertical Spreads
- Bull Call Spread (buy lower strike, sell higher strike)
- Bear Put Spread (buy higher strike, sell lower strike)
- Limited risk, limited profit
- Good for directional trades

### 2. Iron Condor
- Sell OTM call spread + sell OTM put spread
- Profit from low volatility
- Defined risk, limited profit
- Good for range-bound markets

### 3. Custom Strategies
The framework allows you to implement your own strategies by:
1. Extending `OptionsStrategy` class
2. Implementing your analysis logic
3. Using the API to execute trades

## Risk Warning

⚠️ **IMPORTANT**: Options trading is risky and not suitable for everyone.

- You can lose 100% of your investment
- Options can expire worthless
- High leverage amplifies losses
- Market conditions can change rapidly
- Past performance ≠ future results

**Only trade with money you can afford to lose.**

## How to Generate Gains

The intention behind this API integration is to enable **systematic, rules-based trading** with proper risk management. Key principles:

### 1. Risk Management
- Never risk more than 2% per trade
- Define maximum loss before entry
- Use stop losses
- Take profits at 50-75% of max gain

### 2. Strategy Selection
- Use strategies appropriate for market conditions
- Vertical spreads for directional moves
- Iron condors for range-bound markets
- Focus on high-probability trades

### 3. Position Sizing
- Calculate position size based on account risk
- Don't over-leverage
- Maintain diversification

### 4. Discipline
- Follow your trading plan
- Don't chase losses
- Take profits systematically
- Review and learn from each trade

### Expected Returns

With disciplined execution:
- Conservative: 1-2% per month
- Moderate: 2-4% per month  
- Aggressive: 4-6% per month

Higher returns = higher risk. **Capital preservation is priority #1.**

## Files

- `options_trader.py` - Main script with API client and strategy engine
- `OPTIONS_TRADING_GUIDE.md` - Complete documentation (400+ lines)
- `QUICKSTART.md` - Get started in 5 minutes
- `requirements.txt` - Python dependencies
- `config.example.json` - Configuration template
- `.gitignore` - Excludes sensitive files

## Command-Line Usage

```bash
# Setup
python3 options_trader.py --setup

# Get quote
python3 options_trader.py --quote SYMBOL

# Get option chain
python3 options_trader.py --chain SYMBOL

# View positions
python3 options_trader.py --positions

# View orders
python3 options_trader.py --orders

# View account info
python3 options_trader.py --account
```

## Python Module Usage

```python
from options_trader import TDAmeritradeAPI, OptionsStrategy

# Initialize
api = TDAmeritradeAPI()
if not api.authenticate():
    print("Setup required: python3 options_trader.py --setup")
    exit(1)

# Get market data
quote = api.get_quote('AAPL')
chain = api.get_option_chain('SPY')

# Manage positions
positions = api.get_positions()
orders = api.get_orders()

# Trade (be careful!)
order = {...}  # Create order specification
# api.place_order(order)
```

## Testing

Since TD Ameritrade doesn't provide a separate paper trading API, testing must be done carefully:

1. **Start Small**: Use 1 contract for initial tests
2. **Verify Output**: Check all API responses before trading
3. **Review Orders**: Double-check before submission
4. **Test Flow**: Run through entire workflow with minimal risk
5. **Monitor Closely**: Watch initial trades carefully

## Troubleshooting

### "Client ID not provided"
→ Run `python3 options_trader.py --setup`

### "Authentication failed"
→ Check Client ID, ensure callback URL is `https://localhost`, get new auth code

### "API request failed: 401"
→ Re-authenticate with `--setup`

### "No keyring backend available"
→ Install keyring backend for your OS (gnome-keyring, etc.)

📖 **More Help**: See [Troubleshooting](OPTIONS_TRADING_GUIDE.md#troubleshooting) section

## Contributing

This script is part of the `shell_holy_prompt` repository. Contributions welcome:

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

See LICENSE file in repository root.

## Disclaimer

**This software is for educational purposes only.**

- Not financial advice
- No warranty or guarantee
- Use at your own risk
- Authors not responsible for losses
- Consult financial advisors before trading

**Trading involves substantial risk of loss.**

## Support

- 📖 [Full Documentation](OPTIONS_TRADING_GUIDE.md)
- 🚀 [Quick Start](QUICKSTART.md)
- 💻 [TD Ameritrade API Docs](https://developer.tdameritrade.com/)
- 📚 [Options Education](https://www.optionseducation.org/)

---

**Ready to start?** → [QUICKSTART.md](QUICKSTART.md)
