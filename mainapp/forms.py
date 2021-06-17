from django import forms
from django.core.exceptions import ValidationError


class TransferFundsForm(forms.Form):
    passphrase = forms.CharField()
    receiver = forms.CharField(max_length=58)
    amount = forms.IntegerField(min_value=1)
    note = forms.CharField(max_length=1000, required=False)

    def clean_passphrase(self):
        """Example validation for the passphrase field."""
        data = self.cleaned_data["passphrase"]
        words = data.split(" ")
        if len(words) != 25:
            raise ValidationError("Passphrase must have exactly 25 words!")
        return data

    def clean_receiver(self):
        """Example validation for the receiver field."""
        data = self.cleaned_data["receiver"]
        if len(data) != 58:
            raise ValidationError("Algorand's address must be 58 characters long!")
        return data


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
