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
        label="Transaction type"
    )

    def clean_note_prefix(self):
        """Algorand SDK needs bytes-like object for note prefix."""
        data = self.cleaned_data["note_prefix"]
        return data.encode("ascii") if data != "" else data

    def clean(self):
        """Ensure at least one field is non-empty."""
        cleaned_data = super().clean()
        if all(val == "" for val in cleaned_data.values()):
            raise ValidationError("You should fill at least one field!")

        return cleaned_data
