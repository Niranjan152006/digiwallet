import datetime

class DigitalWallet:
    def __init__(self, account_id, pin, daily_limit=1000.00):
        self.account_id = account_id
        self.pin = pin
        self.balance = 0.0
        self.daily_limit = daily_limit
        self.transactions = []  # List of tuples: (timestamp, type, amount, status)
        self.failed_pin_attempts = 0
        self.is_locked = False

    def verify_pin(self, pin):
        if self.is_locked:
            return False
        if self.pin == pin:
            self.failed_pin_attempts = 0
            return True
        else:
            self.failed_pin_attempts += 1
            if self.failed_pin_attempts >= 3:
                self.is_locked = True
            return False

    def check_fraud(self, amount):
        now = datetime.datetime.now()
        ten_minutes_ago = now - datetime.timedelta(minutes=10)
        
        # 1. More than 5 transactions in 10 minutes
        recent_txs = [t for t in self.transactions if t[0] > ten_minutes_ago]
        if len(recent_txs) >= 5:
            return "Suspicious: High frequency"
            
        # 2. Large transaction threshold
        if amount > 5000.0:
            return "Suspicious: Large transaction"
            
        # 3. Unusual transaction amount (e.g., negative or zero value)
        if amount <= 0:
            return "Suspicious: Unusual amount"
            
        return "Normal"

    def deposit(self, pin, amount):
        if not self.verify_pin(pin):
            return "Failed: Invalid PIN"
        
        fraud_status = self.check_fraud(amount)
        if "Suspicious" in fraud_status:
            self.transactions.append((datetime.datetime.now(), "Deposit", amount, "Flagged"))
            return fraud_status

        self.balance += amount
        self.transactions.append((datetime.datetime.now(), "Deposit", amount, "Success"))
        return "Success"

    def withdraw(self, pin, amount):
        if not self.verify_pin(pin):
            return "Failed: Invalid PIN"
            
        fraud_status = self.check_fraud(amount)
        if "Suspicious" in fraud_status:
            self.transactions.append((datetime.datetime.now(), "Withdrawal", amount, "Flagged"))
            return fraud_status

        # Balance verification
        if amount > self.balance:
            return "Failed: Insufficient balance"

        # Daily transaction limit check
        now = datetime.datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_withdrawals = sum(t[2] for t in self.transactions if t[0] >= today_start and t[1] in ["Withdrawal", "Transfer"] and t[3] == "Success")
        
        if today_withdrawals + amount > self.daily_limit:
            return "Failed: Daily limit exceeded"

        self.balance -= amount
        self.transactions.append((datetime.datetime.now(), "Withdrawal", amount, "Success"))
        return "Success"

    def transfer(self, pin, target_wallet, amount):
        if not self.verify_pin(pin):
            return "Failed: Invalid PIN"

        fraud_status = self.check_fraud(amount)
        if "Suspicious" in fraud_status:
            self.transactions.append((datetime.datetime.now(), "Transfer", amount, "Flagged"))
            return fraud_status

        if amount > self.balance:
            return "Failed: Insufficient balance"

        # Duplicate transaction check (same amount within last 10 seconds)
        now = datetime.datetime.now()
        recent_same_tx = [t for t in self.transactions if (now - t[0]).total_seconds() < 10 and t[2] == amount and t[1] == "Transfer"]
        if recent_same_tx:
            return "Suspicious: Duplicate transaction"

        self.balance -= amount
        target_wallet.balance += amount
        self.transactions.append((datetime.datetime.now(), f"Transfer to {target_wallet.account_id}", amount, "Success"))
        return "Success"

    def get_balance(self):
        return self.balance

    def get_history(self):
        return self.transactions
