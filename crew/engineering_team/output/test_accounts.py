import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from accounts import Account, get_share_price


class TestGetSharePrice(unittest.TestCase):
    def test_get_valid_share_price(self):
        # Test that valid stock symbols return the correct price
        self.assertEqual(get_share_price('AAPL'), 150.0)
        self.assertEqual(get_share_price('TSLA'), 800.0)
        self.assertEqual(get_share_price('GOOGL'), 2500.0)

    def test_get_invalid_share_price(self):
        # Test that invalid stock symbols return 0.0
        self.assertEqual(get_share_price('INVALID'), 0.0)
        self.assertEqual(get_share_price(''), 0.0)


class TestAccountInitialization(unittest.TestCase):
    def test_init_with_valid_deposit(self):
        account = Account('user123', 1000.0)
        self.assertEqual(account.user_id, 'user123')
        self.assertEqual(account.initial_deposit, 1000.0)
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(account.portfolio, {})
        self.assertEqual(len(account.transactions), 1)
        self.assertEqual(account.transactions[0]['type'], 'DEPOSIT')
        self.assertEqual(account.transactions[0]['amount'], 1000.0)

    def test_init_with_negative_deposit(self):
        # Test that initializing with negative deposit raises ValueError
        with self.assertRaises(ValueError):
            Account('user123', -100.0)


class TestAccountDeposit(unittest.TestCase):
    def setUp(self):
        self.account = Account('user123', 1000.0)

    def test_deposit_valid_amount(self):
        self.account.deposit_funds(500.0)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]['type'], 'DEPOSIT')
        self.assertEqual(self.account.transactions[1]['amount'], 500.0)

    def test_deposit_zero_amount(self):
        with self.assertRaises(ValueError):
            self.account.deposit_funds(0.0)

    def test_deposit_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.deposit_funds(-100.0)


class TestAccountWithdraw(unittest.TestCase):
    def setUp(self):
        self.account = Account('user123', 1000.0)

    def test_withdraw_valid_amount(self):
        self.account.withdraw_funds(500.0)
        self.assertEqual(self.account.balance, 500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]['type'], 'WITHDRAW')
        self.assertEqual(self.account.transactions[1]['amount'], 500.0)

    def test_withdraw_zero_amount(self):
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(0.0)

    def test_withdraw_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(-100.0)

    def test_withdraw_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(1500.0)


class TestAccountBuyShares(unittest.TestCase):
    def setUp(self):
        self.account = Account('user123', 10000.0)

    def test_buy_valid_shares(self):
        self.account.buy_shares('AAPL', 10)
        self.assertEqual(self.account.balance, 8500.0)  # 10000 - (150 * 10)
        self.assertEqual(self.account.portfolio, {'AAPL': 10})
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]['type'], 'BUY')
        self.assertEqual(self.account.transactions[1]['symbol'], 'AAPL')
        self.assertEqual(self.account.transactions[1]['quantity'], 10)

    def test_buy_additional_shares(self):
        self.account.buy_shares('AAPL', 10)
        self.account.buy_shares('AAPL', 5)
        self.assertEqual(self.account.balance, 7750.0)  # 10000 - (150 * 15)
        self.assertEqual(self.account.portfolio, {'AAPL': 15})

    def test_buy_multiple_symbols(self):
        self.account.buy_shares('AAPL', 10)
        self.account.buy_shares('TSLA', 5)
        self.assertEqual(self.account.balance, 4500.0)  # 10000 - (150 * 10) - (800 * 5)
        self.assertEqual(self.account.portfolio, {'AAPL': 10, 'TSLA': 5})

    def test_buy_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 0)

    def test_buy_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', -5)

    def test_buy_invalid_symbol(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares('INVALID', 10)

    def test_buy_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.buy_shares('TSLA', 20)  # 800 * 20 = 16000 > 10000


class TestAccountSellShares(unittest.TestCase):
    def setUp(self):
        self.account = Account('user123', 10000.0)
        self.account.buy_shares('AAPL', 20)  # Balance now 7000.0
        self.account.buy_shares('TSLA', 5)  # Balance now 3000.0

    def test_sell_valid_shares(self):
        self.account.sell_shares('AAPL', 10)
        self.assertEqual(self.account.balance, 4500.0)  # 3000 + (150 * 10)
        self.assertEqual(self.account.portfolio, {'AAPL': 10, 'TSLA': 5})
        self.assertEqual(len(self.account.transactions), 4)  # init, 2 buys, 1 sell
        self.assertEqual(self.account.transactions[3]['type'], 'SELL')
        self.assertEqual(self.account.transactions[3]['symbol'], 'AAPL')
        self.assertEqual(self.account.transactions[3]['quantity'], 10)

    def test_sell_all_shares_of_symbol(self):
        self.account.sell_shares('AAPL', 20)
        self.assertEqual(self.account.balance, 6000.0)  # 3000 + (150 * 20)
        self.assertEqual(self.account.portfolio, {'TSLA': 5})

    def test_sell_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 0)

    def test_sell_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', -5)

    def test_sell_nonexistent_symbol(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares('GOOGL', 10)

    def test_sell_insufficient_shares(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 30)  # Only have 20


class TestPortfolioValueAndProfitLoss(unittest.TestCase):
    def setUp(self):
        self.account = Account('user123', 10000.0)
        self.account.buy_shares('AAPL', 10)  # 1500 worth
        self.account.buy_shares('TSLA', 5)   # 4000 worth

    def test_get_portfolio_value(self):
        # Portfolio value = (10 * 150) + (5 * 800) = 1500 + 4000 = 5500
        self.assertEqual(self.account.get_portfolio_value(), 5500.0)

    def test_get_profit_or_loss_no_change(self):
        # Initial deposit: 10000
        # Current balance: 4500 (10000 - 1500 - 4000)
        # Portfolio value: 5500
        # Profit/Loss: (4500 + 5500) - 10000 = 0
        self.assertEqual(self.account.get_profit_or_loss(), 0.0)

    def test_get_profit_or_loss_with_deposit(self):
        self.account.deposit_funds(1000.0)
        # Now balance is 5500, but this shouldn't affect profit/loss
        self.assertEqual(self.account.get_profit_or_loss(), 0.0)

    @patch('accounts.get_share_price')
    def test_get_profit_or_loss_with_price_change(self, mock_get_share_price):
        # Mock price changes
        def side_effect(symbol):
            prices = {'AAPL': 180.0, 'TSLA': 900.0}
            return prices.get(symbol, 0.0)
            
        mock_get_share_price.side_effect = side_effect
        
        # New portfolio value = (10 * 180) + (5 * 900) = 1800 + 4500 = 6300
        # Profit/Loss = (4500 + 6300) - 10000 = 800
        self.assertEqual(self.account.get_portfolio_value(), 6300.0)
        self.assertEqual(self.account.get_profit_or_loss(), 800.0)


class TestHoldingsAndTransactionHistory(unittest.TestCase):
    def setUp(self):
        self.account = Account('user123', 10000.0)
        self.account.buy_shares('AAPL', 10)
        self.account.buy_shares('TSLA', 5)

    def test_get_holdings(self):
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {'AAPL': 10, 'TSLA': 5})
        
        # Verify we got a copy, not the original dictionary
        holdings['GOOGL'] = 3
        self.assertNotIn('GOOGL', self.account.portfolio)

    def test_get_transaction_history(self):
        history = self.account.get_transaction_history()
        self.assertEqual(len(history), 3)  # init deposit + 2 buys
        
        # Verify we got a copy, not the original list
        history.append({'fake_transaction': True})
        self.assertEqual(len(self.account.transactions), 3)


if __name__ == '__main__':
    unittest.main()