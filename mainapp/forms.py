from algosdk.constants import address_len, mnemonic_len, note_max_length
from algosdk.encoding import is_valid_address
from django import forms
from django.core.exceptions import ValidationError
from django.forms.fields import CharField

from .models import Asset


class TransferFundsForm(forms.Form):
    """Django form for transferring microAlgos between accounts."""

    passphrase = forms.CharField(required=False)
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
        if not is_valid_address(data):
            raise ValidationError("Provided value is not a valid Algorand address!")
        return data


class CreateAssetForm(forms.models.ModelForm):
    """Django model form for creating Algorand assets."""

    passphrase = CharField(required=False)

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

    def _clean_address(self, field):
        """Base method for validation of fields holding Algorand address."""
        data = self.cleaned_data[field]
        if data != "" and not is_valid_address(data):
            raise ValidationError("Provided value is not a valid Algorand address!")
        return data

    def clean_creator(self):
        return self._clean_address("creator")

    def clean_manager(self):
        return self._clean_address("manager")

    def clean_reserve(self):
        return self._clean_address("reserve")

    def clean_freeze(self):
        return self._clean_address("freeze")

    def clean_clawback(self):
        return self._clean_address("clawback")


class CreateWalletForm(forms.Form):
    """Django form for creating wallets."""

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
    """Django form for searching Algorand transactions."""

    note_prefix = forms.CharField(required=False)
    address = forms.CharField(required=False)
    asset_id = forms.CharField(required=False, label="Asset ID")
    txid = forms.CharField(required=False, label="Transaction ID")
    block = forms.CharField(required=False, label="Round")
    txn_type = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All types"),
            ("pay", "Payment"),
            ("keyreg", "Key registration"),
            ("acfg", "Asset configuration"),
            ("axfer", "Asset freeze"),
            ("afrz", "Asset transfer"),
        ],
        label="Transaction type",
    )

    def clean_note_prefix(self):
        """Algorand SDK needs bytes-like object for note prefix."""
        data = self.cleaned_data["note_prefix"]
        return data.encode("ascii") if data != "" else data

    def clean(self):
        """Ensure at least one field is non-empty."""
        cleaned_data = super().clean()
        if all(val == "" for val in cleaned_data.values()):
            raise ValidationError("You must fill at least one field!")

        return cleaned_data
