# Introduction

The purpose of this tutorial is to introduce the reader to the Algorand SDK and its implementation in Django framework.



**xyz**


# Requirements

This tutorial uses a Python wrapper around Algorand SDK, so you should have Python 3 installed on your system. Also, this tutorial uses `python3-venv` package for creating virtual environments and you have to install it if it's not already installed in your system. For a Debian/Ubuntu based systems, you can do that by issuing the following command:

```bash
$ sudo apt-get install python3-venv
```

In order to clone the Algorand Sandbox (as opposite to just download its installation archive), you'll also need [Git](https://git-scm.com/).


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
├── algorand-django
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

We need one more thing before we start writting our app code. Use your favorite editor and open the `settings.py` file placed in the project's directory. Find the `INSTALLED_APPS` setting and prepend the list with our app's configuration class. Afterward, that setting should look like this:

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

Point your server to the presented URL (http://127.0.0.1:8000/) and you should see a page similar to the following one:

![Django starting page](https://github.com/ipaleka/algorand-django/blob/main/media/django-starting-page.png?raw=true)

If all goes well then you're ready to start writing code for your Algorand application.

