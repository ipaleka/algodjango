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


# Getting started with Algorand SDK

All the sections and code from previous sections can be used for the general purpose of creating web pages with Django. That introduction steps were needed to get you familiarized with the basic Django principles and now we're finally ready to start using Algorand SDK!


## Standalone account creation

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




**after creating the wallets accounts change the index 
    accounts = Account.objects.exclude(walletaccount__isnull=False).order_by("-created")


**update CSS file after adding 
- message
- form errors
- tables