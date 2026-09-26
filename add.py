"""Telegram group utilities compatible with current Telethon 1.x releases."""

from __future__ import annotations

import pickle
import time
from pathlib import Path

from colorama import Fore, init
from telethon.errors import (
    ChatAdminRequiredError,
    ChatWriteForbiddenError,
    FloodWaitError,
    PeerFloodError,
    PhoneNumberBannedError,
    UserAlreadyParticipantError,
    UserBannedInChannelError,
    UserPrivacyRestrictedError,
)
from telethon.sync import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest, ImportChatInviteRequest
from telethon.tl.types import Channel, InputReportReasonOther

init(autoreset=True)

API_ID = 3910389
API_HASH = "86f861352f0ab76a251866059a6adbd6"
ACCOUNTS_FILE = Path("vars.txt")
SESSIONS_DIR = Path("sessions")


def load_accounts() -> list[str]:
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


def client_for(phone: str) -> TelegramClient:
    SESSIONS_DIR.mkdir(exist_ok=True)
    return TelegramClient(str(SESSIONS_DIR / phone), API_ID, API_HASH)


def invite_hash(link: str) -> str | None:
    """Return the hash from both current (t.me/+) and legacy invite URLs."""
    link = link.strip().rstrip("/")
    if "/joinchat/" in link:
        return link.rsplit("/joinchat/", 1)[1]
    if "/+" in link:
        return link.rsplit("/+", 1)[1]
    return None


def join(client: TelegramClient, link: str):
    hash_ = invite_hash(link)
    if hash_:
        try:
            result = client(ImportChatInviteRequest(hash_))
            return result.chats[0]
        except UserAlreadyParticipantError:
            return client.get_entity(link)
    try:
        client(JoinChannelRequest(link))
    except UserAlreadyParticipantError:
        pass
    return client.get_entity(link)


def with_authorized_accounts(action) -> None:
    accounts = load_accounts()
    if not accounts:
        print(Fore.YELLOW + "No accounts are saved. Run manager.py first.")
        return
    for phone in accounts:
        try:
            with client_for(phone) as client:
                if not client.is_user_authorized():
                    print(Fore.YELLOW + f"Skipping {phone}: login required.")
                    continue
                action(client, phone)
        except PhoneNumberBannedError:
            print(Fore.RED + f"Skipping {phone}: account is banned.")
        except Exception as exc:
            print(Fore.RED + f"{phone}: {exc}")


def send_messages() -> None:
    recipient = input("Recipient username, ID, or link: ").strip()
    message = input("Message: ")
    if not recipient or not message:
        print(Fore.RED + "A recipient and message are required.")
        return
    def send(client: TelegramClient, phone: str) -> None:
        client.send_message(recipient, message)
        print(Fore.GREEN + f"Message sent from {phone}.")

    with_authorized_accounts(send)


def change_membership(request_type, verb: str) -> None:
    link = input(f"Group or channel link to {verb}: ").strip()
    if not link:
        return
    def change(client: TelegramClient, phone: str) -> None:
        client(request_type(link))
        print(Fore.GREEN + f"{verb.title()} from {phone}.")

    with_authorized_accounts(change)


def report_group() -> None:
    link = input("Group or channel link to report: ").strip()
    message = input("Report reason: ").strip()
    if not link or not message:
        print(Fore.RED + "A link and report reason are required.")
        return

    def report(client: TelegramClient, phone: str) -> None:
        # Telethon expects an InputReportReason object, not a plain string.
        client(ReportPeerRequest(link, InputReportReasonOther(), message))
        print(Fore.GREEN + f"Report submitted from {phone}.")

    with_authorized_accounts(report)


def add_members() -> None:
    source_link = input("Source group link: ").strip()
    target_link = input("Target group link: ").strip()
    try:
        per_account = int(input("Members per account [60]: ") or "60")
        delay = float(input("Delay between requests in seconds [30]: ") or "30")
    except ValueError:
        print(Fore.RED + "The member count and delay must be numbers.")
        return
    if not source_link or not target_link or per_account < 1 or delay < 0:
        print(Fore.RED + "Provide valid links, a positive count, and a non-negative delay.")
        return

    offset = 0

    def add_for_account(client: TelegramClient, phone: str) -> None:
        nonlocal offset
        source = join(client, source_link)
        target = join(client, target_link)
        members = list(client.iter_participants(source, limit=offset + per_account))[offset:offset + per_account]
        if not members:
            print(Fore.YELLOW + "No more accessible members to add.")
            return
        for user in members:
            try:
                if isinstance(target, Channel):
                    client(InviteToChannelRequest(target, [user]))
                else:
                    client(AddChatUserRequest(target.id, user, fwd_limit=0))
                print(Fore.GREEN + f"{phone}: added {user.id}.")
                time.sleep(delay)
            except UserPrivacyRestrictedError:
                print(Fore.YELLOW + f"{user.id}: privacy settings prevent adding.")
            except UserAlreadyParticipantError:
                print(Fore.YELLOW + f"{user.id}: already a participant.")
            except FloodWaitError as exc:
                print(Fore.RED + f"{phone}: flood wait for {exc.seconds} seconds; stopping this account.")
                break
            except (PeerFloodError, ChatAdminRequiredError, ChatWriteForbiddenError, UserBannedInChannelError) as exc:
                print(Fore.RED + f"{phone}: cannot add members: {exc}")
                break
        # Advance past every member considered, including users Telegram rejected,
        # so that a later account does not repeatedly attempt the same people.
        offset += len(members)

    with_authorized_accounts(add_for_account)


def main() -> None:
    actions = {
        "1": add_members,
        "2": send_messages,
        "3": lambda: change_membership(JoinChannelRequest, "join"),
        "4": lambda: change_membership(LeaveChannelRequest, "leave"),
        "5": report_group,
    }
    print("\n[1] Add members\n[2] Send messages\n[3] Join a group/channel\n[4] Leave a group/channel\n[5] Report a group/channel")
    action = actions.get(input("Enter your choice: ").strip())
    if action is None:
        print(Fore.RED + "Choose an option from the menu.")
        return
    action()


if __name__ == "__main__":
    main()
