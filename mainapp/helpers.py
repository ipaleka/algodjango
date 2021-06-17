import io
import os
import subprocess
from pathlib import Path

from algosdk import account, kmd, mnemonic
from algosdk.future.transaction import PaymentTxn
from algosdk.v2client import algod
from algosdk.wallet import Wallet

from algosdk.error import WrongChecksumError


def _algod_client():
    """Instantiate and return Algod client object."""
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return algod.AlgodClient(algod_token, algod_address)


def _kmd_client():
    """Instantiate and return kmd client object."""
    kmd_address = "http://localhost:4002"
    kmd_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return kmd.KMDClient(kmd_token, kmd_address)


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


def account_balance(address):
    """Return funds balance of the account having provided address."""
    account_info = _algod_client().account_info(address)
    return account_info.get("amount")


def add_standalone_account():
    """Create standalone account and return two-tuple of its address and passphrase."""
    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)
    return address, passphrase


def add_wallet(name, password):
    """Create wallet and return its ID."""
    try:
        wallet = Wallet(name, password, _kmd_client())
    except:
        return ""
    return wallet.id


def cli_account_list():
    """Return list of accounts and coresponding balances in microAlgos."""
    process = _call_sandbox_command("goal", "account", "list")
    accounts = []
    for line in io.TextIOWrapper(process.stdout):
        current = line.split()
        accounts.append((current[1], int(current[3])))

    return accounts


def cli_passphrase_for_account(address):
    """Return passphrase for provided address."""
    process = _call_sandbox_command("goal", "account", "export", "-a", address)
    for line in io.TextIOWrapper(process.stdout):
        parts = line.split('"')
        passphrase = parts[1] if len(parts) > 1 else ""
    return passphrase


def create_transaction(sender, receiver, passphrase, amount, note):
    """Create and sign transaction from provided arguments.

    Returned non-empty tuple carries field where error was raised and description.
    If the first item is None then the error is non-field/integration error.
    Returned two-tuple of empty strings marks successful transaction.
    """

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


def get_wallet(name, password):
    """Return wallet object from provided arguments."""
    return Wallet(name, password, _kmd_client())
