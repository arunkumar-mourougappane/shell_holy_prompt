# Quick Start Guide - Options Trading Script

## 1. Installation (5 minutes)

```bash
# Install dependencies
pip install -r requirements.txt
```

## 2. Get TD Ameritrade API Access (10-15 minutes)

1. **Create Developer Account**
   - Visit https://developer.tdameritrade.com/
   - Sign up (free)
   - Verify email

2. **Create App**
   - Go to "My Apps"
   - Click "Add a new App"
   - App Name: "My Options Trader" (or any name)
   - Callback URL: `https://localhost` (exactly)
   - Click "Create App"
   - **Save your Consumer Key** (this is your Client ID)

3. **Find Account ID**
   - Log in to your TD Ameritrade brokerage account
   - Your account number is your Account ID

## 3. Setup Script (2 minutes)

```bash
python3 options_trader.py --setup
```

Follow the prompts:
1. Enter Client ID (Consumer Key from step 2)
2. Enter Account ID (from step 2)
3. Open the authorization URL in browser
4. Login and approve
5. Copy redirect URL (even though page won't load)
6. Paste URL into script

Done! Credentials are now securely stored.

## 4. Test It Out (1 minute)

```bash
# Get a stock quote
python3 options_trader.py --quote AAPL

# View your positions
python3 options_trader.py --positions

# Get option chain
python3 options_trader.py --chain SPY
```

## 5. Start Trading

Read the full documentation: [OPTIONS_TRADING_GUIDE.md](OPTIONS_TRADING_GUIDE.md)

### Safety Checklist

- [ ] I understand options trading risks
- [ ] I've read the risk management section
- [ ] I'll start with small positions
- [ ] I have a trading plan
- [ ] I know my maximum loss before entering trades

## Need Help?

- **Authentication Issues**: Check [Troubleshooting](OPTIONS_TRADING_GUIDE.md#troubleshooting)
- **API Questions**: See [TD Ameritrade API Docs](https://developer.tdameritrade.com/apis)
- **Trading Education**: Visit [optionsplaybook.com](https://www.optionsplaybook.com/)

## Example Python Usage

```python
from options_trader import TDAmeritradeAPI

# Initialize and authenticate
api = TDAmeritradeAPI()
api.authenticate()

# Get quote
quote = api.get_quote('AAPL')
print(f"AAPL: ${quote['AAPL']['lastPrice']}")

# Get positions
positions = api.get_positions()
for pos in positions:
    print(f"{pos['instrument']['symbol']}: {pos['longQuantity']}")
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `--setup` | Initial configuration and authentication |
| `--quote SYMBOL` | Get real-time quote |
| `--chain SYMBOL` | Get option chain |
| `--positions` | View current positions |
| `--orders` | View recent orders |
| `--account` | View account info |

## Important Notes

⚠️ **Paper Trading**: TD Ameritrade doesn't offer a separate paper trading API. Test with small real positions.

⚠️ **Rate Limits**: Don't make more than 120 requests per minute.

⚠️ **Risk**: Options can expire worthless. Never risk more than you can afford to lose.

⚠️ **Security**: Never share your Client ID, Account ID, or tokens.

## Next Steps

1. ✅ Complete setup
2. 📚 Read [OPTIONS_TRADING_GUIDE.md](OPTIONS_TRADING_GUIDE.md)
3. 📊 Study a strategy (vertical spreads recommended for beginners)
4. 📝 Create a trading plan
5. 🎯 Make your first small trade
6. 📈 Track and review results
7. 🔄 Iterate and improve

Happy trading! 🚀

---

**Disclaimer**: This software is for educational purposes. Trading involves substantial risk. Past performance doesn't guarantee future results. Consult financial advisors before making investment decisions.
