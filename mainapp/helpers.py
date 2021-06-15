import io
import os
import subprocess
from pathlib import Path


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


def _call_sandbox_command(*args):
    """Call and return sandbox command composed from provided arguments."""
    return subprocess.Popen(
        [_sandbox_executable(), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def cli_account_list():
    """Return dictionary of accounts and coresponding balances in microAlgos."""
    process = _call_sandbox_command("goal", "account", "list")
    accounts = {}
    for line in io.TextIOWrapper(process.stdout):
        current = line.split()
        accounts[current[1]] = int(current[3])

    return accounts
