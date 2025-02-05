'''
================SAIFALISEW1508=====================
Telegram members adding script
Coded by a kid- github.com/saifalisew1508
Apologies if anything in the code is dumb :)
Copy with credits
************************************************
'''

# import libraries
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerChannel
from telethon.errors.rpcerrorlist import (
    PeerFloodError, UserPrivacyRestrictedError, PhoneNumberBannedError, 
    ChatAdminRequiredError, ChatWriteForbiddenError, UserBannedInChannelError, 
    UserAlreadyParticipantError, FloodWaitError
)
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, AddChatUserRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest, ReportChannelRequest
from telethon.tl.types import UserStatusRecently
import sys
import time
import random
from colorama import init, Fore
import os
import pickle

init()

# Define colors for console output
r = Fore.RED
lg = Fore.GREEN
n = Fore.RESET
w = Fore.WHITE
grey = '\033[97m'
cy = Fore.CYAN
ye = Fore.YELLOW
colors = [r, lg, w, ye, cy]
info = f'{lg}[{w}i{lg}]{n}'
error = f'{lg}[{r}!{lg}]{n}'
success = f'{w}[{lg}*{w}]{n}'
INPUT = f'{lg}[{cy}~{lg}]{n}'
plus = f'{w}[{lg}+{w}]{n}'
minus = f'{w}[{lg}-{w}]{n}'

def banner():
    # Fancy logo
    b = [
    '░█████╗░██████╗░██████╗░███████╗██████╗░',
    '██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗',
    '███████║██║░░██║██║░░██║█████╗░░██████╔╝',
    '██╔══██║██║░░██║██║░░██║██╔══╝░░██╔══██╗',
    '██║░░██║██████╔╝██████╔╝███████╗██║░░██║',
    '╚═╝░░╚═╝╚═════╝░╚═════╝░╚══════╝╚═╝░░╚═╝'
    ]
    for char in b:
        print(f'{random.choice(colors)}{char}{n}')
    print('Contact below address for get premium script')
    print(f'{lg}Version: {w}2.0{lg} | GitHub: {w}@saifalisew1508{n}')
    print(f'{lg}Telegram: {w}@DearSaif{lg} | Instagram: {w}@_Prince.Babu_{n}')

# Function to clear screen
def clr():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

accounts = []
with open('vars.txt', 'rb') as f:
    while True:
        try:
            accounts.append(pickle.load(f))
        except EOFError:
            break

# Create sessions and check for banned accounts
print('\n' + info + lg + ' Checking for banned accounts...' + rs)
banned = []
for a in accounts:
    phn = a[0]
    print(f'{plus}{grey} Checking {lg}{phn}')
    clnt = TelegramClient(f'sessions/{phn}', 3910389, '86f861352f0ab76a251866059a6adbd6')
    clnt.connect()
    if not clnt.is_user_authorized():
        try:
            clnt.send_code_request(phn)
            print('OK')
        except PhoneNumberBannedError:
            print(f'{error} {w}{phn} {r}is banned!{rs}')
            banned.append(a)
    clnt.disconnect()

for z in banned:
    accounts.remove(z)
    print(info + lg + ' Banned account removed[Remove permanently using manager.py]' + rs)
    time.sleep(0.5)

print(f'{info} Sessions created!')
clr()
banner()

# Function to log scraping details
def log_status(scraped, index):
    with open('status.dat', 'wb') as f:
        pickle.dump([scraped, int(index)], f)
    print(f'{info}{lg} Session stored in {w}status.dat{lg}')

def exit_window():
    input(f'\n{cy} Press enter to exit...')
    clr()
    banner()
    sys.exit()

# Function to send message using all accounts
def send_message_all_accounts():
    message = input(f'\n{lg} [~] Enter the message to send: {r}')
    promotional_message = "This message was sent using mass DM tool GitHub.com/saifalisew1508/Telegram-Members-Adder"
    full_message = f"{message}\n\n{promotional_message}"
    for account in accounts:
        phone = str(account[0])
        client = TelegramClient(f'sessions/{phone}', 3910389, '86f861352f0ab76a251866059a6adbd6')
        client.connect()
        if client.is_user_authorized():
            try:
                client.send_message("me", full_message)  # Sending to self for demo; replace "me" with target ID
                print(f'{lg}[+] Message sent from {phone}')
            except Exception as e:
                print(f'{r}[!] Failed to send message from {phone}: {e}')
        client.disconnect()
    input('\nPress enter to exit...')

# Function to join a group or channel using all accounts
def join_group_all_accounts():
    link = input(f'\n{lg} [~] Enter the group/channel link to join: {r}')
    for account in accounts:
        phone = str(account[0])
        client = TelegramClient(f'sessions/{phone}', 3910389, '86f861352f0ab76a251866059a6adbd6')
        client.connect()
        if client.is_user_authorized():
            try:
                client(JoinChannelRequest(link))
                print(f'{lg}[+] Joined group/channel from {phone}')
            except Exception as e:
                print(f'{r}[!] Failed to join from {phone}: {e}')
        client.disconnect()
    input('\nPress enter to exit...')

# Function to leave a group or channel using all accounts
def leave_group_all_accounts():
    link = input(f'\n{lg} [~] Enter the group/channel link to leave: {r}')
    for account in accounts:
        phone = str(account[0])
        client = TelegramClient(f'sessions/{phone}', 3910389, '86f861352f0ab76a251866059a6adbd6')
        client.connect()
        if client.is_user_authorized():
            try:
                client(LeaveChannelRequest(link))
                print(f'{lg}[+] Left group/channel from {phone}')
            except Exception as e:
                print(f'{r}[!] Failed to leave from {phone}: {e}')
        client.disconnect()
    input('\nPress enter to exit...')

# Function to report a group or channel using all accounts
def report_group_all_accounts():
    link = input(f'\n{lg} [~] Enter the group/channel link to report: {r}')
    reason = input(f'\n{lg} [~] Enter the reason for reporting: {r}')
    for account in accounts:
        phone = str(account[0])
        client = TelegramClient(f'sessions/{phone}', 3910389, '86f861352f0ab76a251866059a6adbd6')
        client.connect()
        if client.is_user_authorized():
            try:
                client(ReportChannelRequest(link, reason))
                print(f'{lg}[+] Reported group/channel from {phone}')
            except Exception as e:
                print(f'{r}[!] Failed to report from {phone}: {e}')
        client.disconnect()
    input('\nPress enter to exit...')

# Function to scrape messages and add hidden members from a group to a desired group or channel
def add_hidden_members_from_group():
    source_group = input(f'\n{lg} [~] Enter the group url link to scrape messages from: {r}')
    target_group = input(f'\n{lg} [~] Enter the target group/channel url link to add members: {r}')
    for account in accounts:
        phone = str(account[0])
        client = TelegramClient(f'sessions/{phone}', 3910389, '86f861352f0ab76a251866059a6adbd6')
        client.connect()
        if client.is_user_authorized():
            try:
                messages = client.get_messages(source_group, limit=100)  # Scraping last 100 messages
                users = set()
                for message in messages:
                    if message.from_id:
                        users.add(message.from_id)
                print(f'{lg}[+] Scraped {len(users)} users from {source_group}')
                for user in users:
                    try:
                        client(InviteToChannelRequest(target_group, [user]))
                        print(f'{lg}[+] Added user {user} to {target_group}')
                    except Exception as e:
                        print(f'{r}[!] Failed to add user {user} to {target_group}: {e}')
            except Exception as e:
                print(f'{r}[!] Failed to scrape messages from {source_group}: {e}')
        client.disconnect()
    input('\nPress enter to exit...')

# Read user details
try:
    with open('status.dat', 'rb') as f:
        status = pickle.load(f)
    resume_scraping = input(f'{INPUT}{cy} Resume scraping members from {w}{status[0]}{lg}? [y/n]: {r}')
    if resume_scraping.lower() == 'y':
        scraped_grp = status[0]
        index = int(status[1])
    else:
        os.remove('status.dat')
        scraped_grp = input(f'{INPUT}{cy} Public/Private group url link to scrape members: {r}')
        index = 0
except FileNotFoundError:
    scraped_grp = input(f'{INPUT}{cy} Public/Private group url link to scrape members: {r}')
    index = 0

with open('vars.txt', 'rb') as f:
    while True:
        try:
            accounts.append(pickle.load(f))
        except EOFError:
            break

print(f'{info}{lg} Total accounts: {w}{len(accounts)}')
number_of_accs = int(input(f'{INPUT}{cy} How Many Accounts You Want Use In Adding: {r}'))
print(f'{info}{cy} Choose an option{lg}')
print(f'{cy}[0]{lg} Add members to group')
print(f'{cy}[1]{lg} Send message using all accounts')
print(f'{cy}[2]{lg} Join a group/channel using all accounts')
print(f'{cy}[3]{lg} Leave a group/channel using all accounts')
print(f'{cy}[4]{lg} Report a group/channel using all accounts')
print(f'{cy}[5]{lg} Add hidden members from group using their messages')
choice = int(input(f'{INPUT}{cy} Enter choice: {r}'))

if choice == 0:
    target = input(f'{INPUT}{cy} Enter group url link: {r}')
    print(f'{grey}_'*50)
    status_choice = input(f'{INPUT}{cy} Do you wanna add active members?[y/n]: {r}')
    to_use = accounts[:number_of_accs]

    with open('vars.txt', 'wb') as f:
        for a in accounts:
            pickle.dump(a, f)
        for ab in to_use:
            pickle.dump(ab, f)

    sleep_time = int(input(f'{INPUT}{cy} Enter delay time per request{w}[{lg}0 for None, i suggest enter 30 to add members properly{w}]: {r}'))
    print(f'{info}{lg} Joining group from {w}{number_of_accs} accounts...')
    print(f'{grey}-'*50)
    print(f'{success}{lg} -- Adding members from {w}{len(to_use)}{lg} account(s) --')

    adding_status = 0
    approx_members_count = 0
    for acc in to_use:
        stop = index + 60
        c = TelegramClient(f'sessions/{acc[0]}', 3910389, '86f861352f0ab76a251866059a6adbd6')
        print(f'{plus}{grey} User: {cy}{acc[0]}{lg} -- {cy}Starting session... ')
        c.start(acc[0])
        acc_name = c.get_me().first_name
        try:
            if '/joinchat/' in scraped_grp:
                g_hash = scraped_grp.split('/joinchat/')[1]
                try:
                    c(ImportChatInviteRequest(g_hash))
                    print(f'{plus}{grey} User: {cy}{acc_name}{lg} -- Joined group to scrape')
                except UserAlreadyParticipantError:
                    pass
            else:
                c(JoinChannelRequest(scraped_grp))
                print(f'{plus}{grey} User: {cy}{acc_name}{lg} -- Joined group to scrape')
            scraped_grp_entity = c.get_entity(scraped_grp)
            if choice == 0:
                c(JoinChannelRequest(target))
                print(f'{plus}{grey} User: {cy}{acc_name}{lg} -- Joined group to add')
                target_entity = c.get_entity(target)
                target_details = InputPeerChannel(target_entity.id, target_entity.access_hash)
            else:
                try:
                    grp_hash = target.split('/joinchat/')[1]
                    c(ImportChatInviteRequest(grp_hash))
                    print(f'{plus}{grey} User: {cy}{acc_name}{lg} -- Joined group to add')
                except UserAlreadyParticipantError:
                    pass
                target_entity = c.get_entity(target)
                target_details = target_entity
        except Exception as e:
            print(f'{error}{r} User: {cy}{acc_name}{lg} -- Failed to join group')
            print(f'{error} {r}{e}')
            continue

        print(f'{plus}{grey} User: {cy}{acc_name}{lg} -- {cy}Retrieving entities...')
        c.get_dialogs()
        try:
            members = c.get_participants(scraped_grp_entity, aggressive=False)
        except Exception as e:
            print(f'{error}{r} Couldn\'t scrape members')
            print(f'{error}{r} {e}')
            continue

        approx_members_count = len(members)
        if approx_members_count == 0:
            print(f'{error}{lg} No members to add!')
            continue

        print(f'{info}{lg} Start: {w}{index}')
        adding_status = 0
        peer_flood_status = 0
        for user in members[index:stop]:
            index += 1
            if peer_flood_status == 10:
                print(f'{error}{r} Too many Peer Flood Errors! Closing session...')
                break
            try:
                if choice == 0:
                    c(InviteToChannelRequest(target_details, [user]))
                else:
                    c(AddChatUserRequest(target_details.id, user, 42))
                user_id = user.first_name
                target_title = target_entity.title
                print(f'{plus}{grey} User: {cy}{acc_name}{lg} -- {cy}{user_id} {lg}--> {cy}{target_title}')
                adding_status += 1
                print(f'{info}{grey} User: {cy}{acc_name}{lg} -- Sleep {w}{sleep_time} {lg}second(s)')
                time.sleep(sleep_time)
            except UserPrivacyRestrictedError:
                print(f'{minus}{grey} User: {cy}{acc_name}{lg} -- {r}User Privacy Restricted Error')
                continue
            except PeerFloodError:
                print(f'{error}{grey} User: {cy}{acc_name}{lg} -- {r}Peer Flood Error.')
                peer_flood_status += 1
                continue
            except ChatWriteForbiddenError:
                print(f'{error}{r} Can\'t add to group. Contact group admin to enable members adding')
                if index < approx_members_count:
                    log_status(scraped_grp, index)
                exit_window()
            except UserBannedInChannelError:
                print(f'{error}{grey} User: {cy}{acc_name}{lg} -- {r}Banned from writing in groups')
                break
            except ChatAdminRequiredError:
                print(f'{error}{grey} User: {cy}{acc_name}{lg} -- {r}Chat Admin rights needed to add')
                break
            except UserAlreadyParticipantError:
                print(f'{minus}{grey} User: {cy}{acc_name}{lg} -- {r}User is already a participant')
                continue
            except FloodWaitError as e:
                print(f'{error}{r} {e}')
                break
            except ValueError:
                print(f'{error}{r} Error in Entity')
                continue
            except KeyboardInterrupt:
                print(f'{error}{r} ---- Adding Terminated ----')
                if index < len(members):
                    log_status(scraped_grp, index)
                exit_window()
            except Exception as e:
                print(f'{error} {e}')
                continue

    if adding_status != 0:
        print(f"\n{info}{lg} Adding session ended")
    try:
        if index < approx_members_count:
            log_status(scraped_grp, index)
            exit_window()
    except:
        exit_window()
elif choice == 1:
    send_message_all_accounts()
elif choice == 2:
    join_group_all_accounts()
elif choice == 3:
    leave_group_all_accounts()
elif choice == 4:
    report_group_all_accounts()
elif choice == 5:
    add_hidden_members_from_group()
