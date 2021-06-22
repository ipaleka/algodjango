# Introduction

The purpose of this tutorial is to introduce the reader to the [Algorand SDK](https://developer.algorand.org/docs/reference/sdks/) and its implementation in [Django framework](https://www.djangoproject.com/).



**xyz**


# Requirements

This tutorial uses a [Python](https://www.python.org/) wrapper around Algorand SDK, so you should have Python 3 installed on your system. Also, this tutorial uses `python3-venv` package for creating virtual environments and you have to install it if it's not already installed in your system. For a Debian/Ubuntu based systems, you can do that by issuing the following command:

```bash
$ sudo apt-get install python3-venv
```

In order to clone the Algorand Sandbox (as opposite to just download its installation archive), you'll also need [Git distributed version control system](https://git-scm.com/).


# Setup and run Algorand Sandbox

Let's create the root directory named `algorand` where your Django project and Sandbox will reside.

```bash
cd ~
mkdir algorand
cd algorand
```

This project depends on [Algorand Sandbox](https://github.com/algorand/sandbox) running in your computer. Use its README for the instructions how to prepare its installation on your system. You may clone the Algorand Sandbox repository with the following command:

```bash
git clone https://github.com/algorand/sandbox.git
```

Start the Sandbox Docker containers by issuing the following command:

```bash
./sandbox/sandbox up
```

For the rest of this tutorial, we'll assume that Sandbox is up and running in your system.

---
**Note**

This tutorial code implies that the Sandbox executable is in the `sandbox` directory which is a sibling to this project's directory:

```bash
$ tree -L 1
.
├── algodjango
└── sandbox
```

If that's not the case, then you should set `SANDBOX_DIR` environment variable holding sandbox directory before running this project's Django development server:

```bash
export SANDBOX_DIR="/home/ipaleka/dev/algorand/sandbox
```

---

# Create and activate project's Python virtual environment

Every Python-based project should run inside its own virtual environment. Create and activate one for this project with:

```bash
python3 -m venv algovenv
source algovenv/bin/activate
```

After a successful activation, the environment name will be presented at your prompt and that indicates that all the Python package installations issued will reside only in that environment.

```bash
(algovenv) $
```

We're ready now to install our project's main dependencies: the [Python Algorand SDK](https://github.com/algorand/py-algorand-sdk) and [Django](https://www.djangoproject.com/).


```bash
(algovenv) $ pip install py-algorand-sdk Django
```

# Create Django project and the main application

Django ships with a helper shortcut utility `django-admin` that will help us in creation of our project files. Create our project named `algodjango` with:

```bash
(algovenv) $ django-admin startproject algodjango
```

That command will create the root directory for our project together with project's directory with the same name:

```bash
(algovenv) $ tree
.
└── algodjango
    ├── algodjango
    │   ├── asgi.py
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── manage.py
```

A Django project is made of applications. All the functionality of this project will reside in a single app. Change directory to the project's root directory and use the `startapp` Django management command to create our app named `mainapp`:

```bash
(algovenv) $ cd algodjango
(algovenv) $ python manage.py startapp mainapp
```

That creates a new directory inside project's root directory with the following structure:

```bash
(algovenv) $ tree
.
├── algodjango
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── mainapp
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── manage.py
```

We need one more thing before we start writing our app code. Use your favorite editor and open the `settings.py` file placed in the project's directory. Find the `INSTALLED_APPS` setting and prepend the list with our app's configuration class. Afterward, that setting should look like this:

```python
INSTALLED_APPS = [
    "mainapp.apps.MainappConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

Now you may start the Django development server with:

```bash
(algovenv) $ python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
June 20, 2021 - 20:42:22
Django version 3.2.4, using settings 'algodjango.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Ignore that warning about unapplied migrations for now and point your browser to the specified URL (http://127.0.0.1:8000/). You should see a page similar to the following one:

![Django starting page](https://github.com/ipaleka/algodjango/blob/main/media/django-starting-page.png?raw=true)

If all goes well then you're ready to start writing code for your Algorand application.


# Our first Django page

In the next few sections we're going to configure and create code for our project's first Django-based HTML page.


## Application's URL configuration

Django URL dispatcher routes predefined urls to Django views and that URL configuration is placed in the `urls.py` file in the project directory. We'll create a separate URL configuration file inside our main application directory and change the project's URL dispatcher to include that newly created configuration:

Project's URL dispatcher `algodjango/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("mainapp.urls")),
]
```

Create a new python module `mainapp/urls.py` with the following content:

```python
from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
]
```

## Root page view

Now every request in your browser to the root page of the site (an empty string as URL defines the root page of the site - in the case of our development server that would be http://127.0.0.1:8000/) will execute code from the `index` function found inside `mainapp/views.py` module.

---
**Note**

You may implement Django views in two different ways: as the function based views or as the class-based views. Please take your time to familiarize with the class-based views in Django because they can make your coding more powerful and more secure, but for the purpose of technology introduction to the readers, like in this tutorial, the function-based views are probably easier to grasp on and so are the better choice.

---

Our root/index page will be used to display the list of all created [standalone accounts](https://developer.algorand.org/docs/features/accounts/) in our application. Beside those standalone accounts, in our app we'll be creating and displaying accounts connected to the wallets. There are other type of accounts that are entities in the Algorand blockchain, like special or multisignature accounts, but those are out of scope for this tutorial.

Update the `views.py` module with the code as follows:

```python
from django.shortcuts import render

from .models import Account


def index(request):
    """Display all the created standalone accounts."""

    accounts = Account.objects.order_by("-created")
    context = {"accounts": accounts}
    return render(request, "mainapp/index.html", context)
```

So, we fetch all the account objects from the database (we'll get to that code related to database in a minute) and we pass them in the form of a Python dictionary as the context of the index page template (another code yet to be created) rendered by Django framework.

---
**Note**

We may use the Algorand SDK for the same purpose of fetching created accounts, but keeping those records in the application database surely represents a real-world application.

---

## Account model

[Django model](https://docs.djangoproject.com/en/3.2/topics/db/models/) is a class that represents a table in your database. The default database engine of a newly created Django project is the SQLite and we're going to use it in this tutorial. That engine creates a single file in the project's root directory named `db.sqlite3` which represents our database.

For the account model, we record only the account addresses and the time when they are created. The rest of account information aren't kept in our database, while keeping the account passphrase is up to the user.

Edit the `models.py` module and add the following code:

```python
from algosdk.constants import address_len
from django.db import models


class Account(models.Model):
    """Base model class for Algorand accounts."""

    address = models.CharField(max_length=address_len)
    created = models.DateTimeField(auto_now_add=True)

    def balance(self):
        """Return this instance's balance in microAlgos."""
        return 0
```

In order to apply those changes to our database, run the following Django management commands:

```bash
(algovenv) $ python manage.py makemigrations
(algovenv) $ python manage.py migrate
```

If you start the development server now, you can see that the warning from the above (about unapplied migrations) has gone.


## Index page template

In order to render the accounts data in the browser, we must create a Django template of our index page. The default placement for such template is in the `mainapp` subdirectory of the `templates` directory inside our application directory:

```bash
(algovenv) $ mkdir -p mainapp/templates/mainapp
```

Now create the following two files in that directory:

`mainapp/templates/mainapp/base.html`
```html
{% load static %}<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}Accounts{% endblock %}</title>
    <link rel="stylesheet" type="text/css" href="{% static 'mainapp/style.css' %}">
  </head>
  <body>
    <div class="topnav">
      <a href="/"{% if request.path == '/' %} class="active"{% endif %}>Standalone accounts</a>
    </div>
    <div class="body">{% block body %}{% endblock %}</div>
  </body>
</html>
```

`mainapp/templates/mainapp/index.html`
```html
{% extends 'mainapp/base.html' %}
{% block title %}Standalone accounts{% endblock %}
{% block body %}
  <h1>Standalone accounts list</h1>
  {% if accounts %}
  <ul>
  {% for account in accounts %}
    <li><a href="/standalone-account/{{ account.address }}">{{ account.address }}</a> : {{ account.balance }} microAlgos</li>
  {% endfor %}
  </ul>
  {% else %}
  <p>There are no standalone accounts.</p>
  {% endif %}
  <br>
  <a href="/create-standalone/">Create standalone account</a>
{% endblock %}
```

We're going to use this `base.html` in all of our templates in this tutorial. In short, based on the [DRY principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) and with the help of the [Django template system](https://docs.djangoproject.com/en/3.2/topics/templates/), our templates will share the same HTML page headers and the navigation bar. As you might have already guessed from these templates, we *extend* the base template and change the defined *blocks* of data in the derived templates.

In the index template, we loop through the context's `accounts` - the value we provided to the template in our index view. For each account we create an unordered list item with a link to that account's detail page (a template we haven't created yet).


## CSS styling

We need to do one more thing before we point our browser to the index page - improve the aesthetic of our pages! This part is optional and it won't change the tutorial's functionality, but maybe it will help you in configuring your future Django-based Algorand's projects.

As you can see from the `base.html` template, the CSS for our site is located in the `style.css` file. The default placement for the [static files](https://docs.djangoproject.com/en/3.2/howto/static-files/) in Django projects is similar to templates:

```bash
(algovenv) $ mkdir -p mainapp/static/mainapp
```

Now create the `style.css` file in that directory with the following content:

```css
body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
}

.body {
    margin: 5px;
}

.topnav {
    overflow: hidden;
    background-color: #222;
}

.topnav a {
    float: left;
    color: #fbfbfb;
    text-align: center;
    padding: 12px 12px;
    text-decoration: none;
    font-size: 16px;
}

.topnav a:hover {
    background-color: #eee;
    color: black;
}

.topnav a.active {
    background-color: #5d6d7e;
    color: white;
}
```

Run the development server now (`python manage.py runserver`) and point your browser to the root page (`http://127.0.0.1:8000/`). If all goes well, you should see the index that looks like this:

![Index page](https://github.com/ipaleka/algodjango/blob/main/media/index-starting-page.png?raw=true)

Congratulations on your first Django page!


# Standalone account creation

All the sections and code from previous sections can be used for the general purpose of creating web pages with Django. That introduction steps were needed to get you familiarized with the basic Django principles and now we're finally ready to start using Algorand SDK!

We created a link in the index page to the page used for creation of a standalone account. Now, update app's `urls.py` and `views.py` modules with the related code.

`mainapp/urls.py`

```python
urlpatterns = [
    #
    path("create-standalone/", views.create_standalone, name="create-standalone"),
]
```

`mainapp/views.py`

```python
from .helpers import add_standalone_account


def create_standalone(request):
    """Create standalone account."""
    address, passphrase = add_standalone_account()
    Account.objects.create(address=address)
    context = {"account": (address, passphrase)}
    return render(request, "mainapp/create_standalone.html", context)
```

A new account record in the database is created by calling the `create` method on the Account's model `objects` manager. All the required model fields values should be provided to the create method in order to successfully create an object - in our case that would be the account's address.

As you can see, we introduced a new module named `helpers.py`. That module will hold all the Algorand functionality code of our project. Create that module in the mainapp directory with the following content:

`mainapp/helpers.py`

```python
from algosdk import account, mnemonic


def add_standalone_account():
    """Create standalone account and return two-tuple of its address and passphrase."""
    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)
    return address, passphrase
```

This code that uses Algorand SDK should be straightforward: we [created an account](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/account.html#algosdk.account.generate_account) and used returned private key to get the [account's passphrase](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/mnemonic.html#algosdk.mnemonic.from_private_key).


Now create the template that will be rendered upon account creation.

`mainapp/templates/mainapp/create_standalone.html`

```html
{% extends 'mainapp/base.html' %}
{% block title %}Create standalone account{% endblock %}
{% block body %}
  <h1>New standalone account</h1>
  {% if account %}
  <p>Your standalone account has been created. Please write down the following data:</p>
  <p><strong>Address</strong>: {{ account.0 }}</p>
  <p><strong>Passphrase</strong>: {{ account.1 }}</p>
  <br>
  <a href="/initial-funds/{{ account.0 }}/">Add initial funds</a>
  {% endif %}
{% endblock %}
```

We provided a two-tuple (a tuple consisting of two items) as the context to this template and in this template its values are retrieved by the related indexes.

Go to the index page, click the link entitled `Create standalone account` and you should see the page that looks like:

![Create standalone account](https://github.com/ipaleka/algodjango/blob/main/media/create-standalone-page.png?raw=true)


# Initial funds for the standalone accounts

Algorand Sandbox operates either in a real network mode (using one of the Algorand's [public networks](https://developer.algorand.org/docs/reference/algorand-networks/)) or in a private network mode. In the former case, you may use the Testnet and add funds to your account in the [Algorand dispenser](https://bank.testnet.algorand.network/), but in this tutorial we use the private network mode which has been the default setup for the Sandbox. Algorand Sandbox creates some test accounts filled with Algos and we'll use one of those accounts to transfer initial funds to the accounts created by our application.

The following code in `helpers.py` module is responsible for retrieving the address of a test account (created by Sandbox) that has enough funds (funds to transfer plus minimum requirement of 0.1 Algo) which can be transferred to our accounts:

```python
from algosdk.constants import microalgos_to_algos_ratio
from algosdk.v2client import indexer

INITIAL_FUNDS = 1000000000  # in microAlgos


def _indexer_client():
    """Instantiate and return Indexer client object."""
    indexer_address = "http://localhost:8980"
    indexer_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return indexer.IndexerClient(indexer_token, indexer_address)


def initial_funds_sender():
    """Get the address of initially created account having enough funds."""
    return next(
        (
            account.get("address")
            for account in _indexer_client().accounts().get("accounts", [])
            if account.get("created-at-round") == 0
            and account.get("amount") > INITIAL_FUNDS + microalgos_to_algos_ratio / 10
        ),
        None,
    )
```

Every transaction in the Algorand blockchain has to be signed by the sender account, so we also need the passphrase of the sender account. We use Python capabilities for communicating with command line interfaces and running Sandbox process to export that passphrase using Algorand's `goal` command:

`mainapp\helpers.py`

```python
import io
import os
import subprocess
from pathlib import Path


def _call_sandbox_command(*args):
    """Call and return sandbox command composed from provided arguments."""
    return subprocess.Popen(
        [_sandbox_executable(), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _sandbox_executable():
    """Return full path to Algorand's sandbox executable.

    The location of sandbox directory is retrieved either from the SANDBOX_DIR
    environment variable or if it's not set then the location of sandbox directory
    is implied to be the sibling of this Django project in the directory tree.
    """
    sandbox_dir = os.environ.get("SANDBOX_DIR") or str(
        Path(__file__).resolve().parent.parent.parent / "sandbox"
    )
    return sandbox_dir + "/sandbox"


def cli_passphrase_for_account(address):
    """Return passphrase for provided address."""
    process = _call_sandbox_command("goal", "account", "export", "-a", address)
    passphrase = ""
    for line in io.TextIOWrapper(process.stdout):
        parts = line.split('"')
        if len(parts) > 1:
            passphrase = parts[1]
    return passphrase
```

Let's create the related URL and view:

`mainapp/urls.py`

```python
urlpatterns = [
    #
    path("initial-funds/<str:receiver>/", views.initial_funds, name="initial-funds"),
]
```

`mainapp\views.py`

```python
from django.contrib import messages
from django.shortcuts import redirect

from .helpers import (
    INITIAL_FUNDS,
    add_transaction,
    cli_passphrase_for_account,
    initial_funds_sender,
)


def initial_funds(request, receiver):
    """Add initial funds to provided standalone receiver account."""
    sender = initial_funds_sender()
    if sender is None:
        message = "Initial funds weren't transferred!"
        messages.add_message(request, messages.ERROR, message)
    else:
        add_transaction(
            sender,
            receiver,
            cli_passphrase_for_account(sender),
            INITIAL_FUNDS,
            "Initial funds",
        )
    return redirect("standalone-account", receiver)
```

As you can see, the URL contains a receiver address and that address is supplied as a positional argument to the view.

We'll get to the `add_transaction` function in a minute, let's first create the template where this view redirects:

`mainapp\templates\mainapp\standalone_account.html`

```html
{% extends 'mainapp/base_account.html' %}
```

We use the base template as we're going to code the wallet-based accounts functionality in this tutorial that will use the same base template:

`mainapp\templates\mainapp\base_account.html`

```html
{% extends 'mainapp/base.html' %}
{% block title %}Account page{% endblock %}
{% block body %}
  <h1>{% block prefix %}Standalone{% endblock prefix %} account page</h1>
  {% block start %}{% endblock start %}
  <p>Address: {{ account.address }}</p>
  <p>Created: {{ account.created }}</p>
  <p>Balance: {{ account.balance }} microAlgos</p>
  <br>
  {% if messages %}
    <ul class="messages">
      {% for message in messages %}
        <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
      {% endfor %}
    </ul>
  {% endif %}
{% endblock body %}
```

As you can see from the presented code, if the initial funds transfer fails then the [error message](https://docs.djangoproject.com/en/3.2/ref/contrib/messages/) is rendered. Update our styling CSS too so the error text is displayed in red:

`mainapp/static/mainapp/style.css`

```css
ul.messages li.error {
    color: red;
}

ul.messages li.success {
    color: green;
}
```

One more thing we should do before we get to the `add_transaction` SDK call - we need to update the account model with the proper `balance` method:

`mainapp\models.py`

```python
from .helpers import account_balance

class Account(models.Model):
    #

    def balance(self):
        """Return this instance's balance in microAlgos."""
        return account_balance(self.address)

```

The code for that `account_balance` helper function should be straightforward: we use predefined (by Algorand Sandbox) tokens and API endpoints to instantiate Algod client and then we use the `account_info` method of that client to retrieve the funds amount in microAlgos.

`mainapp\helpers.py`

```python
from algosdk.v2client import algod


def _algod_client():
    """Instantiate and return Algod client object."""
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return algod.AlgodClient(algod_token, algod_address)


def account_balance(address):
    """Return funds balance of the account having provided address."""
    account_info = _algod_client().account_info(address)
    return account_info.get("amount")
```


# Create and sign a transaction on the Algorand blockchain

[Algorand](https://developer.algorand.org/docs/reference/transactions/) and [Python Algorand SDK](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/transaction.html) allow you to change various arguments in the transactions creating process according to your needs, We'll be using the suggested parameters by Algorand SDK for the purpose of this tutorial.

`mainapp\helpers.py`

```python
from algosdk.future.transaction import PaymentTxn
from algosdk.error import WrongChecksumError


def add_transaction(sender, receiver, passphrase, amount, note):
    """Create and sign transaction from provided arguments."""

    client = _algod_client()
    params = client.suggested_params()
    unsigned_txn = PaymentTxn(sender, params, receiver, amount, None, note.encode())
    try:
        signed_txn = unsigned_txn.sign(mnemonic.to_private_key(passphrase))
    except WrongChecksumError:
        return "passphrase", "Checksum failed to validate"
    except ValueError:
        return "passphrase", "Unknown word in passphrase"

    transaction_id = client.send_transaction(signed_txn)
    try:
        _wait_for_confirmation(client, transaction_id, 4)
    except Exception as err:
        return None, err  # None implies non-field error
    return "", ""
```

The code for `_wait_for_confirmation` function is still our obligation for the version `1.5.0` of the `py-algorand-sdk`, but it will probably be a part of the Algorand's Python SDK in the future.

`mainapp\helpers.py`

```python
def _wait_for_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception("pool error: {}".format(pending_txn["pool-error"]))
        client.status_after_block(current_round)
        current_round += 1
    raise Exception(
        "pending tx not found in timeout rounds, timeout value = : {}".format(timeout)
    )
```

And now you're ready to transfer the initial funds to your account. Point your browser to the index page, create a standalone account, click the `Add initial funds` link, wait no more than 5 seconds for the transaction confirmation on the blockchain and - voilà! - you've got your Algos!


# Display account's transactions

The account page should display a list of all created transactions. Edit the account model and add the following method:

`mainapp\models.py`

```python
from .helpers import account_transactions


class Account(models.Model):
    #
    def transactions(self):
        """Return all the transactions involving this account."""
        return account_transactions(self.address)
```

The code that will return the list of provided [account's transactions](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/v2client/indexer.html#algosdk.v2client.indexer.IndexerClient.search_transactions_by_address) is placed in the `account_transactions` helper function:

`mainapp\helpers.py`

```python
def account_transactions(address):
    """Return all transactions involving provided address."""
    transactions = (
        _indexer_client()
        .search_transactions_by_address(address)
        .get("transactions", [])
    )
    return [
        {
            "id": tr.get("id"),
            "round": tr.get("confirmed-round"),
            "type": tr.get("tx-type"),
            "sender": tr.get("sender"),
            "receiver": tr.get("payment-transaction", {}).get("receiver"),
            "amount": tr.get("payment-transaction", {}).get("amount"),
            "note": base64.b64decode(tr.get("note", "")).decode("utf-8"),
        }
        for tr in transactions
    ]
```

You can see that transactions notes in the Algorand blockchain are base64 encoded, so we have to decode them in order to present them in a human-readable way.

Update the base account template by adding the following code just before the `{% endblock body %}` tag:

`mainapp\templates\mainapp\base_account.html`

```html
  <h2>Transactions</h2>
  <table class="full-width">
  <tr>
    <th>ID</th>
    <th>Round/Type</th>
    <th>Sender/Receiver</th>
    <th>Amount</th>
    <th>Note</th>
  </tr>
  {% for transaction in account.transactions %}
  <tr>
    <td rowspan="2">{{ transaction.id }}</td>
    <td>{{ transaction.round }}</td>
    <td>{{ transaction.sender }}</td>
    <td rowspan="2">{{ transaction.amount }}</td>
    <td rowspan="2">{{ transaction.note }}</td>
  </tr>
  <tr>
    <td>{{ transaction.type }}</td>
    <td>{{ transaction.receiver }}</td>
  </tr>
  {% endfor %}
</table>
```

Also, add the following rules to our CSS:

`mainapp/static/mainapp/style.css`

```css
table.full-width {
    width: 100%;
}

th {
    text-align: left;
}
```

From now on, every account's transaction will be displayed as a table row at the end of the account page.


# Transfer funds functionality

In this section we'll use one of the most powerful Django beasts - its [forms system](https://docs.djangoproject.com/en/3.2/topics/forms/)!

For the start, edit the base account page template once again and add the the following link just before the transactions table:

`mainapp\templates\mainapp\base_account.html`

```html
<a href="/transfer-funds/{{ account.address }}/">Transfer funds</a>
```

The URL configuration should look like:

`mainapp/urls.py`

```python
urlpatterns = [
    #
    path("transfer-funds/<str:sender>/", views.transfer_funds, name="transfer-funds"),
]
```

Now create a brand new module `forms.py` in the main application directory and add the following code into it:

`mainapp/forms.py`

```python
from algosdk.constants import address_len, mnemonic_len, note_max_length
from django import forms
from django.core.exceptions import ValidationError
from django.forms.fields import CharField


class TransferFundsForm(forms.Form):
    """Django form for transferring microAlgos between accounts."""

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
```

When a validation error is raised during the form submission process inside Django framework, then the form is returned with either the field error(s) or with a non-field error. Django forms system can take care of some predefined requirements on the client side (like the receiver or note field length in this form) before validation takes place on the server side. In this form we validate two fields, `passphrase` and `receiver`, for some simple requirements.

The template responsible for rendering this form looks like this:

`mainapp/templates/mainapp/transfer_funds.html`

```html
{% extends 'mainapp/base.html' %}
{% block title %}Transfer funds{% endblock %}
{% block body %}
  <h1>Transfer funds</h1>
  <p><strong>Sender</strong>: {{ sender }}</p>
  <form action="/transfer-funds/{{ sender }}/" method="post">
    {% csrf_token %}
    <table>{{ form.as_table }}</table>
    <input type="submit" value="Submit">
  </form>
{% endblock %}
```

As you can see, we instruct the Django template system to display the form as a table and Django takes care of rendering it properly. Also, every Django form needs the [Cross Site Request Forgery protection token tag](https://docs.djangoproject.com/en/3.2/ref/csrf/) for the security reasons.

In order to display the form errors text in red, update the CSS with:

`mainapp/static/mainapp/style.css`

```css
ul.errorlist li {
    color: red;
}
```

Now add the following to the main application views module:

`mainapp/views.py`

```python
from .forms import TransferFundsForm


def transfer_funds(request, sender):
    """Transfer funds from the provided sender account to the receiver from the form."""
    if request.method == "POST":

        form = TransferFundsForm(request.POST)

        if form.is_valid():

            error_field, error_description = add_transaction(
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
```

This code uses the same template for the GET and the failed POST requests. For the GET it instantiates an empty form, while for the POST the form is instantiated with the user's data together with the errors and then it is forwarded to the same template as a context variable.

![Server side error](https://github.com/ipaleka/algodjango/blob/main/media/form-server-side-error.png?raw=true)

In the case of successfully validated form, the entered data is sent to the helper function where Algorand SDK tries to create a transaction. That is the second step in validation process and if Algorand SDK can't create a transaction from the provided data then we manually add the supplied error to the form and it is forwarded to the same template.

![SDK error](https://github.com/ipaleka/algodjango/blob/main/media/sdk-form-error.png?raw=true)

If Algorand SDK successfully manages to create a transaction, then a success message is created and request redirects to the starting account's page. Refresh the page after few seconds and both account's transactions should be displayed:

![Standalone account transactions](https://github.com/ipaleka/algodjango/blob/main/media/standalone-account-transactions.png?raw=true)


# Wallets creation

We created Algorand's standalone accounts in the previous sections that aren't connected to any wallet. Now we're going to create both the wallets and the accounts connected to them.

Update the app's URL configuration with all the URL we+re going to manage in this section:

`mainapp/urls.py`

```python
urlpatterns = [
    #
    path("wallets/", views.wallets, name="wallets"),
    path("create-wallet/", views.create_wallet, name="create-wallet"),
    path("wallet/<str:wallet_id>/", views.wallet, name="wallet"),
    path(
        "create-wallet-account/<str:wallet_id>/",
        views.create_wallet_account,
        name="create-wallet-account",
    ),
    path(
        "wallet-account/<str:wallet_id>/<str:address>/",
        views.wallet_account,
        name="wallet-account",
    ),
]
```

Our navigation bar located in the base template gets another item:

`mainapp\templates\mainapp\base.html`

```html
    <div class="topnav">
      <a href="/"{% if request.path == '/' %} class="active"{% endif %}>Standalone accounts</a>
      <a href="/wallets/"{% if request.path == '/wallets/' %} class="active"{% endif %}>Wallets</a>
    </div>
```

The wallets list page is similar to our index page where all the standalone accounts are displayed:

`mainapp\templates\mainapp\wallets.html`

```html
{% extends 'mainapp/base.html' %}
{% block title %}Wallets{% endblock %}
{% block body %}
  <h1>Wallets list</h1>
  {% if wallets %}
  <ul>
  {% for wallet in wallets %}
    <li><a href="/wallet/{{ wallet.wallet_id }}">{{ wallet.name }}</a></li>
  {% endfor %}
  </ul>
  {% else %}
  <p>There are no wallets.</p>
  {% endif %}
  <br>
  <a href="/create-wallet/">Create wallet</a>
{% endblock %}
```

![Wallets page](https://github.com/ipaleka/algodjango/blob/main/media/wallets-page.png?raw=true)


The page used for creating a new wallet should look familiar too:

`mainapp\templates\mainapp\create_wallet.html`

```html
{% extends 'mainapp/base.html' %}
{% block title %}Create wallet{% endblock %}
{% block body %}
  <h1>Create wallet</h1>
  <form action="/create-wallet/" method="post">
    {% csrf_token %}
    <table>{{ form.as_table }}</table>
    <input type="submit" value="Submit">
  </form>
{% endblock %}
```

A user defines the name and password of the wallet, while Algorand SDK creates its ID. Those are the wallet properties that we record in our database:

`mainapp\models.html`

```python

class Wallet(models.Model):
    """Model class for wallets."""

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
```

To retrieve a wallet object from the wallet ID string we use the class method `instance_from_id`. So, a call `Wallet.instance_from_id(id_string)` will either return the wallet instance or will raise the error if there's no wallet with provided `id_string` as its ID.

For the purpose of this tutorial and validation example, we define that a password can't consist just of numbers or just of letters:

`mainapp\forms.html`

```python
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
```

The most interesting thing in this section is the object-oriented capability of Django models that we're going to use for the account connected to wallets:

`mainapp\models.html`

```python
class WalletAccount(Account):
    """Model class for accounts belonging to wallets."""

    wallet = models.ForeignKey(Wallet, default=None, on_delete=models.CASCADE)
```

Our model is inherited from the old Account model and we just add a foreign key to the wallet it belongs to. We also use the Django template system to avoid redundancy:

`mainapp/templates/mainapp/wallet_account.html`

```html
{% extends 'mainapp/base_account.html' %}
{% block prefix %}Wallet{% endblock prefix %}
{% block start %}<p>Wallet: {{ wallet.name }} (ID: {{ wallet.wallet_id }})</p>{% endblock start %}
```

The page for displaying a wallet has a familiar structure:

`mainapp/templates/mainapp/wallet.html`

```html
{% extends 'mainapp/base.html' %}
{% block title %}Wallet page{% endblock %}
{% block body %}
  <h1>Wallet page</h1>
  <p>Name: {{ wallet.name }}</p>
  <p>ID: {{ wallet.wallet_id }}</p>
  <p>Created: {{ wallet.created }}</p>

  {% if messages %}
    <ul class="messages">
      {% for message in messages %}
        <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
      {% endfor %}
    </ul>
  {% endif %}

  <h2>Wallet accounts</h2>
  {% for account in wallet.walletaccount_set.all %}
    <li><a href="/wallet-account/{{ wallet.wallet_id }}/{{ account.address }}">{{ account.address }}</a> : {{ account.balance }} microAlgos</li>
  {% endfor %}
  <br>
  <a href="/create-wallet-account/{{ wallet.wallet_id }}/">Create wallet account</a>

{% endblock %}
```

The views and related code involved in the wallet creating and displaying processes follow the practice already presented in this tutorial:

`mainapp/views.py`

```python
from .forms import CreateWalletForm
from .helpers import add_wallet, get_wallet


def create_wallet(request):
    """Create wallet from the form data."""
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


def create_wallet_account(request, wallet_id):
    """Create account in the wallet with provided ID."""
    model = Wallet.instance_from_id(wallet_id)
    wallet = get_wallet(model.name, model.password)
    address = wallet.generate_key()
    WalletAccount.objects.create(wallet=model, address=address)
    message = "Address '{}' has been created in the wallet.".format(address)
    messages.add_message(request, messages.SUCCESS, message)
    return redirect("wallet", wallet_id)


def wallet(request, wallet_id):
    """Display information of the wallet with provided ID."""
    context = {"wallet": Wallet.instance_from_id(wallet_id)}
    return render(request, "mainapp/wallet.html", context)


def wallet_account(request, wallet_id, address):
    """Display information of the wallet account with provided address."""
    context = {
        "wallet": Wallet.instance_from_id(wallet_id),
        "account": Account.instance_from_address(address),
    }
    return render(request, "mainapp/wallet_account.html", context)


def wallets(request):
    """Display all the created wallets."""
    wallets = Wallet.objects.order_by("name")
    context = {"wallets": wallets}
    return render(request, "mainapp/wallets.html", context)
```

We use the [Key Management Daemon client](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/kmd.html#algosdk.kmd.KMDClient) for the purpose of creating and retrieving the wallets from the Algorand blockchain:

`mainapp/helpers.py`

```python
from algosdk import kmd
from algosdk.wallet import Wallet


def _kmd_client():
    """Instantiate and return kmd client object."""
    kmd_address = "http://localhost:4002"
    kmd_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return kmd.KMDClient(kmd_token, kmd_address)

def add_wallet(name, password):
    """Create wallet and return its ID."""
    try:
        wallet = Wallet(name, password, _kmd_client())
    except:
        return ""
    return wallet.id

def get_wallet(name, password):
    """Return wallet object from provided arguments."""
    return Wallet(name, password, _kmd_client())
```

A wallet object is returned if a user instantiates the [Wallet class](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/wallet.html#algosdk.wallet.Wallet) with a wallet name and a password. If such wallet doesn't exist then Algorand SDK simply creates it with that name and password.

Let's do one more thing before we move to the next section. If we now visit project's root/index page then both the standalone and wallet-based accounts will show up. Update the index view and use the Django object relational mapper to exclude the wallet-based accounts:

`mainapp/views.py`

```python
def index(request):
    #
    accounts = Account.objects.exclude(walletaccount__isnull=False).order_by("-created")
```


# Assets creation
