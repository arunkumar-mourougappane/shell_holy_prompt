#!/usr/bin/env python3
"""
Options Trading Script for ThinkorSwim/TD Ameritrade API

This script provides a secure interface to TD Ameritrade's API for options trading.
It uses keyring for secure credential storage and implements basic trading operations.

Author: Arun Kumar Mourougappane
License: See LICENSE file
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import keyring
from requests.auth import HTTPBasicAuth


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('options_trader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TDAmeritradeAPI:
    """
    TD Ameritrade API client for options trading.
    
    This class handles authentication, credential management, and trading operations
    using the TD Ameritrade API (which powers ThinkorSwim).
    """
    
    BASE_URL = "https://api.tdameritrade.com/v1"
    AUTH_URL = "https://auth.tdameritrade.com/auth"
    TOKEN_URL = "https://api.tdameritrade.com/v1/oauth2/token"
    
    # Keyring service name for storing credentials
    KEYRING_SERVICE = "thinkorswim_api"
    
    def __init__(self, client_id: Optional[str] = None, account_id: Optional[str] = None):
        """
        Initialize the TD Ameritrade API client.
        
        Args:
            client_id: TD Ameritrade API client ID (Consumer Key)
            account_id: TD Ameritrade account ID
        """
        self.client_id = client_id
        self.account_id = account_id
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        
        # Load credentials from keyring if not provided
        if not self.client_id:
            self.client_id = self._get_credential('client_id')
        if not self.account_id:
            self.account_id = self._get_credential('account_id')
    
    def _get_credential(self, key: str) -> Optional[str]:
        """
        Retrieve credential from keyring.
        
        Args:
            key: Credential key name
            
        Returns:
            Credential value or None if not found
        """
        try:
            value = keyring.get_password(self.KEYRING_SERVICE, key)
            if value:
                logger.debug(f"Retrieved {key} from keyring")
            return value
        except Exception as e:
            logger.error(f"Error retrieving {key} from keyring: {e}")
            return None
    
    def _set_credential(self, key: str, value: str) -> bool:
        """
        Store credential in keyring.
        
        Args:
            key: Credential key name
            value: Credential value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            keyring.set_password(self.KEYRING_SERVICE, key, value)
            logger.info(f"Stored {key} in keyring")
            return True
        except Exception as e:
            logger.error(f"Error storing {key} in keyring: {e}")
            return False
    
    def save_credentials(self, client_id: str, account_id: str, 
                        refresh_token: Optional[str] = None) -> bool:
        """
        Save credentials to secure keyring storage.
        
        Args:
            client_id: TD Ameritrade API client ID
            account_id: TD Ameritrade account ID
            refresh_token: Optional refresh token for OAuth
            
        Returns:
            True if all credentials saved successfully
        """
        success = True
        success &= self._set_credential('client_id', client_id)
        success &= self._set_credential('account_id', account_id)
        
        if refresh_token:
            success &= self._set_credential('refresh_token', refresh_token)
        
        if success:
            self.client_id = client_id
            self.account_id = account_id
            self.refresh_token = refresh_token
            logger.info("Credentials saved successfully")
        
        return success
    
    def authenticate(self, authorization_code: Optional[str] = None) -> bool:
        """
        Authenticate with TD Ameritrade API using OAuth 2.0.
        
        Args:
            authorization_code: Authorization code from OAuth flow (for initial auth)
            
        Returns:
            True if authentication successful
        """
        if not self.client_id:
            logger.error("Client ID not provided. Cannot authenticate.")
            return False
        
        # Try to use refresh token first if available
        if not authorization_code:
            self.refresh_token = self._get_credential('refresh_token')
            if self.refresh_token:
                return self._refresh_access_token()
        
        # Use authorization code for initial authentication
        if authorization_code:
            return self._get_access_token(authorization_code)
        
        logger.error("No authorization code or refresh token available for authentication")
        return False
    
    def _get_access_token(self, authorization_code: str) -> bool:
        """
        Get access token using authorization code.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            
        Returns:
            True if token retrieved successfully
        """
        try:
            data = {
                'grant_type': 'authorization_code',
                'access_type': 'offline',
                'code': authorization_code,
                'client_id': f"{self.client_id}@AMER.OAUTHAP",
                'redirect_uri': 'https://localhost'
            }
            
            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 1800)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            # Save refresh token to keyring
            if self.refresh_token:
                self._set_credential('refresh_token', self.refresh_token)
            
            logger.info("Successfully authenticated with TD Ameritrade API")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting access token: {e}")
            return False
    
    def _refresh_access_token(self) -> bool:
        """
        Refresh access token using refresh token.
        
        Returns:
            True if token refreshed successfully
        """
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
        
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': f"{self.client_id}@AMER.OAUTHAP"
            }
            
            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 1800)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Successfully refreshed access token")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing access token: {e}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """
        Ensure we have a valid access token, refreshing if necessary.
        
        Returns:
            True if authenticated
        """
        if not self.access_token or not self.token_expiry:
            return self.authenticate()
        
        # Refresh token if it expires in less than 5 minutes
        if datetime.now() >= self.token_expiry - timedelta(minutes=5):
            return self._refresh_access_token()
        
        return True
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        Make authenticated API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data or None on error
        """
        if not self._ensure_authenticated():
            logger.error("Not authenticated. Cannot make request.")
            return None
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f"Bearer {self.access_token}"
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time quote for a symbol.
        
        Args:
            symbol: Stock or option symbol
            
        Returns:
            Quote data or None on error
        """
        endpoint = f"/marketdata/{symbol}/quotes"
        return self._make_request('GET', endpoint)
    
    def get_option_chain(self, symbol: str, contract_type: str = 'ALL',
                         strike_count: int = 10, include_quotes: bool = True,
                         from_date: Optional[str] = None,
                         to_date: Optional[str] = None) -> Optional[Dict]:
        """
        Get option chain for a symbol.
        
        Args:
            symbol: Underlying symbol
            contract_type: 'CALL', 'PUT', or 'ALL'
            strike_count: Number of strikes to return
            include_quotes: Include quote data
            from_date: Start date for expiration (YYYY-MM-DD)
            to_date: End date for expiration (YYYY-MM-DD)
            
        Returns:
            Option chain data or None on error
        """
        params = {
            'symbol': symbol,
            'contractType': contract_type,
            'strikeCount': strike_count,
            'includeQuotes': str(include_quotes).upper()
        }
        
        if from_date:
            params['fromDate'] = from_date
        if to_date:
            params['toDate'] = to_date
        
        endpoint = "/marketdata/chains"
        return self._make_request('GET', endpoint, params=params)
    
    def get_account_info(self, fields: Optional[str] = None) -> Optional[Dict]:
        """
        Get account information.
        
        Args:
            fields: Optional comma-separated list of fields
                   (positions, orders, etc.)
            
        Returns:
            Account data or None on error
        """
        if not self.account_id:
            logger.error("Account ID not set")
            return None
        
        endpoint = f"/accounts/{self.account_id}"
        params = {}
        if fields:
            params['fields'] = fields
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_positions(self) -> Optional[List[Dict]]:
        """
        Get current positions.
        
        Returns:
            List of positions or None on error
        """
        account_data = self.get_account_info(fields='positions')
        if account_data and 'securitiesAccount' in account_data:
            return account_data['securitiesAccount'].get('positions', [])
        return None
    
    def place_order(self, order: Dict) -> bool:
        """
        Place a trading order.
        
        Args:
            order: Order specification dict following TD Ameritrade format
            
        Returns:
            True if order placed successfully
        """
        if not self.account_id:
            logger.error("Account ID not set")
            return False
        
        endpoint = f"/accounts/{self.account_id}/orders"
        response = self._make_request('POST', endpoint, json=order)
        
        if response is not None:
            logger.info(f"Order placed successfully")
            return True
        return False
    
    def get_orders(self, max_results: int = 10, 
                   from_date: Optional[str] = None,
                   to_date: Optional[str] = None,
                   status: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Get orders for the account.
        
        Args:
            max_results: Maximum number of orders to return
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            status: Order status filter
            
        Returns:
            List of orders or None on error
        """
        if not self.account_id:
            logger.error("Account ID not set")
            return None
        
        endpoint = f"/accounts/{self.account_id}/orders"
        params = {'maxResults': max_results}
        
        if from_date:
            params['fromEnteredTime'] = from_date
        if to_date:
            params['toEnteredTime'] = to_date
        if status:
            params['status'] = status
        
        return self._make_request('GET', endpoint, params=params)
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        if not self.account_id:
            logger.error("Account ID not set")
            return False
        
        endpoint = f"/accounts/{self.account_id}/orders/{order_id}"
        response = self._make_request('DELETE', endpoint)
        
        if response is not None:
            logger.info(f"Order {order_id} cancelled successfully")
            return True
        return False


class OptionsStrategy:
    """
    Options trading strategy implementation.
    
    This class provides methods for analyzing options and generating trading signals
    with risk management.
    """
    
    def __init__(self, api: TDAmeritradeAPI, risk_per_trade: float = 0.02):
        """
        Initialize options strategy.
        
        Args:
            api: TDAmeritradeAPI instance
            risk_per_trade: Maximum risk per trade as fraction of account (default 2%)
        """
        self.api = api
        self.risk_per_trade = risk_per_trade
    
    def analyze_option(self, option_data: Dict) -> Dict[str, Any]:
        """
        Analyze an option contract.
        
        Args:
            option_data: Option data from API
            
        Returns:
            Analysis results with risk metrics
        """
        analysis = {
            'symbol': option_data.get('symbol', 'N/A'),
            'strike': option_data.get('strikePrice', 0),
            'expiration': option_data.get('expirationDate', 'N/A'),
            'bid': option_data.get('bid', 0),
            'ask': option_data.get('ask', 0),
            'last': option_data.get('last', 0),
            'volume': option_data.get('totalVolume', 0),
            'open_interest': option_data.get('openInterest', 0),
            'implied_volatility': option_data.get('volatility', 0),
            'delta': option_data.get('delta', 0),
            'gamma': option_data.get('gamma', 0),
            'theta': option_data.get('theta', 0),
            'vega': option_data.get('vega', 0)
        }
        
        # Calculate mid price
        if analysis['bid'] and analysis['ask']:
            analysis['mid_price'] = (analysis['bid'] + analysis['ask']) / 2
        else:
            analysis['mid_price'] = analysis['last']
        
        # Liquidity score (0-100)
        volume_score = min(analysis['volume'] / 100, 1) * 50
        oi_score = min(analysis['open_interest'] / 1000, 1) * 50
        analysis['liquidity_score'] = volume_score + oi_score
        
        return analysis
    
    def find_opportunities(self, symbol: str, strategy_type: str = 'vertical_spread',
                          max_dte: int = 45, min_dte: int = 7) -> List[Dict]:
        """
        Find trading opportunities based on strategy.
        
        Args:
            symbol: Underlying symbol
            strategy_type: Type of strategy (vertical_spread, iron_condor, etc.)
            max_dte: Maximum days to expiration
            min_dte: Minimum days to expiration
            
        Returns:
            List of trade opportunities
        """
        opportunities = []
        
        # Get option chain
        today = datetime.now()
        from_date = (today + timedelta(days=min_dte)).strftime('%Y-%m-%d')
        to_date = (today + timedelta(days=max_dte)).strftime('%Y-%m-%d')
        
        chain_data = self.api.get_option_chain(
            symbol=symbol,
            from_date=from_date,
            to_date=to_date
        )
        
        if not chain_data:
            logger.error("Failed to get option chain")
            return opportunities
        
        # Implement strategy-specific logic
        if strategy_type == 'vertical_spread':
            opportunities = self._find_vertical_spreads(chain_data)
        elif strategy_type == 'iron_condor':
            opportunities = self._find_iron_condors(chain_data)
        
        return opportunities
    
    def _find_vertical_spreads(self, chain_data: Dict) -> List[Dict]:
        """
        Find vertical spread opportunities.
        
        Args:
            chain_data: Option chain data
            
        Returns:
            List of vertical spread opportunities
        """
        opportunities = []
        
        # This is a simplified example
        # In production, you would implement more sophisticated analysis
        
        logger.info("Analyzing vertical spread opportunities")
        
        # Add your vertical spread logic here
        # Example: Find bull call spreads or bear put spreads
        
        return opportunities
    
    def _find_iron_condors(self, chain_data: Dict) -> List[Dict]:
        """
        Find iron condor opportunities.
        
        Args:
            chain_data: Option chain data
            
        Returns:
            List of iron condor opportunities
        """
        opportunities = []
        
        logger.info("Analyzing iron condor opportunities")
        
        # Add your iron condor logic here
        
        return opportunities
    
    def create_order(self, order_type: str, symbol: str, quantity: int,
                     price: float, **kwargs) -> Dict:
        """
        Create an order object for submission.
        
        Args:
            order_type: Order type (MARKET, LIMIT, STOP, etc.)
            symbol: Option symbol
            quantity: Number of contracts
            price: Price for limit orders
            **kwargs: Additional order parameters
            
        Returns:
            Order object ready for submission
        """
        order = {
            'orderType': order_type,
            'session': kwargs.get('session', 'NORMAL'),
            'duration': kwargs.get('duration', 'DAY'),
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [
                {
                    'instruction': kwargs.get('instruction', 'BUY_TO_OPEN'),
                    'quantity': quantity,
                    'instrument': {
                        'symbol': symbol,
                        'assetType': 'OPTION'
                    }
                }
            ]
        }
        
        if order_type == 'LIMIT':
            order['price'] = price
        
        return order


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Options Trading Script for ThinkorSwim/TD Ameritrade API'
    )
    parser.add_argument('--setup', action='store_true',
                       help='Setup and save credentials')
    parser.add_argument('--quote', type=str,
                       help='Get quote for symbol')
    parser.add_argument('--chain', type=str,
                       help='Get option chain for symbol')
    parser.add_argument('--positions', action='store_true',
                       help='Show current positions')
    parser.add_argument('--orders', action='store_true',
                       help='Show recent orders')
    parser.add_argument('--account', action='store_true',
                       help='Show account information')
    
    args = parser.parse_args()
    
    if args.setup:
        print("=== TD Ameritrade API Setup ===")
        print("\nTo use this script, you need:")
        print("1. TD Ameritrade account")
        print("2. Developer API account at https://developer.tdameritrade.com/")
        print("3. Create an app and get your Consumer Key (Client ID)")
        print()
        
        client_id = input("Enter your Client ID (Consumer Key): ").strip()
        account_id = input("Enter your Account ID: ").strip()
        
        print("\nYou need to authorize this application:")
        auth_url = (
            f"https://auth.tdameritrade.com/auth?"
            f"response_type=code&"
            f"redirect_uri=https://localhost&"
            f"client_id={client_id}%40AMER.OAUTHAP"
        )
        print(f"\n1. Visit this URL:\n{auth_url}")
        print("\n2. Login and authorize the application")
        print("3. You'll be redirected to localhost with a code parameter")
        print("4. Copy the entire URL you were redirected to")
        print()
        
        redirect_url = input("Paste the redirect URL here: ").strip()
        
        # Extract authorization code from URL
        if 'code=' in redirect_url:
            auth_code = redirect_url.split('code=')[1].split('&')[0]
            auth_code = auth_code.replace('%40', '@')  # URL decode
            
            api = TDAmeritradeAPI(client_id=client_id, account_id=account_id)
            
            if api.authenticate(authorization_code=auth_code):
                if api.save_credentials(client_id, account_id, api.refresh_token):
                    print("\n✓ Credentials saved successfully!")
                    print("You can now use the script for trading.")
                else:
                    print("\n✗ Failed to save credentials")
            else:
                print("\n✗ Authentication failed")
        else:
            print("\n✗ Invalid redirect URL. No authorization code found.")
        
        return
    
    # Initialize API with saved credentials
    api = TDAmeritradeAPI()
    
    if not api.authenticate():
        print("Authentication failed. Run with --setup to configure credentials.")
        return
    
    if args.quote:
        quote = api.get_quote(args.quote)
        if quote:
            print(json.dumps(quote, indent=2))
    
    elif args.chain:
        chain = api.get_option_chain(args.chain)
        if chain:
            print(json.dumps(chain, indent=2))
    
    elif args.positions:
        positions = api.get_positions()
        if positions:
            print("\n=== Current Positions ===")
            for pos in positions:
                print(f"\nSymbol: {pos.get('instrument', {}).get('symbol', 'N/A')}")
                print(f"Quantity: {pos.get('longQuantity', 0) - pos.get('shortQuantity', 0)}")
                print(f"Market Value: ${pos.get('marketValue', 0):,.2f}")
        else:
            print("No positions found")
    
    elif args.orders:
        orders = api.get_orders()
        if orders:
            print("\n=== Recent Orders ===")
            for order in orders:
                print(f"\nOrder ID: {order.get('orderId', 'N/A')}")
                print(f"Status: {order.get('status', 'N/A')}")
                print(f"Entered: {order.get('enteredTime', 'N/A')}")
        else:
            print("No orders found")
    
    elif args.account:
        account = api.get_account_info()
        if account:
            print(json.dumps(account, indent=2))


if __name__ == '__main__':
    main()
