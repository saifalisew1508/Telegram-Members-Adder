"""Create Telegram group invitation links using an authorized account.

This replaces automated scraping, unsolicited bulk adding and mass-DM actions
with an invitation workflow that lets people choose whether to join.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from colorama import Fore, Style, init
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import ExportChatInviteRequest

init(autoreset=True)

ROOT = Path(__file__).resolve().parent
SESSIONS = ROOT / "sessions"
ACCOUNTS_FILE = ROOT / "accounts.json"


def get_credentials() -> tuple[int, str]:
    api_id = os.getenv("TELEGRAM_API_ID", "").strip()
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    if not api_id.isdigit() or not api_hash:
        raise RuntimeError(
            "Set TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables. "
            "Get them from https://my.telegram.org."
        )
    return int(api_id), api_hash


def get_accounts() -> list[str]:
    if not ACCOUNTS_FILE.exists():
        return []
    try:
        data = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read accounts.json: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError("accounts.json must contain a JSON array.")
    result = []
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("phone"), str):
            phone = item["phone"].strip()
            if re.fullmatch(r"\+[1-9]\d{7,14}", phone):
                result.append(phone)
    return result


def main() -> None:
    try:
        api_id, api_hash = get_credentials()
        accounts = get_accounts()
        if not accounts:
            print(Fore.YELLOW + "No accounts found. Run python manager.py first.")
            return

        print("Saved accounts:")
        for number, phone in enumerate(accounts, 1):
            print(f"{number}. {phone}")
        selection = input("Choose account number: ").strip()
        if not selection.isdigit() or not 1 <= int(selection) <= len(accounts):
            print(Fore.RED + "Invalid account selection.")
            return

        phone = accounts[int(selection) - 1]
        group = input("Group/channel username or link: ").strip()
        if not group:
            print(Fore.RED + "A group or channel is required.")
            return

        client = TelegramClient(
            str(SESSIONS / re.sub(r"[^0-9+]", "", phone)), api_id, api_hash
        )
        try:
            client.start(phone=phone)
            entity = client.get_entity(group)
            result = client(ExportChatInviteRequest(peer=entity))
            print(Fore.GREEN + "\nInvitation link created:")
            print(result.link)
            print(
                Fore.CYAN
                + "\nShare this link with people who have agreed to join. "
                "Telegram may require you to be an administrator."
            )
        finally:
            client.disconnect()
    except (RuntimeError, ValueError) as exc:
        print(Fore.RED + str(exc))
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as exc:
        print(Fore.RED + f"Operation failed: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
