from datetime import datetime
from typing import Dict, List, Optional

def get_share_price(symbol: str) -> float:
    """Returns the current price of a share for testing purposes.
    
    Args:
        symbol: The stock symbol for which the share price is requested.
        
    Returns:
        The current price of the stock.
    """
    prices = {
        'AAPL': 150.0,
        'TSLA': 800.0,
        'GOOGL': 2500.0
    }
    return prices.get(symbol, 0.0)

class Account:
    """Class that manages the details and operations for a trading simulation account.
    It maintains the account balance, portfolio holdings, and transaction history.
    """
    
    def __init__(self, user_id: str, initial_deposit: float) -> None:
        """Constructor to initialize a new account with a user ID and an initial deposit.
        
        Args:
            user_id: A unique identifier for the user.
            initial_deposit: The initial funds deposited into the account.
        """
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
            
        self.user_id = user_id
        self.initial_deposit = initial_deposit
        self.balance = initial_deposit
        self.portfolio = {}  # Symbol -> Quantity
        self.transactions = []
        
        # Record the initial deposit as a transaction
        self._record_transaction('DEPOSIT', None, None, initial_deposit, initial_deposit)
    
    def deposit_funds(self, amount: float) -> None:
        """Method to deposit funds into the account.
        
        Args:
            amount: The amount of funds to be deposited.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
            
        self.balance += amount
        self._record_transaction('DEPOSIT', None, None, amount, self.balance)
    
    def withdraw_funds(self, amount: float) -> None:
        """Method to withdraw funds from the account.
        
        Args:
            amount: The amount of funds to be withdrawn.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError(f"Insufficient funds: {self.balance} available, {amount} requested")
            
        self.balance -= amount
        self._record_transaction('WITHDRAW', None, None, amount, self.balance)
    
    def buy_shares(self, symbol: str, quantity: int) -> None:
        """Method to buy shares of a company.
        
        Args:
            symbol: The stock symbol of the company.
            quantity: The number of shares to buy.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        price = get_share_price(symbol)
        if price <= 0:
            raise ValueError(f"Invalid stock symbol: {symbol}")
            
        total_cost = price * quantity
        
        if total_cost > self.balance:
            raise ValueError(f"Insufficient funds: {self.balance} available, {total_cost} required")
        
        # Update balance
        self.balance -= total_cost
        
        # Update portfolio
        if symbol in self.portfolio:
            self.portfolio[symbol] += quantity
        else:
            self.portfolio[symbol] = quantity
        
        self._record_transaction('BUY', symbol, quantity, price, self.balance)
    
    def sell_shares(self, symbol: str, quantity: int) -> None:
        """Method to sell shares of a company.
        
        Args:
            symbol: The stock symbol of the company.
            quantity: The number of shares to sell.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        if symbol not in self.portfolio:
            raise ValueError(f"You don't own any shares of {symbol}")
            
        if self.portfolio[symbol] < quantity:
            raise ValueError(f"Insufficient shares: {self.portfolio[symbol]} owned, {quantity} requested to sell")
        
        price = get_share_price(symbol)
        total_value = price * quantity
        
        # Update balance
        self.balance += total_value
        
        # Update portfolio
        self.portfolio[symbol] -= quantity
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        
        self._record_transaction('SELL', symbol, quantity, price, self.balance)
    
    def get_portfolio_value(self) -> float:
        """Method to calculate and return the total value of the user's portfolio.
        
        Returns:
            The total value of holdings in the portfolio.
        """
        total_value = 0.0
        for symbol, quantity in self.portfolio.items():
            total_value += get_share_price(symbol) * quantity
        return total_value
    
    def get_profit_or_loss(self) -> float:
        """Method to calculate and return the profit or loss from the initial deposit.
        
        Returns:
            The profit or loss calculated from the initial deposit to current state.
        """
        return self.balance + self.get_portfolio_value() - self.initial_deposit
    
    def get_holdings(self) -> Dict[str, int]:
        """Method to return the current holdings of the user.
        
        Returns:
            A dictionary with stock symbols as keys and quantities as values.
        """
        return self.portfolio.copy()
    
    def get_transaction_history(self) -> List[Dict]:
        """Method to return the transaction history of the user.
        
        Returns:
            A list of transaction records, with each record detailing the transaction type,
            symbol, quantity, price, and timestamp.
        """
        return self.transactions.copy()
    
    def _record_transaction(self, transaction_type: str, symbol: Optional[str], 
                           quantity: Optional[int], price: float, balance: float) -> None:
        """Helper method to record a transaction in the transaction history.
        
        Args:
            transaction_type: Type of transaction (DEPOSIT, WITHDRAW, BUY, SELL)
            symbol: The stock symbol (for BUY and SELL transactions)
            quantity: The number of shares (for BUY and SELL transactions)
            price: The price per share or amount for deposit/withdraw
            balance: The account balance after the transaction
        """
        transaction = {
            'type': transaction_type,
            'timestamp': datetime.now().isoformat(),
            'balance': balance
        }
        
        if transaction_type in ['BUY', 'SELL']:
            transaction['symbol'] = symbol
            transaction['quantity'] = quantity
            transaction['price'] = price
            transaction['total'] = price * quantity
        else:  # DEPOSIT or WITHDRAW
            transaction['amount'] = price
        
        self.transactions.append(transaction)