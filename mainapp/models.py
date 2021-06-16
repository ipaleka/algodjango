from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404

from .helpers import account_balance


class Account(models.Model):
    address = models.CharField(max_length=58)
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

    def __str__(self):
        """Account's human representation."""
        return self.address
