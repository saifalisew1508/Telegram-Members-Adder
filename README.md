# Telegram Group Invitation Tool

A small Telethon-based command-line utility for managing your own Telegram sessions and creating invitation links for groups/channels you administer.

## Requirements

- Python 3.10+
- A Telegram API ID and API hash from https://my.telegram.org
- Permission to create invite links in the destination group/channel

## Installation

```bash
git clone https://github.com/saifalisew1508/Telegram-Members-Adder.git
cd Telegram-Members-Adder
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configure API credentials

Set these environment variables before running either script. Do not commit API credentials or session files.

Linux/macOS:
```bash
export TELEGRAM_API_ID="YOUR_API_ID"
export TELEGRAM_API_HASH="YOUR_API_HASH"
```

Windows PowerShell:
```powershell
$env:TELEGRAM_API_ID="YOUR_API_ID"
$env:TELEGRAM_API_HASH="YOUR_API_HASH"
```

## Account manager

```bash
python manager.py
```

Use the menu to log in to an account, check saved sessions, or remove an account. Account phone numbers are stored in `accounts.json`; Telethon session files are stored in `sessions/`.

## Create a group invitation link

```bash
python add.py
```

Choose an authorized account and enter the group/channel username or link. The account must have permission to create invite links. Share the generated link with people who want to join.

## Privacy and safety

- Never share your `sessions/` directory, `accounts.json`, API hash, login codes, or 2FA password.
- Session files grant access to Telegram accounts. Keep them private and back them up securely.
- This project intentionally uses invitation links instead of scraping members, unsolicited bulk adding, or mass-DM automation. Respect Telegram's Terms and each group's privacy settings.
- The old `vars.txt` pickle format is no longer used. Add accounts again with `manager.py`; do not load untrusted pickle files.

## Troubleshooting

- `Set TELEGRAM_API_ID...`: configure both environment variables in the same terminal session.
- `LOGIN REQUIRED`: use the account manager to log in again.
- Invite-link permission errors: ask a group administrator to grant permission to create invite links.
- For dependency issues, recreate the virtual environment and run `pip install -r requirements.txt`.
