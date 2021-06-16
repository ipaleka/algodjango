from django.contrib import messages
from django.shortcuts import redirect, render

from .helpers import (
    cli_account_list,
    cli_passphrase_for_account,
    create_standalone_account,
    create_transaction,
)

from .forms import TransferFundsForm
from .models import Account


INITIAL_FUNDS = 1000000000


def index(request):
    accounts = Account.objects.order_by("-created")
    context = {"accounts": accounts}
    return render(request, "mainapp/index.html", context)


def create_standalone(request):

    address, passphrase = create_standalone_account()
    Account.objects.create(address=address)
    context = {"account": (address, passphrase)}
    return render(request, "mainapp/create_standalone.html", context)


def standalone_account(request, address):

    context = {"account": Account.instance_from_address(address)}
    return render(request, "mainapp/standalone_account.html", context)


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


def transfer_funds(request, sender):

    # If this is a POST request then process the Form data
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
        # form = TransferFundsForm(initial={"renewal_date": proposed_renewal_date})
        form = TransferFundsForm()

    context = {"form": form, "sender": sender}

    return render(request, "mainapp/transfer_funds.html", context)
