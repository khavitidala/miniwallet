import uuid
from django.db import models


class Account(models.Model):
    customer_xid = models.UUIDField(primary_key=True)


class Wallet(models.Model):
    class EnabledChoices(models.IntegerChoices):
        DISABLED = 0
        ENABLED = 1

    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    owned_by = models.OneToOneField(to=Account, on_delete=models.CASCADE, db_column='owned_by', unique=True)
    status = models.PositiveSmallIntegerField(choices=EnabledChoices.choices, default=EnabledChoices.ENABLED)
    enabled_at = models.DateTimeField(blank=True, null=True)
    disabled_at = models.DateTimeField(blank=True, null=True)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)


class TransactionHistory(models.Model):
    class StatusChoices(models.IntegerChoices):
        FAILED = 0
        SUCCESS = 1
    
    class TypeChoices(models.IntegerChoices):
        DEPOSIT = 1
        WITHDRAWAL = -1
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    status = models.PositiveSmallIntegerField(choices=StatusChoices.choices)
    transacted_at = models.DateTimeField(auto_now_add=True)
    type = models.SmallIntegerField(choices=TypeChoices.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    reference_id = models.UUIDField(unique=True, default=uuid.uuid1)
    transacted_by = models.CharField(max_length=50)
    wallet_id = models.ForeignKey(to=Wallet, on_delete=models.CASCADE, db_column='wallet_id')