import os
import random
import asyncio
import re
import json
from datetime import datetime
from telethon import TelegramClient, events, errors
from telethon.errors import FloodWaitError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest

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
    "fwd_delay_min.txt": "2",
    "fwd_delay_max.txt": "5",
    "fwd_extra_text.txt": "",
    "fwd_extra_position.txt": "after",
    "clone_target.txt": ""
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

@events.register(events.NewMessage(pattern=re.compile(r'^/help$', re.IGNORECASE)))
async def help_command(event):
    if not await check_owner(event): return
    await event.reply("""**Help List**

**Setup:**
/chatid - Get current chat/group ID
/setgp <id> - Set TARGET chat ID

**Forward Spam:**
/setfwd <message_link> - Set SOURCE
/setfwd_delay <min> <max> - Random delay
/setfwd_text <text> - Extra text
/setfwd_pos before/after - Position
/fwdspam_on - Start
/fwdspam_off - Stop
/showfwd - Show config

**Text Spam:**
/cap <text> - Global caption
/speed <n> - Delay seconds
/spam_on - Start
/spam_off - Stop

**Clone:**
/clone @username - Clone target
/resetme - Reset profile

**Auto Join:**
/join <link> - Join group/channel by link

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
        await event.reply(f"❌ Failed to parse link: {e}")

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
    await event.reply(f"✅ Extra text set")

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
    
    if not ForwardSpammer[0]:
        ForwardSpammer[0] = True
        asyncio.create_task(forward_spam_function())
        await event.reply(f"🔥 **Forward spam STARTED!**")
    else:
        await event.reply("⚠️ Already running")

@events.register(events.NewMessage(pattern=re.compile(r'^/fwdspam_off$', re.IGNORECASE)))
async def forward_spam_off(event):
    if not await check_owner(event): return
    if ForwardSpammer[0]:
        ForwardSpammer[0] = False
        await event.reply("🛑 **Forward spam STOPPED**")
    else:
        await event.reply("⚠️ Not running")

@events.register(events.NewMessage(pattern=re.compile(r'^/showfwd$', re.IGNORECASE)))
async def show_forward_config(event):
    if not await check_owner(event): return
    with open(os.path.join(BOT_DIR, 'targetid.txt'), 'r') as f:
        target = f.read().strip()
    with open(os.path.join(BOT_DIR, 'fwd_source_channel.txt'), 'r', encoding="utf-8") as f:
        source = f.read().strip()
    with open(os.path.join(BOT_DIR, 'fwd_source_msg_id.txt'), 'r') as f:
        msg_id = f.read().strip()
    
    status = "🛑 STOPPED" if not ForwardSpammer[0] else "🔥 RUNNING"
    
    await event.reply(f"""**📋 Forward Config - {status}**
• TARGET: `{target}`
• SOURCE: `{source}/{msg_id}`""")

@events.register(events.NewMessage(pattern=re.compile(r'^/cap (.+)$', re.IGNORECASE)))
async def set_caption(event):
    if not await check_owner(event): return
    cap = event.pattern_match.group(1).strip()
    with open(os.path.join(BOT_DIR, 'Caption.txt'), 'w', encoding="utf-8") as f:
        f.write(cap)
    await event.reply(f"✅ Caption set")

@events.register(events.NewMessage(pattern=re.compile(r'^/speed (.+)$', re.IGNORECASE)))
async def set_speed(event):
    if not await check_owner(event): return
    val = event.pattern_match.group(1).strip()
    if val.isdigit() and int(val) > 0:
        with open(os.path.join(BOT_DIR, 'time.txt'), 'w') as f:
            f.write(val)
        await event.reply(f"⏱ Speed: {val} seconds")

@events.register(events.NewMessage(pattern=re.compile(r'^/chatid$', re.IGNORECASE)))
async def get_chat_id(event):
    if not await check_owner(event): return
    await event.reply(f"📌 Chat ID: `{event.chat_id}`")

@events.register(events.NewMessage(pattern=re.compile(r'^/setgp (.+)$', re.IGNORECASE)))
async def set_group(event):
    if not await check_owner(event): return
    group_id = event.pattern_match.group(1).strip()
    try:
        int(group_id)
        with open(os.path.join(BOT_DIR, 'targetid.txt'), 'w') as f:
            f.write(group_id)
        await event.reply(f"✅ Target set to: `{group_id}`")
    except:
        await event.reply("❌ Invalid ID")

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
    await event.reply("ALIVE")

# ========== CLONE ==========
@events.register(events.NewMessage(pattern=re.compile(r'^/clone (.+)$', re.IGNORECASE)))
async def clone_user(event):
    if not await check_owner(event): return
    
    target = event.pattern_match.group(1).strip()
    
    try:
        await event.reply(f"🔄 Cloning @{target} ...")
        
        entity = await client.get_entity(target)
        
        # Get bio safely
        target_bio = ""
        try:
            full = await client(GetFullUserRequest(entity.id))
            if hasattr(full, 'about') and full.about:
                target_bio = full.about
        except:
            pass
        
        # Save original
        me = await client.get_me()
        my_bio = ""
        try:
            me_full = await client(GetFullUserRequest(me.id))
            if hasattr(me_full, 'about') and me_full.about:
                my_bio = me_full.about
        except:
            pass
        
        original_data = {
            "first": me.first_name or "",
            "last": me.last_name or "",
            "about": my_bio,
            "username": me.username or ""
        }
        with open(os.path.join(BOT_DIR, 'original_profile.json'), 'w', encoding="utf-8") as f:
            json.dump(original_data, f)
        
        # Clone name
        first_name = entity.first_name or "Clone"
        last_name = entity.last_name or ""
        await client(UpdateProfileRequest(first_name=first_name, last_name=last_name))
        
        # Clone bio
        bio_cloned = False
        if target_bio:
            try:
                await client(UpdateProfileRequest(about=target_bio))
                bio_cloned = True
            except:
                pass
        
        # Clone username
        username_cloned = False
        if entity.username:
            try:
                await client(UpdateUsernameRequest(entity.username))
                username_cloned = True
            except:
                pass
        
        # Clone photo
        photo_cloned = False
        if entity.photo:
            try:
                photo_path = await client.download_profile_photo(entity)
                if photo_path:
                    file = await client.upload_file(photo_path)
                    await client(UploadProfilePhotoRequest(file=file))
                    os.remove(photo_path)
                    photo_cloned = True
            except:
                pass
        
        await event.reply(f"""✅ **CLONE COMPLETE**
━━━━━━━━━━━━━━━━━
👤 Name: {first_name} {last_name}
📝 Bio: {'✓' if bio_cloned else '✗'}
🖼️ Photo: {'✓' if photo_cloned else '✗'}
🏷️ Username: {'✓' if username_cloned else '✗'}
━━━━━━━━━━━━━━━━━
/resetme to restore""")
        
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

@events.register(events.NewMessage(pattern=re.compile(r'^/resetme$', re.IGNORECASE)))
async def reset_profile(event):
    if not await check_owner(event): return
    
    try:
        json_path = os.path.join(BOT_DIR, 'original_profile.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding="utf-8") as f:
                original = json.load(f)
            
            first = original.get("first", "Reset")
            last = original.get("last", "")
            about = original.get("about", "")
            username = original.get("username", "")
            
            await client(UpdateProfileRequest(first_name=first, last_name=last, about=about))
            
            if username:
                try:
                    await client(UpdateUsernameRequest(username))
                except:
                    pass
            
            await event.reply(f"✅ Restored: {first} {last}")
        else:
            await client(UpdateProfileRequest(first_name="Reset", last_name="", about=""))
            await event.reply("✅ Profile reset")
            
    except Exception as e:
        await event.reply(f"❌ Reset failed: {e}")

# ========== AUTO JOIN ==========
@events.register(events.NewMessage(pattern=re.compile(r'^/join (.+)$', re.IGNORECASE)))
async def auto_join(event):
    if not await check_owner(event): return
    
    link = event.pattern_match.group(1).strip()
    
    try:
        await event.reply(f"🔄 Joining: {link} ...")
        
        # استخراج invite hash از لینک
        if "t.me/+" in link:
            invite_hash = link.split("t.me/+")[1].split("/")[0]
            await client(ImportChatInviteRequest(invite_hash))
        elif "t.me/joinchat/" in link:
            invite_hash = link.split("t.me/joinchat/")[1].split("/")[0]
            await client(ImportChatInviteRequest(invite_hash))
        elif "t.me/" in link:
            username = link.split("t.me/")[1].split("/")[0]
            await client(JoinChannelRequest(username))
        else:
            # اگه خود لینک کامل نبود
            await client(ImportChatInviteRequest(link))
        
        await event.reply(f"✅ **JOINED SUCCESSFULLY!**\n📢 Link: {link}")
        
    except Exception as e:
        await event.reply(f"❌ Join failed: {str(e)}")

async def main():
    global client
    client = TelegramClient('userbot_session', API_ID, API_HASH)

    print("🔐 Connecting...")
    await client.start(phone=PHONE_NUMBER)

    me = await client.get_me()
    print(f"✅ Logged in as: @{me.username}")

    client.add_event_handler(help_command)
    client.add_event_handler(set_caption)
    client.add_event_handler(set_speed)
    client.add_event_handler(get_chat_id)
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
    client.add_event_handler(clone_user)
    client.add_event_handler(reset_profile)
    client.add_event_handler(auto_join)

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
