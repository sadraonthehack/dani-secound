import os
import random
import asyncio
import re
from telethon import TelegramClient, events, errors
from telethon.errors import FloodWaitError

API_ID = 31255158
API_HASH = "517d1e9d58e3e9c60abe3e6ecd59b755"
PHONE_NUMBER = "+989213907638"

OWNERS = {"usernames": ["DevilWillCryBitch", "AliiSoeched" , "Babariapsycho"]}

BOT_DIR = "downloads_bot1"
if not os.path.exists(BOT_DIR):
    os.mkdir(BOT_DIR)

files_defaults = {
    "Kheshab.txt": "ONLINE",
    "targetid.txt": "1",
    "Caption.txt": "",
    "time.txt": "2",
    "fwd_source_channel.txt": "",
    "fwd_source_msg_id.txt": "0",
    "fwd_active.txt": "False",
    "fwd_delay_min.txt": "2",
    "fwd_delay_max.txt": "5",
    "fwd_extra_text.txt": "",
    "fwd_extra_position.txt": "after"
}

for filename, content in files_defaults.items():
    path = os.path.join(BOT_DIR, filename)
    if not os.path.exists(path):
        with open(path, 'w', encoding="utf-8") as f:
            f.write(content)

Spammer = [False]
ForwardSpammer = [False]
client = None

async def spam_function():
    global client
    print("Text spam thread started")
    while Spammer[0]:
        try:
            with open(os.path.join(BOT_DIR, 'targetid.txt'), 'r') as f:
                target_id = int(f.read().strip())
            with open(os.path.join(BOT_DIR, 'Kheshab.txt'), 'r', encoding="utf-8") as f:
                messages = f.readlines()
            with open(os.path.join(BOT_DIR, 'Caption.txt'), 'r', encoding="utf-8") as f:
                caption = f.read().strip()
            with open(os.path.join(BOT_DIR, 'time.txt'), 'r') as f:
                delay = int(f.read().strip())
        except Exception as e:
            print(f"Config error: {e}")
            delay = 2
            messages = []

        if messages and target_id != 1:
            try:
                text = random.choice(messages).strip()
                if text:
                    print(f"📤 Sending: {text[:30]}...")
                    msg = f"{text}\n\n{caption}" if caption else text
                    await client.send_message(target_id, msg)
            except Exception as e:
                print(f"Send error: {e}")
        await asyncio.sleep(delay)
    print("Text spam stopped")

async def forward_spam_function():
    global client
    print("Forward spam thread started")
    while ForwardSpammer[0]:
        try:
            with open(os.path.join(BOT_DIR, 'targetid.txt'), 'r') as f:
                target_id = int(f.read().strip())
            with open(os.path.join(BOT_DIR, 'fwd_source_channel.txt'), 'r', encoding="utf-8") as f:
                source_channel = f.read().strip()
            with open(os.path.join(BOT_DIR, 'fwd_source_msg_id.txt'), 'r') as f:
                source_msg_id = int(f.read().strip())
            with open(os.path.join(BOT_DIR, 'fwd_delay_min.txt'), 'r') as f:
                delay_min = float(f.read().strip())
            with open(os.path.join(BOT_DIR, 'fwd_delay_max.txt'), 'r') as f:
                delay_max = float(f.read().strip())
            with open(os.path.join(BOT_DIR, 'fwd_extra_text.txt'), 'r', encoding="utf-8") as f:
                extra_text = f.read().strip()
            with open(os.path.join(BOT_DIR, 'fwd_extra_position.txt'), 'r', encoding="utf-8") as f:
                extra_pos = f.read().strip()
        except Exception as e:
            print(f"Config read error: {e}")
            await asyncio.sleep(5)
            continue

        if target_id == 1:
            print("⚠️ No target set. Use /setgp <chatid>")
            ForwardSpammer[0] = False
            break
            
        if not source_channel or source_msg_id == 0:
            print("⚠️ No source set. Use /setfwd <message_link>")
            ForwardSpammer[0] = False
            break

        try:
            source_message = await client.get_messages(source_channel, ids=source_msg_id)
            if not source_message:
                print(f"❌ Message {source_msg_id} not found in {source_channel}")
                ForwardSpammer[0] = False
                break

            await client.forward_messages(target_id, source_message)

            if extra_text:
                if extra_pos == "before":
                    await client.send_message(target_id, f"{extra_text}\n\n")
                else:
                    await client.send_message(target_id, f"\n\n{extra_text}")

            print(f"📨 Forwarded to {target_id}")

            delay = random.uniform(delay_min, delay_max)
            await asyncio.sleep(delay)

        except FloodWaitError as e:
            print(f"⏳ Flood wait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Forward error: {e}")
            await asyncio.sleep(5)

    print("Forward spam stopped")

async def check_owner(event):
    sender = await event.get_sender()
    if sender and sender.username and sender.username in OWNERS["usernames"]:
        return True
    return False

# UPDATED HELP COMMAND WITH YOUR CHANNEL PROMO
@events.register(events.NewMessage(pattern=re.compile(r'^/help$', re.IGNORECASE)))
async def help_command(event):
    if not await check_owner(event): return
    await event.reply("""*help list**

**Setup (One Time):**
/chatid - Get current chat/group ID
/setgp <id> - Set TARGET chat ID (where messages go)

**Forward Spam**
/setfwd <message_link> - Set SOURCE (any message link from Telegram)
/setfwd_delay <min> <max> - Random delay (seconds)
/setfwd_text <text> - Extra text before/after forward
/setfwd_pos before/after - Position of extra text
/fwdspam_on - Start forwarding to target
/fwdspam_off - Stop
/showfwd - Show current config

**Text Spam **
/cap <text> - Global caption
/speed <n> - Delay seconds
/spam_on - Start text spam
/spam_off - Stop

/ping - Bot status



━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Coded by BrianMoser - MERGED BY JUST LISA**


**OWNER CHANNEL** → https://t.me/nahuhnothinghere/4
""")

@events.register(events.NewMessage(pattern=re.compile(r'^/setfwd (https?://t\.me/[^\s]+)$', re.IGNORECASE)))
async def set_forward_from_link(event):
    if not await check_owner(event): return
    link = event.pattern_match.group(1).strip()
    
    try:
        parts = link.replace("https://t.me/", "").split("/")
        
        if parts[0] == "c":
            channel_id = int("-100" + parts[1])
            msg_id = int(parts[2])
            channel_username = str(channel_id)
        else:
            channel_username = parts[0]
            msg_id = int(parts[1])
            
        with open(os.path.join(BOT_DIR, 'fwd_source_channel.txt'), 'w', encoding="utf-8") as f:
            f.write(channel_username)
        with open(os.path.join(BOT_DIR, 'fwd_source_msg_id.txt'), 'w') as f:
            f.write(str(msg_id))
            
        await event.reply(f"✅ Source set!\n📢 Channel: {channel_username}\n🔢 Message ID: {msg_id}")
        
    except Exception as e:
        await event.reply(f"❌ Failed to parse link: {e}\nUse format: https://t.me/username/message_id")

@events.register(events.NewMessage(pattern=re.compile(r'^/setfwd_delay (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)$', re.IGNORECASE)))
async def set_forward_delay(event):
    if not await check_owner(event): return
    min_d = float(event.pattern_match.group(1))
    max_d = float(event.pattern_match.group(2))
    if min_d < 0.5: min_d = 0.5
    if max_d < min_d: max_d = min_d + 1
    
    with open(os.path.join(BOT_DIR, 'fwd_delay_min.txt'), 'w') as f:
        f.write(str(min_d))
    with open(os.path.join(BOT_DIR, 'fwd_delay_max.txt'), 'w') as f:
        f.write(str(max_d))
    
    await event.reply(f"✅ Delay: {min_d}-{max_d} seconds")

@events.register(events.NewMessage(pattern=re.compile(r'^/setfwd_text (.+)$', re.IGNORECASE)))
async def set_forward_text(event):
    if not await check_owner(event): return
    text = event.pattern_match.group(1).strip()
    with open(os.path.join(BOT_DIR, 'fwd_extra_text.txt'), 'w', encoding="utf-8") as f:
        f.write(text)
    await event.reply(f"✅ Extra text: {text[:50]}{'...' if len(text) > 50 else ''}")

@events.register(events.NewMessage(pattern=re.compile(r'^/setfwd_pos (before|after)$', re.IGNORECASE)))
async def set_forward_pos(event):
    if not await check_owner(event): return
    pos = event.pattern_match.group(1).lower()
    with open(os.path.join(BOT_DIR, 'fwd_extra_position.txt'), 'w', encoding="utf-8") as f:
        f.write(pos)
    await event.reply(f"✅ Position: {pos}")

@events.register(events.NewMessage(pattern=re.compile(r'^/fwdspam_on$', re.IGNORECASE)))
async def forward_spam_on(event):
    if not await check_owner(event): return
    
    with open(os.path.join(BOT_DIR, 'targetid.txt'), 'r') as f:
        target = int(f.read().strip())
    if target == 1:
        await event.reply("❌ Set target first: /setgp <chatid>")
        return
    
    with open(os.path.join(BOT_DIR, 'fwd_source_channel.txt'), 'r', encoding="utf-8") as f:
        source = f.read().strip()
    with open(os.path.join(BOT_DIR, 'fwd_source_msg_id.txt'), 'r') as f:
        msg_id = f.read().strip()
    
    if not source or msg_id == "0":
        await event.reply("❌ Set source first: /setfwd <message_link>")
        return
    
    if not ForwardSpammer[0]:
        ForwardSpammer[0] = True
        asyncio.create_task(forward_spam_function())
        await event.reply(f"🔥 **Forward spam STARTED!**\n📥 Target: {target}\n📤 Source: {source}/{msg_id}")
    else:
        await event.reply("⚠️ Already running")

@events.register(events.NewMessage(pattern=re.compile(r'^/fwdspam_off$', re.IGNORECASE)))
async def forward_spam_off(event):
    if not await check_owner(event): return
    if ForwardSpammer[0]:
        ForwardSpammer[0] = False
        await event.reply(" **Forward spam STOPPED**")
    else:
        await event.reply(" Not running")

@events.register(events.NewMessage(pattern=re.compile(r'^/showfwd$', re.IGNORECASE)))
async def show_forward_config(event):
    if not await check_owner(event): return
    with open(os.path.join(BOT_DIR, 'targetid.txt'), 'r') as f:
        target = f.read().strip()
    with open(os.path.join(BOT_DIR, 'fwd_source_channel.txt'), 'r', encoding="utf-8") as f:
        source = f.read().strip()
    with open(os.path.join(BOT_DIR, 'fwd_source_msg_id.txt'), 'r') as f:
        msg_id = f.read().strip()
    with open(os.path.join(BOT_DIR, 'fwd_delay_min.txt'), 'r') as f:
        min_d = f.read().strip()
    with open(os.path.join(BOT_DIR, 'fwd_delay_max.txt'), 'r') as f:
        max_d = f.read().strip()
    with open(os.path.join(BOT_DIR, 'fwd_extra_text.txt'), 'r', encoding="utf-8") as f:
        extra = f.read().strip()
    with open(os.path.join(BOT_DIR, 'fwd_extra_position.txt'), 'r', encoding="utf-8") as f:
        pos = f.read().strip()
    
    status = " STOPPED" if not ForwardSpammer[0] else " RUNNING"
    
    await event.reply(f"""**📋 Forward Config - {status}**
• TARGET (chatid): `{target}`
• SOURCE: `{source}/{msg_id}`
• DELAY: {min_d}-{max_d}s
• EXTRA TEXT: {extra[:50] if extra else '(none)'}
• POSITION: {pos}
    
Use /setgp to change target
Use /setfwd with new link to change source""")

@events.register(events.NewMessage(pattern=re.compile(r'^/cap (.+)$', re.IGNORECASE)))
async def set_caption(event):
    if not await check_owner(event): return
    cap = event.pattern_match.group(1).strip()
    with open(os.path.join(BOT_DIR, 'Caption.txt'), 'w', encoding="utf-8") as f:
        f.write(cap)
    await event.reply(f" Caption: {cap}")

@events.register(events.NewMessage(pattern=re.compile(r'^/cap_show$', re.IGNORECASE)))
async def get_caption(event):
    if not await check_owner(event): return
    with open(os.path.join(BOT_DIR, 'Caption.txt'), 'r', encoding="utf-8") as f:
        cap = f.read()
    await event.reply(f"📝 Caption: {cap if cap else '(empty)'}")

@events.register(events.NewMessage(pattern=re.compile(r'^/speed (.+)$', re.IGNORECASE)))
async def set_speed(event):
    if not await check_owner(event): return
    val = event.pattern_match.group(1).strip()
    if val.isdigit() and int(val) > 0:
        with open(os.path.join(BOT_DIR, 'time.txt'), 'w') as f:
            f.write(val)
        await event.reply(f"⏱ Speed: {val} seconds")
    else:
        await event.reply(" Invalid number")

@events.register(events.NewMessage(pattern=re.compile(r'^/speed_show$', re.IGNORECASE)))
async def get_speed(event):
    if not await check_owner(event): return
    with open(os.path.join(BOT_DIR, 'time.txt'), 'r') as f:
        val = f.read()
    await event.reply(f"⏱ Speed: {val} seconds")

@events.register(events.NewMessage(pattern=re.compile(r'^/chatid$', re.IGNORECASE)))
async def get_chat_id(event):
    if not await check_owner(event): return
    await event.reply(f" Chat ID: `{event.chat_id}`")

@events.register(events.NewMessage(pattern=re.compile(r'^/userid$', re.IGNORECASE)))
async def get_user_id(event):
    if not await check_owner(event): return
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        await event.reply(f" User ID: `{reply_msg.sender_id}`")
    else:
        await event.reply(" Reply to a message")

@events.register(events.NewMessage(pattern=re.compile(r'^/setgp (.+)$', re.IGNORECASE)))
async def set_group(event):
    if not await check_owner(event): return
    group_id = event.pattern_match.group(1).strip()
    try:
        int(group_id)
        with open(os.path.join(BOT_DIR, 'targetid.txt'), 'w') as f:
            f.write(group_id)
        await event.reply(f" TARGET chat ID set to: `{group_id}`")
    except:
        await event.reply(" Invalid ID (numbers only, get with /chatid)")

@events.register(events.NewMessage(pattern=re.compile(r'^/spam_on$', re.IGNORECASE)))
async def spam_on(event):
    if not await check_owner(event): return
    if not Spammer[0]:
        with open(os.path.join(BOT_DIR, 'targetid.txt'), 'r') as f:
            if int(f.read().strip()) == 1:
                await event.reply("⚠️ Set target first: /setgp <id>")
                return
        Spammer[0] = True
        asyncio.create_task(spam_function())
        await event.reply("🔥 **Text Spam STARTED!**")
    else:
        await event.reply("⚠️ Already spamming")

@events.register(events.NewMessage(pattern=re.compile(r'^/spam_off$', re.IGNORECASE)))
async def spam_off(event):
    if not await check_owner(event): return
    if Spammer[0]:
        Spammer[0] = False
        await event.reply("🛑 **Text Spam STOPPED**")
    else:
        await event.reply("⚠️ Not spamming")

@events.register(events.NewMessage(pattern=re.compile(r'^/ping$', re.IGNORECASE)))
async def ping(event):
    if not await check_owner(event): return
    await event.reply(" Bot is alive.")

async def main():
    global client
    client = TelegramClient('userbot_session', API_ID, API_HASH)

    print("🔐 Connecting...")
    await client.start(phone=PHONE_NUMBER)

    me = await client.get_me()
    print(f"✅ Logged in as: @{me.username}")

    client.add_event_handler(help_command)
    client.add_event_handler(set_caption)
    client.add_event_handler(get_caption)
    client.add_event_handler(set_speed)
    client.add_event_handler(get_speed)
    client.add_event_handler(get_chat_id)
    client.add_event_handler(get_user_id)
    client.add_event_handler(set_group)
    client.add_event_handler(spam_on)
    client.add_event_handler(spam_off)
    client.add_event_handler(ping)
    client.add_event_handler(set_forward_from_link)
    client.add_event_handler(set_forward_delay)
    client.add_event_handler(set_forward_text)
    client.add_event_handler(set_forward_pos)
    client.add_event_handler(forward_spam_on)
    client.add_event_handler(forward_spam_off)
    client.add_event_handler(show_forward_config)

    print("="*40)
    print("🔥 Bot running - Just-Lisa edition")
    print("Commands: /help")
    print("="*40)

    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
