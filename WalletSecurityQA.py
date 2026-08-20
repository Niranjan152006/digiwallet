import unittest
import time
import datetime
from DigitalWallet import DigitalWallet

class TestWalletSecurityQA(unittest.TestCase):
    def setUp(self):
        self.wallet = DigitalWallet(account_id="ACC123", pin="1234", daily_limit=500.00)
        self.target_wallet = DigitalWallet(account_id="ACC456", pin="5678")
        self.wallet.deposit("1234", 1000.00) # Pre-fund wallet

    def test_normal_transaction(self):
        result = self.wallet.withdraw("1234", 100.00)
        self.assertEqual(result, "Success")
        self.assertEqual(self.wallet.get_balance(), 900.00)

    def test_insufficient_balance(self):
        result = self.wallet.withdraw("1234", 2000.00)
        self.assertEqual(result, "Failed: Insufficient balance")

    def test_daily_limit(self):
        result = self.wallet.withdraw("1234", 600.00)
        self.assertEqual(result, "Failed: Daily limit exceeded")

    def test_multiple_failed_pins(self):
        self.assertFalse(self.wallet.verify_pin("9999"))
        self.assertFalse(self.wallet.verify_pin("9999"))
        self.assertFalse(self.wallet.verify_pin("9999"))
        self.assertTrue(self.wallet.is_locked)
        self.assertEqual(self.wallet.withdraw("1234", 50.00), "Failed: Invalid PIN")

    def test_suspicious_transaction_large_amount(self):
        # Testing fraud detection for extremely large amounts
        result = self.wallet.deposit("1234", 6000.00)
        self.assertEqual(result, "Suspicious: Large transaction")

    def test_duplicate_transaction(self):
        self.wallet.transfer("1234", self.target_wallet, 20.00)
        result = self.wallet.transfer("1234", self.target_wallet, 20.00)
        self.assertEqual(result, "Suspicious: Duplicate transaction")

    def test_negative_amount(self):
        result = self.wallet.deposit("1234", -50.00)
        self.assertEqual(result, "Suspicious: Unusual amount")

    def test_concurrent_transactions_frequency(self):
        # Simulate high-frequency transactions to trigger the 5-tx limit rule
        for _ in range(5):
            self.wallet.deposit("1234", 10.00)
        result = self.wallet.deposit("1234", 10.00)
        self.assertEqual(result, "Suspicious: High frequency")

if __name__ == '__main__':
    unittest.main()
