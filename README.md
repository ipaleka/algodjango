![algodjango](https://github.com/ipaleka/algodjango/blob/main/media/algodjango.png?raw=true)

Django project presenting some Algorand's blockchain processes with the help of `py-algorand-sdk` package.

---
**Security warning**

This project has not been audited and should not be used in a production environment.

---

# Requirements

You should have Python 3 installed on your system. Also, this tutorial uses `python3-venv` for creating virtual environments - install it in a Debian/Ubuntu based systems by issuing the following command:

```bash
$ sudo apt-get install python3-venv
```

[Algorand Sandbox](https://github.com/algorand/sandbox) must be installed on your computer. It is implied that the Sandbox executable is in the `sandbox` directory next to this project directory:

```bash
$ tree -L 1
.
├── algodjango
└── sandbox
```

If that's not the case, then you should set `SANDBOX_DIR` environment variable holding sandbox directory before running the Django development server, like the following:

```bash
export SANDBOX_DIR="/home/ipaleka/dev/algorand/sandbox"
```

If you want to clone the repositories, not just download them, then you should have Git installed on your computer.

And finally, keeping secrets in a public repository is not recommended so our code implies you set an environment variable for the Django SECRET_KEY:

```bash
export SECRET_KEY="my-django-secret-key"
```


# Setup

At first create the root directory:

```bash
cd ~
mkdir algorand
cd algorand
```

Then clone both repositories:

```bash
git clone https://github.com/ipaleka/algodjango.git
git clone https://github.com/algorand/sandbox.git
```

Start the Sandbox and wait until it's ready:

```bash
./sandbox/sandbox up
```

As always for the Python-based projects, you should create a Python environment and activate it:

```bash
python3 -m venv algovenv
source algovenv/bin/activate
```

Now change the directory to the project root directory and install the project dependencies with:

```bash
(algovenv) $ pip install -r requirements.txt
```

After that, you'll be able to start the Django development server:

```bash
(algovenv) $ cd algodjango
(algovenv) $ python manage.py runserver
```

Point your browser to http://127.0.0.1:8000/ and you should see the starting page:

![algodjango starting page](https://github.com/ipaleka/algodjango/blob/main/media/starting-page.png?raw=true)


# Troubleshooting

If you want a fresh start, issue the following for the Sandbox:

```bash
./sandbox/sandbox clean
./sandbox/sandbox up
```

Then delete the SQLite database file and recreate it with the `migrate` Django management command:

```bash
(algovenv) $ cd algodjango
(algovenv) $ rm db.sqlite3
(algovenv) $ python manage.py migrate
```
