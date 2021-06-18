from algosdk.constants import address_len, mnemonic_len, note_max_length
from django import forms
from django.core.exceptions import ValidationError
from django.forms.fields import CharField

from .models import Asset


class TransferFundsForm(forms.Form):
    passphrase = forms.CharField()
    receiver = forms.CharField(max_length=address_len)
    amount = forms.IntegerField(min_value=1)
    note = forms.CharField(max_length=note_max_length, required=False)

    def clean_passphrase(self):
        """Example validation for the passphrase field."""
        data = self.cleaned_data["passphrase"]
        words = data.split(" ")
        if len(words) != mnemonic_len:
            raise ValidationError(
                "Passphrase must have exactly %s words!" % (mnemonic_len,)
            )
        return data

    def clean_receiver(self):
        """Example validation for the receiver field."""
        data = self.cleaned_data["receiver"]
        if len(data) != address_len:
            raise ValidationError(
                "Algorand's address must be %s characters long!" % (address_len,)
            )
        return data


class CreateAssetForm(forms.models.ModelForm):
    passphrase = CharField(required=True)

    class Meta:
        model = Asset
        fields = (
            "creator",
            "name",
            "unit",
            "total",
            "decimals",
            "frozen",
            "url",
            "metadata",
            "manager",
            "reserve",
            "freeze",
            "clawback",
        )


class CreateWalletForm(forms.Form):
    name = forms.CharField(min_length=2)
    password = forms.CharField(min_length=2)

    def clean_password(self):
        """Example validation for the password field."""
        data = self.cleaned_data["password"]
        if data.isnumeric():
            raise ValidationError("Alphanumeric value for password is required!")
        if data.isalpha():
            raise ValidationError("Alphanumeric value for password is required!")

        return data


class SearchTransactionsForm(forms.Form):
    note = forms.CharField()
