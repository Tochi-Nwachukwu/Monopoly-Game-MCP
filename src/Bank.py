class Bank:
    def __init__(self) -> None:
        self.balance = 200000

    def pay_in(self, amount):
        self.balance += amount

    def pay_out(self, amount):
        self.balance -= amount

    def get_bank_balance(self):
        return self.balance
