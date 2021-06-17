from algosdk.constants import address_len, hash_len
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404

from .helpers import account_balance, account_transactions


class Account(models.Model):
    address = models.CharField(max_length=address_len)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def instance_from_address(cls, address):
        """Return model instance from provided account address."""
        try:
            return cls.objects.get(address=address)
        except ObjectDoesNotExist:
            raise Http404

    def balance(self):
        """Return this instance's balance in microAlgos."""
        return account_balance(self.address)

    def transactions(self):
        """Return all the transactions involving this account."""
        return account_transactions(self.address)

    def __str__(self):
        """Account's human-readable string representation."""
        return self.address


class Wallet(models.Model):
    wallet_id = models.CharField(max_length=hash_len)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def instance_from_id(cls, wallet_id):
        """Return model instance from provided wallet's ID."""
        try:
            return cls.objects.get(wallet_id=wallet_id)
        except ObjectDoesNotExist:
            raise Http404

    def __str__(self):
        """Wallet's human-readable string representation."""
        return self.name


class WalletAccount(Account):
    wallet = models.ForeignKey(Wallet, default=None, on_delete=models.CASCADE)
