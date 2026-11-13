"""Telegram group utility.

Features are intentionally limited to group announcements, individual moderation,
admin-roster export, and opt-in invitation links.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from colorama import Fore, init
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

init(autoreset=True)
ROOT = Path(__file__).resolve().parent
SESSIONS = ROOT / "sessions"
ACCOUNTS_FILE = ROOT / "accounts.json"
USERS_FILE = ROOT / "users.json"


def credentials() -> tuple[int, str]:
    api_id, api_hash = os.getenv("TELEGRAM_API_ID", "").strip(), os.getenv("TELEGRAM_API_HASH", "").strip()
    if not api_id.isdigit() or not api_hash:
        raise RuntimeError("Set TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables.")
    return int(api_id), api_hash


def accounts() -> list[str]:
    if not ACCOUNTS_FILE.exists():
        return []
    data = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise RuntimeError("accounts.json must contain a JSON array.")
    return [x["phone"] for x in data if isinstance(x, dict) and isinstance(x.get("phone"), str)]


def choose_account() -> str:
    saved = accounts()
    if not saved:
        raise RuntimeError("No accounts saved. Run python manager.py first.")
    for i, phone in enumerate(saved, 1):
        print(f"{i}. {phone}")
    choice = input("Select account: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(saved):
        raise ValueError("Invalid account selection.")
    return saved[int(choice) - 1]


def with_client():
    api_id, api_hash = credentials()
    phone = choose_account()
    SESSIONS.mkdir(parents=True, exist_ok=True)
    client = TelegramClient(str(SESSIONS / re.sub(r"[^0-9+]", "", phone)), api_id, api_hash)
    client.start(phone=phone)
    return client


def group_entity(client):
    group = input("Group/channel username, link, or ID: ").strip()
    if not group:
        raise ValueError("Group/channel is required.")
    return client.get_entity(group)


def confirm(action: str, target: str) -> bool:
    print(Fore.YELLOW + f"\nYou are about to {action}: {target}")
    return input("Type CONFIRM to continue: ").strip() == "CONFIRM"


def send_group_announcement() -> None:
    client = with_client()
    try:
        entity = group_entity(client)
        print("This sends ONE message to the group, not private messages to members.")
        message = input("Announcement text (e.g. Good morning!): ").strip()
        if not message:
            print("Message cannot be empty.")
            return
        title = getattr(entity, "title", str(entity))
        if confirm("send a group announcement in", title):
            client.send_message(entity, message)
            print(Fore.GREEN + "Announcement sent to the group.")
    finally:
        client.disconnect()


def moderate_one_member(unban: bool = False) -> None:
    client = with_client()
    try:
        entity = group_entity(client)
        user_ref = input("Target member username or numeric user ID: ").strip()
        if not user_ref:
            raise ValueError("A member username or ID is required.")
        user = client.get_entity(int(user_ref) if user_ref.lstrip("-").isdigit() else user_ref)
        label = f"{getattr(user, 'first_name', '')} (@{getattr(user, 'username', None) or 'no username'}, ID {user.id})"
        action = "unban" if unban else "ban"
        if not confirm(action, label):
            print("Cancelled.")
            return
        rights = ChatBannedRights(
            until_date=None,
            view_messages=not unban,
            send_messages=False if unban else True,
            send_media=False if unban else True,
            send_stickers=False if unban else True,
            send_gifs=False if unban else True,
            send_games=False if unban else True,
            send_inline=False if unban else True,
            embed_links=False if unban else True,
        )
        client(EditBannedRequest(entity, user, rights))
        print(Fore.GREEN + f"Member {action} completed.")
    finally:
        client.disconnect()


def export_admin_roster() -> None:
    client = with_client()
    try:
        entity = group_entity(client)
        title = getattr(entity, "title", str(entity))
        records = []
        for user in client.iter_participants(entity, filter=ChannelParticipantsAdmins):
            records.append({
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_bot": user.bot,
            })
        payload = {
            "group": title,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "scope": "administrators_only",
            "users": records,
        }
        USERS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(Fore.GREEN + f"Saved {len(records)} administrator records to {USERS_FILE.name}.")
    finally:
        client.disconnect()


def create_invite_link() -> None:
    client = with_client()
    try:
        entity = group_entity(client)
        if not confirm("create an invitation link for", getattr(entity, "title", str(entity))):
            print("Cancelled.")
            return
        invite = client(ExportChatInviteRequest(peer=entity))
        print(Fore.GREEN + "\nInvitation link (share only with people who choose to join):")
        print(invite.link)
    finally:
        client.disconnect()


def main() -> None:
    actions = {
        "1": ("Send a group announcement (e.g. Good morning)", send_group_announcement),
        "2": ("Ban one member", lambda: moderate_one_member(False)),
        "3": ("Unban one member", lambda: moderate_one_member(True)),
        "4": ("Export group administrators to users.json", export_admin_roster),
        "5": ("Create an opt-in group invitation link", create_invite_link),
    }
    while True:
        print(Fore.CYAN + "\n===== TELEGRAM GROUP MANAGER =====")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("6. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "6":
            break
        action = actions.get(choice)
        if not action:
            print(Fore.YELLOW + "Choose a number from 1 to 6.")
            continue
        try:
            action[1]()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        except Exception as exc:
            print(Fore.RED + f"Error: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
