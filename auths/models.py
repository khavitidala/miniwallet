from django.db import models


class Account(models.Model):
    customer_xid = models.UUIDField(primary_key=True)