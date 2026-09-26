"""Manage Telegram sessions used by the adder.

The script intentionally uses Telethon's synchronous convenience API, so every
request in this file is completed before the next menu action is displayed.
"""

from __future__ import annotations

import pickle
from pathlib import Path

from colorama import Fore, init
from telethon.sync import TelegramClient
from telethon.errors import PhoneNumberBannedError

init(autoreset=True)

API_ID = 3910389
API_HASH = "86f861352f0ab76a251866059a6adbd6"
ACCOUNTS_FILE = Path("vars.txt")
SESSIONS_DIR = Path("sessions")


def load_accounts() -> list[str]:
    """Read the legacy pickle stream, ignoring an absent or empty file."""
    if not ACCOUNTS_FILE.exists():
        return []

    accounts: list[str] = []
    with ACCOUNTS_FILE.open("rb") as account_file:
        while True:
            try:
                record = pickle.load(account_file)
            except EOFError:
                break
            if isinstance(record, (list, tuple)) and record:
                phone = str(record[0])
                if phone not in accounts:
                    accounts.append(phone)
    return accounts


def save_accounts(accounts: list[str]) -> None:
    with ACCOUNTS_FILE.open("wb") as account_file:
        for phone in accounts:
            pickle.dump([phone], account_file)


def client_for(phone: str) -> TelegramClient:
    SESSIONS_DIR.mkdir(exist_ok=True)
    return TelegramClient(str(SESSIONS_DIR / phone), API_ID, API_HASH)


def add_new_accounts() -> None:
    try:
        count = int(input("How many accounts would you like to add? "))
    except ValueError:
        print(Fore.RED + "Enter a whole number.")
        return
    if count <= 0:
        print(Fore.RED + "The number of accounts must be positive.")
        return

    accounts = load_accounts()
    for _ in range(count):
        phone = "".join(input("Phone number with country code: ").split())
        if not phone:
            print(Fore.YELLOW + "Skipped an empty phone number.")
            continue
        if phone in accounts:
            print(Fore.YELLOW + f"{phone} is already saved.")
            continue
        try:
            with client_for(phone) as client:
                client.start(phone=phone)
            accounts.append(phone)
            print(Fore.GREEN + f"Login successful for {phone}.")
        except PhoneNumberBannedError:
            print(Fore.RED + f"{phone} is banned and was not saved.")
        except Exception as exc:
            print(Fore.RED + f"Could not log in to {phone}: {exc}")
    save_accounts(accounts)


def filter_banned_accounts() -> None:
    accounts = load_accounts()
    if not accounts:
        print(Fore.YELLOW + "There are no saved accounts.")
        return

    active: list[str] = []
    for phone in accounts:
        try:
            with client_for(phone) as client:
                if client.is_user_authorized():
                    active.append(phone)
                    print(Fore.GREEN + f"{phone} has an active session.")
                else:
                    client.send_code_request(phone)
                    active.append(phone)
                    print(Fore.GREEN + f"{phone} is not banned (login required).")
        except PhoneNumberBannedError:
            print(Fore.RED + f"{phone} is banned and has been removed.")
        except Exception as exc:
            # Do not discard an account merely because the network is unavailable.
            active.append(phone)
            print(Fore.YELLOW + f"Could not check {phone}; keeping it: {exc}")
    save_accounts(active)


def delete_specific_account() -> None:
    accounts = load_accounts()
    if not accounts:
        print(Fore.YELLOW + "There are no saved accounts.")
        return
    for index, phone in enumerate(accounts, start=1):
        print(f"[{index}] {phone}")
    try:
        index = int(input("Account to delete: ")) - 1
        phone = accounts.pop(index)
    except (ValueError, IndexError):
        print(Fore.RED + "Choose a valid account number.")
        return

    session_file = SESSIONS_DIR / f"{phone}.session"
    session_file.unlink(missing_ok=True)
    # SQLite can leave these auxiliary files after an interrupted session.
    for suffix in ("-journal", "-shm", "-wal"):
        (SESSIONS_DIR / f"{phone}.session{suffix}").unlink(missing_ok=True)
    save_accounts(accounts)
    print(Fore.GREEN + f"Deleted {phone}.")


def display_all_accounts() -> None:
    accounts = load_accounts()
    if accounts:
        print("\n".join(accounts))
    else:
        print(Fore.YELLOW + "There are no saved accounts.")


def main() -> None:
    actions = {
        "1": add_new_accounts,
        "2": filter_banned_accounts,
        "3": delete_specific_account,
        "4": display_all_accounts,
    }
    while True:
        print("\n[1] Add accounts\n[2] Filter banned accounts\n[3] Delete an account\n[4] List accounts\n[5] Quit")
        choice = input("Enter your choice: ").strip()
        if choice == "5":
            return
        action = actions.get(choice)
        if action is None:
            print(Fore.RED + "Choose an option from the menu.")
        else:
            action()


if __name__ == "__main__":
    main()
