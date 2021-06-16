from django.contrib import messages
from django.shortcuts import redirect, render

from .helpers import (
    add_standalone_account,
    add_wallet,
    cli_account_list,
    cli_passphrase_for_account,
    create_transaction,
)

from .forms import CreateWalletForm, TransferFundsForm
from .models import Account, Wallet


INITIAL_FUNDS = 1000000000


def create_standalone(request):

    address, passphrase = add_standalone_account()
    Account.objects.create(address=address)
    context = {"account": (address, passphrase)}
    return render(request, "mainapp/create_standalone.html", context)


def create_wallet(request):

    if request.method == "POST":

        form = CreateWalletForm(request.POST)

        if form.is_valid():

            wallet_id = add_wallet(
                form.cleaned_data["name"], form.cleaned_data["password"]
            )
            if wallet_id != "":
                Wallet.objects.create(
                    wallet_id=wallet_id,
                    name=form.cleaned_data["name"],
                    password=form.cleaned_data["password"],
                )
                message = "Wallet with name '{}' and ID '{}' has been created.".format(
                    form.cleaned_data["name"], wallet_id
                )
                messages.add_message(request, messages.SUCCESS, message)
                return redirect("wallet", wallet_id)

            form.add_error(None, "Wallet is not created!")

    else:
        form = CreateWalletForm()

    context = {"form": form}

    return render(request, "mainapp/create_wallet.html", context)


def index(request):
    accounts = Account.objects.order_by("-created")
    context = {"accounts": accounts}
    return render(request, "mainapp/index.html", context)


def initial_funds(request, receiver):

    for account in cli_account_list():
        if account[1] > INITIAL_FUNDS:
            sender = account[0]
            break
    else:
        return render(request, "mainapp/initial_funds.html", {})

    create_transaction(
        sender,
        receiver,
        cli_passphrase_for_account(sender),
        INITIAL_FUNDS,
        "Initial funds",
    )
    return redirect("standalone-account", receiver)


def standalone_account(request, address):

    context = {"account": Account.instance_from_address(address)}
    return render(request, "mainapp/standalone_account.html", context)


def transfer_funds(request, sender):

    if request.method == "POST":

        form = TransferFundsForm(request.POST)

        if form.is_valid():

            error_field, error_description = create_transaction(
                sender,
                form.cleaned_data["receiver"],
                form.cleaned_data["passphrase"],
                form.cleaned_data["amount"],
                form.cleaned_data["note"],
            )
            if error_field == "":
                message = "Amount of {} microAlgos has been successfully transferred to account {}".format(
                    form.cleaned_data["amount"], form.cleaned_data["receiver"]
                )
                messages.add_message(request, messages.SUCCESS, message)
                return redirect("standalone-account", sender)

            form.add_error(error_field, error_description)

    else:
        form = TransferFundsForm()

    context = {"form": form, "sender": sender}

    return render(request, "mainapp/transfer_funds.html", context)


def wallet(request, wallet_id):

    context = {"wallet": Wallet.instance_from_id(wallet_id)}
    return render(request, "mainapp/wallet.html", context)


def wallets(request):
    wallets = Wallet.objects.order_by("-created")
    context = {"wallets": wallets}
    return render(request, "mainapp/wallets.html", context)
