"""Manage Telegram user sessions safely.

Set TELEGRAM_API_ID and TELEGRAM_API_HASH in the environment before running.
Account metadata is stored as JSON; session files remain in ./sessions.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from colorama import Fore, Style, init
from telethon.sync import TelegramClient

init(autoreset=True)

ROOT = Path(__file__).resolve().parent
SESSIONS = ROOT / "sessions"
ACCOUNTS_FILE = ROOT / "accounts.json"


def credentials() -> tuple[int, str]:
    api_id = os.getenv("TELEGRAM_API_ID", "").strip()
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    if not api_id.isdigit() or not api_hash:
        raise RuntimeError(
            "Set TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables. "
            "Get them from https://my.telegram.org."
        )
    return int(api_id), api_hash


def load_accounts() -> list[dict[str, str]]:
    if not ACCOUNTS_FILE.exists():
        return []
    try:
        data: Any = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read {ACCOUNTS_FILE.name}: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError("accounts.json must contain a JSON array.")
    accounts = []
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("phone"), str):
            phone = item["phone"].strip()
            if phone:
                accounts.append({"phone": phone})
    return accounts


def save_accounts(accounts: list[dict[str, str]]) -> None:
    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = ACCOUNTS_FILE.with_suffix(".json.tmp")
    temp.write_text(json.dumps(accounts, indent=2) + "\n", encoding="utf-8")
    temp.replace(ACCOUNTS_FILE)


def session_path(phone: str) -> Path:
    safe = re.sub(r"[^0-9+]", "", phone)
    if not safe:
        raise ValueError("Invalid phone number.")
    return SESSIONS / safe


def login_account(phone: str) -> None:
    api_id, api_hash = credentials()
    SESSIONS.mkdir(parents=True, exist_ok=True)
    client = TelegramClient(str(session_path(phone)), api_id, api_hash)
    try:
        client.start(phone=phone)
        me = client.get_me()
        label = " ".join(part for part in [me.first_name, me.last_name] if part)
        print(Fore.GREEN + f"Login successful: {label or me.username or phone}")
    finally:
        client.disconnect()


def add_account() -> None:
    phone = input("Phone number with country code (e.g. +919876543210): ").strip()
    if not re.fullmatch(r"\+[1-9]\d{7,14}", phone):
        print(Fore.RED + "Enter a valid international phone number.")
        return
    accounts = load_accounts()
    if any(item["phone"] == phone for item in accounts):
        print(Fore.YELLOW + "This account is already registered.")
        return
    login_account(phone)
    accounts.append({"phone": phone})
    save_accounts(accounts)
    print(Fore.GREEN + "Account saved.")


def check_accounts() -> None:
    accounts = load_accounts()
    if not accounts:
        print("No accounts saved yet.")
        return
    api_id, api_hash = credentials()
    for account in accounts:
        phone = account["phone"]
        client = TelegramClient(str(session_path(phone)), api_id, api_hash)
        try:
            client.connect()
            if client.is_user_authorized():
                me = client.get_me()
                name = " ".join(x for x in [me.first_name, me.last_name] if x)
                print(Fore.GREEN + f"[AUTHORIZED] {phone} - {name}")
            else:
                print(Fore.YELLOW + f"[LOGIN REQUIRED] {phone}")
        except Exception as exc:
            print(Fore.RED + f"[ERROR] {phone}: {type(exc).__name__}: {exc}")
        finally:
            client.disconnect()


def remove_account() -> None:
    accounts = load_accounts()
    if not accounts:
        print("No accounts saved.")
        return
    for index, item in enumerate(accounts, 1):
        print(f"{index}. {item['phone']}")
    raw = input("Account number to remove: ").strip()
    if not raw.isdigit() or not 1 <= int(raw) <= len(accounts):
        print(Fore.RED + "Invalid selection.")
        return
    account = accounts.pop(int(raw) - 1)
    save_accounts(accounts)
    if input("Also delete its local session file? [y/N]: ").strip().lower() == "y":
        path = session_path(account["phone"]).with_suffix(".session")
        if path.exists():
            path.unlink()
    print(Fore.GREEN + "Account removed.")


def main() -> None:
    while True:
        print("\n=== Telegram Account Manager ===")
        print("1. Add/login account")
        print("2. Check saved sessions")
        print("3. Remove account")
        print("4. Exit")
        choice = input("Select: ").strip()
        try:
            if choice == "1":
                add_account()
            elif choice == "2":
                check_accounts()
            elif choice == "3":
                remove_account()
            elif choice == "4":
                break
            else:
                print(Fore.YELLOW + "Choose 1, 2, 3, or 4.")
        except (RuntimeError, ValueError) as exc:
            print(Fore.RED + str(exc))
        except KeyboardInterrupt:
            print("\nCancelled.")
        except Exception as exc:
            print(Fore.RED + f"Operation failed: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
