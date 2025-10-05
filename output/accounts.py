import datetime
from typing import Dict, List, Any

# Helper Function
def get_share_price(symbol: str) -> float:
    """
    Simulates fetching the current market price for a given share symbol.
    This is a *test implementation* for demonstration purposes and would typically
    be replaced by an external API call in a production environment.

    Arguments:
        symbol (str): The stock ticker symbol (e.g., 'AAPL', 'TSLA', 'GOOGL').

    Returns:
        float: The current price of the share.

    Raises:
        ValueError: If the symbol is not recognized in the test data.

    Test Implementation Details:
    Returns fixed prices for 'AAPL' ($170.00), 'TSLA' ($250.00), and 'GOOGL' ($140.00).
    Other symbols will raise a `ValueError`.
    """
    prices = {
        'AAPL': 170.00,
        'TSLA': 250.00,
        'GOOGL': 140.00,
    }
    upper_symbol = symbol.upper()
    if upper_symbol not in prices:
        raise ValueError(f"Share symbol '{symbol}' not recognized in test data.")
    return prices[upper_symbol]


class Account:
    """
    Manages a single user's trading simulation account. It encapsulates the user's
    cash balance, share holdings, and a history of all financial and trading transactions.
    It also provides methods to calculate portfolio value and profit/loss.
    """

    def __init__(self, account_id: str):
        """
        Initializes a new trading account with a unique identifier.
        Sets up initial cash balance, holdings, and an empty transaction history.

        Arguments:
            account_id (str): A unique string identifier for the account.

        Raises:
            ValueError: If the `account_id` is empty.
        """
        if not account_id:
            raise ValueError("Account ID cannot be empty.")

        self._account_id: str = account_id
        self._balance: float = 0.0
        self._holdings: Dict[str, int] = {}
        self._transactions: List[Dict[str, Any]] = []
        self._total_deposits_sum: float = 0.0
        self._total_withdrawals_sum: float = 0.0

        self._record_transaction(type='account_created', initial_balance=self._balance)

    def _record_transaction(self, type: str, **kwargs):
        """
        A private helper method to record details of a transaction into the `_transactions` list.
        It automatically adds a timestamp and the account ID.

        Arguments:
            type (str): The type of transaction (e.g., 'account_created', 'deposit',
                        'withdraw', 'buy', 'sell').
            **kwargs: Additional key-value pairs specific to the transaction type
                      (e.g., `amount`, `symbol`, `quantity`, `price_per_share`,
                      `current_balance`).
        """
        transaction = {
            'timestamp': datetime.datetime.now().isoformat(),
            'account_id': self._account_id,
            'type': type,
            **kwargs,
            'current_balance': self._balance # Always include current balance at the time of transaction
        }
        self._transactions.append(transaction)

    def deposit(self, amount: float):
        """
        Deposits funds into the account, increasing the cash balance and tracking the total deposits.

        Arguments:
            amount (float): The amount of money to deposit. Must be a positive number.

        Raises:
            ValueError: If the `amount` is not positive.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self._balance += amount
        self._total_deposits_sum += amount
        self._record_transaction(type='deposit', amount=amount)

    def withdraw(self, amount: float):
        """
        Withdraws funds from the account, decreasing the cash balance and tracking total withdrawals.
        Prevents withdrawals that would lead to a negative balance.

        Arguments:
            amount (float): The amount of money to withdraw. Must be a positive number.

        Raises:
            ValueError: If the `amount` is not positive or if there are insufficient funds.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self._balance - amount < 0:
            raise ValueError("Insufficient funds for withdrawal.")
        self._balance -= amount
        self._total_withdrawals_sum += amount
        self._record_transaction(type='withdraw', amount=amount)

    def buy_shares(self, symbol: str, quantity: int):
        """
        Buys a specified quantity of shares for a given symbol. The cost is deducted
        from the cash balance. Prevents buying if insufficient funds are available.

        Arguments:
            symbol (str): The stock ticker symbol (will be converted to uppercase for internal storage).
            quantity (int): The number of shares to buy. Must be a positive integer.

        Raises:
            ValueError: If `quantity` is not positive, if the symbol price is unavailable
                        (from `get_share_price`), or if there are insufficient funds.
        """
        if quantity <= 0:
            raise ValueError("Quantity of shares to buy must be positive.")

        upper_symbol = symbol.upper()
        try:
            price_per_share = get_share_price(upper_symbol)
        except ValueError as e:
            raise ValueError(f"Cannot buy shares: {e}")

        total_cost = price_per_share * quantity

        if self._balance < total_cost:
            raise ValueError("Insufficient funds to buy shares.")

        self._balance -= total_cost
        self._holdings[upper_symbol] = self._holdings.get(upper_symbol, 0) + quantity
        self._record_transaction(type='buy', symbol=upper_symbol, quantity=quantity,
                                 price_per_share=price_per_share, total_cost=total_cost)

    def sell_shares(self, symbol: str, quantity: int):
        """
        Sells a specified quantity of shares for a given symbol. The revenue is added
        to the cash balance. Prevents selling shares that the user does not own or
        more shares than they hold.

        Arguments:
            symbol (str): The stock ticker symbol (will be converted to uppercase for internal storage).
            quantity (int): The number of shares to sell. Must be a positive integer.

        Raises:
            ValueError: If `quantity` is not positive, if the symbol price is unavailable
                        (from `get_share_price`), or if the user does not own enough shares of that symbol.
        """
        if quantity <= 0:
            raise ValueError("Quantity of shares to sell must be positive.")

        upper_symbol = symbol.upper()

        if upper_symbol not in self._holdings or self._holdings[upper_symbol] < quantity:
            raise ValueError(f"Cannot sell {quantity} shares of {upper_symbol}: Insufficient holdings.")

        try:
            price_per_share = get_share_price(upper_symbol)
        except ValueError as e:
            raise ValueError(f"Cannot sell shares: {e}")

        total_revenue = price_per_share * quantity

        self._balance += total_revenue
        self._holdings[upper_symbol] -= quantity
        if self._holdings[upper_symbol] == 0:
            del self._holdings[upper_symbol] # Remove if no shares left

        self._record_transaction(type='sell', symbol=upper_symbol, quantity=quantity,
                                 price_per_share=price_per_share, total_revenue=total_revenue)

    def get_balance(self) -> float:
        """
        Returns the current cash balance in the account.

        Returns:
            float: The current cash balance.
        """
        return self._balance

    def get_holdings(self) -> Dict[str, int]:
        """
        Returns a copy of the current share holdings in the account.

        Returns:
            Dict[str, int]: A dictionary where keys are stock symbols (uppercase) and values are the quantities held.
        """
        return self._holdings.copy()

    def get_portfolio_value(self) -> float:
        """
        Calculates and returns the total value of the portfolio.
        This includes the current cash balance plus the current market value of all
        held shares, based on `get_share_price`.

        Returns:
            float: The total portfolio value.
        """
        portfolio_value = self._balance
        for symbol, quantity in self._holdings.items():
            try:
                price = get_share_price(symbol)
                portfolio_value += price * quantity
            except ValueError:
                # If a share price is unavailable, we don't include its value
                # but also don't crash. A more robust system might log this.
                pass
        return portfolio_value

    def get_profit_loss(self) -> float:
        """
        Calculates the current profit or loss of the portfolio.
        This is determined by subtracting the *net capital injected*
        (total deposits minus total withdrawals) from the current `get_portfolio_value()`.

        Returns:
            float: The profit or loss. A positive value indicates profit, a negative value indicates loss.
        """
        net_capital_injected = self._total_deposits_sum - self._total_withdrawals_sum
        current_portfolio_value = self.get_portfolio_value()
        return current_portfolio_value - net_capital_injected

    def get_transactions(self) -> List[Dict[str, Any]]:
        """
        Returns a chronological list of all transactions made on this account.
        Each transaction is represented as a dictionary.

        Returns:
            List[Dict[str, Any]]: A list of transaction dictionaries. The list is a copy to prevent external modification of the internal transaction log.
        """
        return self._transactions.copy()