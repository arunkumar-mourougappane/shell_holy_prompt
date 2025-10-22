# Options Trading Script Documentation

## Overview

This Python script provides a secure and comprehensive interface to TD Ameritrade's API (which powers ThinkorSwim) for options trading. It implements secure credential storage using keyring, OAuth 2.0 authentication, and various trading operations.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [API Setup](#api-setup)
4. [Authentication](#authentication)
5. [Usage Examples](#usage-examples)
6. [Trading Strategies](#trading-strategies)
7. [Risk Management](#risk-management)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

## Prerequisites

### Requirements

- Python 3.8 or higher
- TD Ameritrade brokerage account
- TD Ameritrade Developer API account
- Internet connection for API access

### Knowledge Requirements

- Basic understanding of options trading
- Familiarity with command-line interfaces
- Understanding of API concepts and OAuth 2.0

## Installation

### 1. Clone or Download the Repository

```bash
cd /path/to/shell_holy_prompt
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install dependencies manually:

```bash
pip install requests keyring
```

### 3. Make the Script Executable

```bash
chmod +x options_trader.py
```

## API Setup

### Step 1: Create TD Ameritrade Developer Account

1. Go to [TD Ameritrade Developer Portal](https://developer.tdameritrade.com/)
2. Sign up for a developer account (free)
3. Verify your email address

### Step 2: Create an Application

1. Log in to the developer portal
2. Navigate to "My Apps"
3. Click "Add a new App"
4. Fill in the application details:
   - **App Name**: Choose any name (e.g., "My Options Trader")
   - **Callback URL**: Enter `https://localhost` (exactly as shown)
   - **Description**: Brief description of your app
5. Click "Create App"
6. Note down your **Consumer Key** (this is your Client ID)

### Step 3: Note Your Account Information

- **Client ID**: Your Consumer Key from the app you created
- **Account ID**: Your TD Ameritrade account number (found in your brokerage account)

## Authentication

### Initial Setup

Run the setup process to securely store your credentials:

```bash
python3 options_trader.py --setup
```

Follow the interactive prompts:

1. **Enter Client ID**: Paste your Consumer Key from the developer portal
2. **Enter Account ID**: Enter your TD Ameritrade account number
3. **Authorize Application**: 
   - The script will provide an authorization URL
   - Open the URL in your browser
   - Log in to TD Ameritrade
   - Approve the application access
   - You'll be redirected to `https://localhost/?code=...`
   - Copy the entire URL (even though the page won't load)
4. **Paste Redirect URL**: Paste the full redirect URL into the script

The script will:
- Exchange the authorization code for access and refresh tokens
- Securely store all credentials in your system's keyring
- Set up automatic token refresh for future use

### How Authentication Works

The script uses OAuth 2.0 authentication with the following flow:

1. **Initial Authorization**: User authorizes the app via browser
2. **Token Exchange**: Authorization code is exchanged for access token and refresh token
3. **Token Storage**: Refresh token is securely stored in system keyring
4. **Automatic Refresh**: Access token is automatically refreshed when needed
5. **Secure Access**: All API calls use the current access token

### Credential Storage

Credentials are stored securely using the `keyring` library:

- **Linux**: Uses Secret Service API (GNOME Keyring, KWallet)
- **macOS**: Uses Keychain
- **Windows**: Uses Windows Credential Locker

Data stored:
- Client ID (Consumer Key)
- Account ID
- Refresh Token (encrypted by the OS)

**Note**: Access tokens are never stored permanently; they're kept in memory and refreshed as needed.

## Usage Examples

### Get a Stock Quote

```bash
python3 options_trader.py --quote AAPL
```

### Get Option Chain

```bash
python3 options_trader.py --chain AAPL
```

### View Current Positions

```bash
python3 options_trader.py --positions
```

### View Recent Orders

```bash
python3 options_trader.py --orders
```

### View Account Information

```bash
python3 options_trader.py --account
```

### Using as a Python Module

```python
from options_trader import TDAmeritradeAPI, OptionsStrategy

# Initialize API (uses stored credentials)
api = TDAmeritradeAPI()
api.authenticate()

# Get a quote
quote = api.get_quote('AAPL')
print(quote)

# Get option chain
chain = api.get_option_chain('AAPL', contract_type='CALL', strike_count=5)

# Get account positions
positions = api.get_positions()
for position in positions:
    symbol = position['instrument']['symbol']
    quantity = position['longQuantity'] - position['shortQuantity']
    print(f"{symbol}: {quantity} shares/contracts")

# Place an order (example - use with caution!)
order = {
    'orderType': 'LIMIT',
    'session': 'NORMAL',
    'duration': 'DAY',
    'price': 1.50,
    'orderStrategyType': 'SINGLE',
    'orderLegCollection': [{
        'instruction': 'BUY_TO_OPEN',
        'quantity': 1,
        'instrument': {
            'symbol': 'AAPL_100121C150',  # Example option symbol
            'assetType': 'OPTION'
        }
    }]
}
# api.place_order(order)  # Uncomment to actually place order
```

## Trading Strategies

### Overview

The script includes an `OptionsStrategy` class that provides methods for analyzing options and implementing various trading strategies.

### Supported Strategies

#### 1. Vertical Spreads

**Bull Call Spread**:
- Buy lower strike call
- Sell higher strike call
- Same expiration date
- Intention: Profit from moderate upward move with limited risk

**Bear Put Spread**:
- Buy higher strike put
- Sell lower strike put
- Same expiration date
- Intention: Profit from moderate downward move with limited risk

#### 2. Iron Condor

- Sell out-of-the-money call spread
- Sell out-of-the-money put spread
- Same expiration date
- Intention: Profit from low volatility, price staying in range

### Strategy Implementation Example

```python
from options_trader import TDAmeritradeAPI, OptionsStrategy

api = TDAmeritradeAPI()
api.authenticate()

# Initialize strategy with 2% risk per trade
strategy = OptionsStrategy(api, risk_per_trade=0.02)

# Find vertical spread opportunities
opportunities = strategy.find_opportunities(
    symbol='SPY',
    strategy_type='vertical_spread',
    max_dte=45,  # Maximum 45 days to expiration
    min_dte=7    # Minimum 7 days to expiration
)

# Analyze specific option
option_data = {...}  # Get from option chain
analysis = strategy.analyze_option(option_data)

print(f"Liquidity Score: {analysis['liquidity_score']}")
print(f"Implied Volatility: {analysis['implied_volatility']}")
print(f"Delta: {analysis['delta']}")
```

## Risk Management

### Key Principles

1. **Position Sizing**
   - Never risk more than 2% of account on a single trade
   - Adjust position size based on account value
   - Consider maximum loss before entering trade

2. **Diversification**
   - Don't concentrate positions in single underlying
   - Use different expiration dates
   - Mix strategies (spreads, condors, etc.)

3. **Stop Losses**
   - Set maximum loss threshold (e.g., 50% of credit received)
   - Use stop-loss orders or mental stops
   - Exit losing trades before expiration if needed

4. **Profit Targets**
   - Take profits at 50-75% of maximum gain
   - Don't wait for full profit potential
   - Use limit orders to automate profit taking

5. **Expiration Management**
   - Close positions before expiration to avoid assignment risk
   - Roll positions if still bullish/bearish on trade
   - Don't hold short options into expiration

### Risk Calculation Example

```python
# Calculate position size based on account risk
account_value = 50000  # $50,000 account
risk_per_trade = 0.02  # 2% risk per trade
max_risk = account_value * risk_per_trade  # $1,000

# For a vertical spread with $500 max loss
max_loss_per_contract = 500  # $5 wide spread at $0 credit
contracts = max_risk / max_loss_per_contract  # 2 contracts
```

### Trading Rules

1. **Entry Rules**
   - Only enter trades with positive expected value
   - Ensure sufficient liquidity (volume > 100, open interest > 1000)
   - Verify bid-ask spread is reasonable (< 10% of option price)
   - Check implied volatility rank/percentile

2. **Exit Rules**
   - Exit at profit target (50-75% max gain)
   - Exit at stop loss (50% of credit or less)
   - Exit 7-14 days before expiration
   - Exit if underlying breaks key technical levels

3. **Adjustment Rules**
   - Consider rolling if position moves against you
   - Don't add to losing positions
   - Adjust only if maintaining positive expected value

## API Reference

### TDAmeritradeAPI Class

#### Methods

**`__init__(client_id=None, account_id=None)`**
- Initialize API client
- Parameters:
  - `client_id`: TD Ameritrade Consumer Key
  - `account_id`: TD Ameritrade account number

**`save_credentials(client_id, account_id, refresh_token=None)`**
- Save credentials to keyring
- Returns: `True` if successful

**`authenticate(authorization_code=None)`**
- Authenticate with TD Ameritrade
- Parameters:
  - `authorization_code`: OAuth authorization code (for initial auth)
- Returns: `True` if authenticated

**`get_quote(symbol)`**
- Get real-time quote
- Parameters:
  - `symbol`: Stock or option symbol
- Returns: Quote data dictionary

**`get_option_chain(symbol, contract_type='ALL', strike_count=10, ...)`**
- Get option chain data
- Parameters:
  - `symbol`: Underlying symbol
  - `contract_type`: 'CALL', 'PUT', or 'ALL'
  - `strike_count`: Number of strikes
  - `include_quotes`: Include quote data
  - `from_date`: Start date (YYYY-MM-DD)
  - `to_date`: End date (YYYY-MM-DD)
- Returns: Option chain dictionary

**`get_account_info(fields=None)`**
- Get account information
- Parameters:
  - `fields`: Optional fields (positions, orders)
- Returns: Account data dictionary

**`get_positions()`**
- Get current positions
- Returns: List of position dictionaries

**`place_order(order)`**
- Place trading order
- Parameters:
  - `order`: Order specification dictionary
- Returns: `True` if successful

**`get_orders(max_results=10, from_date=None, to_date=None, status=None)`**
- Get order history
- Returns: List of order dictionaries

**`cancel_order(order_id)`**
- Cancel an order
- Parameters:
  - `order_id`: Order ID to cancel
- Returns: `True` if successful

### OptionsStrategy Class

**`__init__(api, risk_per_trade=0.02)`**
- Initialize strategy
- Parameters:
  - `api`: TDAmeritradeAPI instance
  - `risk_per_trade`: Risk per trade (0.02 = 2%)

**`analyze_option(option_data)`**
- Analyze option contract
- Parameters:
  - `option_data`: Option data from API
- Returns: Analysis dictionary with metrics

**`find_opportunities(symbol, strategy_type, max_dte=45, min_dte=7)`**
- Find trading opportunities
- Parameters:
  - `symbol`: Underlying symbol
  - `strategy_type`: 'vertical_spread', 'iron_condor'
  - `max_dte`: Max days to expiration
  - `min_dte`: Min days to expiration
- Returns: List of opportunities

**`create_order(order_type, symbol, quantity, price, **kwargs)`**
- Create order object
- Parameters:
  - `order_type`: 'MARKET', 'LIMIT', etc.
  - `symbol`: Option symbol
  - `quantity`: Number of contracts
  - `price`: Limit price
- Returns: Order dictionary

## Troubleshooting

### Authentication Issues

**Problem**: "Client ID not provided"
- **Solution**: Run `python3 options_trader.py --setup` to configure credentials

**Problem**: "Error refreshing access token"
- **Solution**: Run setup again to get new refresh token

**Problem**: "Authentication failed"
- **Solution**: 
  - Verify Client ID is correct
  - Ensure callback URL is exactly `https://localhost`
  - Check that authorization code hasn't expired (use within 30 seconds)

### API Request Issues

**Problem**: "API request failed: 401 Unauthorized"
- **Solution**: Re-authenticate using `--setup`

**Problem**: "API request failed: 403 Forbidden"
- **Solution**: 
  - Verify account has API access enabled
  - Check that account ID is correct
  - Ensure account has options trading approval

**Problem**: "API request failed: 429 Too Many Requests"
- **Solution**: Reduce request frequency, implement rate limiting

### Keyring Issues

**Problem**: "No keyring backend available"
- **Solution**: 
  - Linux: Install `gnome-keyring` or similar
  - macOS: Keychain should be available by default
  - Windows: Windows Credential Locker should be available

**Problem**: "Error storing credential in keyring"
- **Solution**: 
  - Check keyring service is running
  - Ensure you have permission to access keyring
  - Try `keyring --list-backends` to see available backends

## Security Best Practices

### Credential Management

1. **Never Hard-Code Credentials**
   - Always use keyring for storage
   - Never commit credentials to version control
   - Don't share credentials

2. **Protect Your API Keys**
   - Treat Client ID as sensitive
   - Don't expose in public repositories
   - Rotate keys if compromised

3. **Monitor Access**
   - Review API access logs regularly
   - Watch for unauthorized access attempts
   - Enable two-factor authentication on TD Ameritrade account

### Trading Security

1. **Start Small**
   - Test with small positions first
   - Verify order execution before scaling up
   - Use paper trading if available

2. **Review Orders**
   - Always review order details before submission
   - Double-check symbol, quantity, and price
   - Understand maximum risk before entering

3. **Monitor Positions**
   - Check positions regularly
   - Set price alerts
   - Have exit plan before entering

4. **Secure Your System**
   - Keep Python and dependencies updated
   - Use strong passwords
   - Enable system encryption
   - Log out when not in use

### API Usage

1. **Rate Limiting**
   - TD Ameritrade has API rate limits
   - Don't make excessive requests
   - Implement exponential backoff on errors

2. **Error Handling**
   - Always check API response
   - Handle errors gracefully
   - Log all API interactions

3. **Testing**
   - Test thoroughly with small positions
   - Verify calculations before live trading
   - Use paper trading accounts when possible

## Generating Gains: Strategy Intent

### Core Philosophy

The intention of this API integration is to enable **systematic, disciplined options trading** with proper risk management. The goal is to generate consistent gains through:

1. **Premium Collection Strategies**
   - Selling options with positive expected value
   - Capturing time decay (theta)
   - Exploiting high implied volatility

2. **Directional Strategies**
   - Using spreads to limit risk
   - Defining maximum loss before entry
   - Taking profits systematically

3. **Market Neutral Strategies**
   - Iron condors for range-bound markets
   - Balancing delta across positions
   - Profiting from volatility contraction

### Expected Returns

With proper risk management:
- **Conservative Target**: 1-2% per month
- **Moderate Target**: 2-4% per month
- **Aggressive Target**: 4-6% per month

**Note**: Higher returns come with higher risk. Always prioritize capital preservation.

### Success Factors

1. **Consistency**: Execute trades according to plan
2. **Discipline**: Follow risk management rules
3. **Patience**: Don't force trades
4. **Learning**: Review and improve continuously
5. **Adaptation**: Adjust to market conditions

### Risk Disclosure

**Options trading involves substantial risk and is not suitable for all investors.**

- You can lose 100% of your investment
- Options can expire worthless
- High leverage amplifies both gains and losses
- Market conditions can change rapidly
- Past performance doesn't guarantee future results

**Always**:
- Understand the risks before trading
- Only risk capital you can afford to lose
- Consult with financial advisors
- Start small and scale gradually
- Maintain emergency funds outside trading account

## Additional Resources

### TD Ameritrade Resources

- [Developer Portal](https://developer.tdameritrade.com/)
- [API Documentation](https://developer.tdameritrade.com/apis)
- [Options Education](https://www.tdameritrade.com/education/options.html)

### Options Trading Education

- Options Playbook: [optionsplaybook.com](https://www.optionsplaybook.com/)
- CBOE Education: [cboe.com/education](https://www.cboe.com/education/)
- OIC: [optionseducation.org](https://www.optionseducation.org/)

### Python and API

- Requests Documentation: [docs.python-requests.org](https://docs.python-requests.org/)
- Keyring Documentation: [keyring.readthedocs.io](https://keyring.readthedocs.io/)

## License

This script is provided under the same license as the repository. See LICENSE file for details.

## Disclaimer

This software is for educational purposes only. The authors and contributors are not responsible for any trading losses. Always consult with qualified financial advisors before making investment decisions.

**USE AT YOUR OWN RISK.**
