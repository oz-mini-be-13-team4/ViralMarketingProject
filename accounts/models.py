from django.db import models

from accounts.constants import TRANSACTION_METHOD, TRANSACTION_TYPE


class Transaction(models.Model):
    transaction_amount = models.DecimalField("거래 금액", decimal_places=2, max_digits=18)
    amount_after_transaction = models.DecimalField("거래 후 잔액", decimal_places=2, max_digits=18)
    account_factor_history = models.CharField("계좌 인자 내역", max_length=255)
    deposit_and_withdrawal_type = models.CharField("입출금 타입", max_length=8, choices=TRANSACTION_TYPE)
    transaction_type = models.CharField("거래 타입", max_length=20, choices=TRANSACTION_METHOD)
    transaction_timestamp = models.DateTimeField("거래 일시", auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.transaction_type} {self.transaction_amount}"
