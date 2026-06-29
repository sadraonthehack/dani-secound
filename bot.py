import asyncio
import random
import time
import os
from typing import Set, List, Optional

from telethon import TelegramClient, events
from telethon.tl.types import Message, User
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import InputPhoto


API_ID = 27029926
API_HASH = "6963d3bf5f8a776f5139d71cfc707abc"
PHONE_NUMBER = "+989213907638"

SESSION_NAME = "user_session"


ADMIN_IDS: Set[int] = {7202211827}  
FOSHLIST: List[str] = []
SPAM_TARGET: Optional[int] = None
SPAM_TEXT: str = "ONLINE"
SPAM_ACTIVE: bool = False
SPAM_TASK: Optional[asyncio.Task] = None
SPAM_SPEED: float = 1.0  
ENEMY_TARGET: Optional[int] = None
ENEMY_ACTIVE: bool = False
REPLY_TO_ENEMY: bool = True
ORIGINAL_NAME: str = ""
ORIGINAL_PHOTO: Optional[InputPhoto] = None

client: Optional[TelegramClient] = None


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def spam_loop():
    """Background task that sends spam messages with custom speed."""
    global SPAM_ACTIVE, SPAM_TARGET, SPAM_TEXT, SPAM_SPEED, client
    while SPAM_ACTIVE and SPAM_TARGET and client:
        try:
            await client.send_message(SPAM_TARGET, SPAM_TEXT)
            print(f"[SPAM] 📨 Sent to {SPAM_TARGET} | Speed: {SPAM_SPEED}s")
        except Exception as e:
            print(f"[ERROR] Spam failed: {e}")
        await asyncio.sleep(SPAM_SPEED)  

async def send_loading_animation(event):
    """Send a loading animation with progress bar effect."""
    loading_steps = [
        " [          ] 0%",
        " [█         ] 10%",
        " [██        ] 20%",
        " [███       ] 30%",
        " [████      ] 40%",
        " [█████     ] 50%",
        " [██████    ] 60%",
        " [███████   ] 70%",
        " [████████  ] 80%",
        " [█████████ ] 90%",
        " [██████████] 100%",
        " LOADING COMPLETE"
    ]
    loading_msg = await event.reply(" **Loading...**\n" + loading_steps[0])
    for i in range(1, len(loading_steps)):
        await asyncio.sleep(0.3)
        try:
            await loading_msg.edit(f" **Loading...**\n{loading_steps[i]}")
        except:
            break
    await asyncio.sleep(0.3)
    try:
        await loading_msg.delete()
    except:
        pass

async def handle_all_messages(event):
    global ADMIN_IDS, FOSHLIST, SPAM_TARGET, SPAM_TEXT, SPAM_ACTIVE, SPAM_TASK, SPAM_SPEED
    global ENEMY_TARGET, ENEMY_ACTIVE, REPLY_TO_ENEMY, ORIGINAL_NAME, ORIGINAL_PHOTO, client
    
    if not event.message or not event.message.text:
        return
    
    user_id = event.sender_id
    text = event.message.text.strip().lower() if event.message.text else ""
    
    me = await client.get_me()
    if user_id == me.id:
        return
    
    
    if ENEMY_ACTIVE and REPLY_TO_ENEMY and FOSHLIST:
        if user_id == ENEMY_TARGET:
            reply_text = random.choice(FOSHLIST)
            await asyncio.sleep(0.5)
            try:
                await event.reply(reply_text)
                print(f"[BOT]  Enemy reply sent to {user_id}")
            except Exception as e:
                print(f"[ERROR] Enemy reply failed: {e}")
            return
    
    
    if user_id not in ADMIN_IDS:
        return  
    
    
    if event.is_private:
        location = "PRIVATE"
    elif event.is_group:
        location = "GROUP"
    elif event.is_channel:
        location = "CHANNEL"
    else:
        location = "UNKNOWN"
    
    print(f"[BOT]  Admin {user_id} in {location}: {text[:50]}")
    
    
    if text == "help" or text == "راهنما":
        await send_loading_animation(event)
        help_text = """
• `spam` – Start spamming the set chat.
• • • • • • • • • • • • • • • • • • • • • • • •
• `spamoff` – Stop all spam activities.
• • • • • • • • • • • • • • • • • • • • • • • •
• `setfosh <text>` – Change spam message.
• • • • • • • • • • • • • • • • • • • • • • • •
• `speed <1-60>` – Adjust spam speed (in seconds).
• • • • • • • • • • • • • • • • • • • • • • • •
• `id` – get chatid
• • • • • • • • • • • • • • • • • • • • • • • •
• `setid <chat_id>` – Set target chat ID.
• • • • • • • • • • • • • • • • • • • • • • • •
• `addfosh` – Reply to a message to save it.
• • • • • • • • • • • • • • • • • • • • • • • •
• `listfosh` – Show all saved fosh items.
• • • • • • • • • • • • • • • • • • • • • • • •
• `removefosh <index>` – Delete a fosh by index.
• • • • • • • • • • • • • • • • • • • • • • • •
• `setenemy` – Reply to mark user as enemy.
• • • • • • • • • • • • • • • • • • • • • • • •
• `enemyoff` – Disable enemy mode.
• • • • • • • • • • • • • • • • • • • • • • • •

• `clone @username` – Clone target's profile pic + name.
• • • • • • • • • • • • • • • • • • • • • • • •
• `cloneback` – Restore your original profile
• • • • • • • • • • • • • • • • • • • • • • • •
• `ping` – PING A BOT.
• • • • • • • • • • • • • • • • • • • • • • • •
• `status` – Show current configuration.
• • • • • • • • • • • • • • • • • • • • • • • •
• `addadmin <user_id>` – Add admin.
• • • • • • • • • • • • • • • • • • • • • • • •
• `kiladmin <user_id>` – Remove admin.
| https://t.me/fjsicksv/6 | JUST EDIT YOU KNOW  
"""
        await event.reply(help_text)
        return
    
    
    if text.startswith("speed "):
        try:
            new_speed = float(text[6:].strip())
            if 1 <= new_speed <= 60:
                SPAM_SPEED = new_speed
                print(f"[BOT]  Spam speed changed to {SPAM_SPEED}s (silent)")
        except ValueError:
            pass
        return  
    
    
    if text == "spam":
        if not SPAM_TARGET:
            await event.reply(" No target chat set. Use `setid` first.")
            return
        if SPAM_ACTIVE:
            await event.reply(" Spam is already running. Use `spamoff` to stop.")
            return
        
        SPAM_ACTIVE = True
        await event.reply(
            f"spam run!**\n"
            f"Target: `{SPAM_TARGET}`\n"
            f"Text: `{SPAM_TEXT}`\n"
            f"Speed: `{SPAM_SPEED} seconds`\n"
        )
        
        if SPAM_TASK and not SPAM_TASK.done():
            SPAM_TASK.cancel()
        SPAM_TASK = asyncio.create_task(spam_loop())
        return
    
    if text == "spamoff":
        if SPAM_ACTIVE:
            SPAM_ACTIVE = False
            if SPAM_TASK and not SPAM_TASK.done():
                SPAM_TASK.cancel()
            await event.reply("SPAM STOP ")
        else:
            await event.reply("NOT ACTIVE")
        return
    
    if text.startswith("setfosh "):
        SPAM_TEXT = text[8:].strip()
        await event.reply(f" new txt :\n`{SPAM_TEXT}`")
        return
    
    if text == "id":
        chat_id = event.chat_id
        chat_type = "Private" if event.is_private else "Group" if event.is_group else "Channel"
        await event.reply(f" ID `{chat_id}`\n **Type:** {chat_type}")
        return
    
    if text.startswith("setid "):
        try:
            SPAM_TARGET = int(text[6:].strip())
            await event.reply(f"TG SET `{SPAM_TARGET}`")
        except ValueError:
            await event.reply(" WRONG CHATID ")
        return
    
    
    if text == "addfosh":
        if not event.is_reply:
            await event.reply(" Reply fosh and after type addfosh")
            return
        
        replied_msg = await event.get_reply_message()
        if not replied_msg or not replied_msg.text:
            await event.reply(" The replied message has no text.")
            return
        
        FOSHLIST.append(replied_msg.text)
        await event.reply(
            f"fosh added** (Index #{len(FOSHLIST)-1})\n"
            f"Preview: `{replied_msg.text[:50]}...`"
        )
        return
    
    if text == "listfosh":
        if not FOSHLIST:
            await event.reply(" Foshlist is empty. Use `addfosh` to fill it.")
            return
        lines = []
        for i, item in enumerate(FOSHLIST):
            snippet = item.replace("\n", " ")[:60]
            lines.append(f"`{i}`: {snippet}...")
        msg = " **FOSHLIST** (index to use with `removefosh`):\n" + "\n".join(lines[:20])
        if len(lines) > 20:
            msg += f"\n... and {len(lines)-20} more."
        await event.reply(msg)
        return
    
    if text.startswith("removefosh "):
        try:
            idx = int(text[11:].strip())
            if idx < 0 or idx >= len(FOSHLIST):
                await event.reply(" Index out of range.")
                return
            removed = FOSHLIST.pop(idx)
            await event.reply(
                f" Removed fosh {idx}:\n`{removed[:50]}...`"
            )
        except ValueError:
            await event.reply(" Invalid index. Must be a number.")
        return
    
    
    if text == "setenemy":
        if not event.is_reply:
            await event.reply("reply dojman ")
            return
        
        replied_msg = await event.get_reply_message()
        if not replied_msg or not replied_msg.sender_id:
            await event.reply(" Could not identify the user")
            return
        
        target_user = await client.get_entity(replied_msg.sender_id)
        ENEMY_TARGET = target_user.id
        ENEMY_ACTIVE = True
        await event.reply(
            f" **mother fuck:** @{target_user.username or target_user.first_name or 'Unknown'}\n"
            f"ID: `{ENEMY_TARGET}`\n"
        )
        return
    
    if text == "enemyoff":
        if ENEMY_ACTIVE:
            ENEMY_ACTIVE = False
            await event.reply(" Enemy mode deactivated.")
        else:
            await event.reply("ℹ Enemy mode is already off.")
        return
    
    if text.startswith("setreply "):
        mode = text[9:].strip().lower()
        if mode not in ["on", "off"]:
            await event.reply(" Usage: `setreply on` or `setreply off`")
            return
        REPLY_TO_ENEMY = mode == "on"
        await event.reply(f" Auto-reply set to: {REPLY_TO_ENEMY}")
        return
    
    if text.startswith("clone "):
        target_identifier = text[6:].strip()
        if target_identifier.startswith("@"):
            target_identifier = target_identifier[1:]
        
        await event.reply(f"🔍 Searching for user: `{target_identifier}`...")
        
        try:
            try:
                target_user = await client.get_entity(target_identifier)
            except:
                if target_identifier.isdigit():
                    try:
                        target_user = await client.get_entity(int(target_identifier))
                    except:
                        target_user = None
                else:
                    target_user = None
            
            if not target_user and event.is_reply:
                replied_msg = await event.get_reply_message()
                if replied_msg and replied_msg.sender_id:
                    target_user = await client.get_entity(replied_msg.sender_id)
            
            if not target_user:
                await event.reply(" Could not find user. Make sure they exist or use their ID.")
                return
            
            me = await client.get_me()
            if not ORIGINAL_NAME:
                ORIGINAL_NAME = me.first_name or ""
            
            if not ORIGINAL_PHOTO:
                try:
                    photos = await client.get_profile_photos(me, limit=1)
                    if photos:
                        ORIGINAL_PHOTO = photos[0]
                except:
                    pass
            
            await event.reply(f"🎭 Cloning `{target_user.first_name or 'Unknown'}`...")
            
            try:
                photos = await client.get_profile_photos(target_user, limit=1)
                
                if photos:
                    photo = photos[0]
                    photo_path = await client.download_media(photo, file="temp_profile.jpg")
                    
                    if photo_path:
                        await client(UploadProfilePhotoRequest(
                            file=await client.upload_file(photo_path)
                        ))
                        await event.reply("✅ **Profile picture cloned successfully!**")
                        try:
                            os.remove(photo_path)
                        except:
                            pass
                else:
                    await event.reply("ℹ️ Target user has no profile picture. Skipping photo clone.")
            except Exception as e:
                await event.reply(f"❌ Failed to set profile picture: `{str(e)[:100]}`")
            
            new_first_name = target_user.first_name or ""
            new_last_name = target_user.last_name or ""
            
            try:
                await client(UpdateProfileRequest(
                    first_name=new_first_name,
                    last_name=new_last_name
                ))
                
                await event.reply(
                    f" **Name cloned successfully**\n"
                    f"New name: `{new_first_name} {new_last_name}`".strip()
                )
            except Exception as e:
                await event.reply(f" Failed to set name `{str(e)[:100]}`")
            
            await event.reply(
                f"🎭 **CLONE COMPLETE!**\n"
                f"Now impersonating: `{target_user.first_name or 'Unknown'}`\n"
                f"ID: `{target_user.id}`"
            )
            
        except Exception as e:
            await event.reply(f" Clone failed `{str(e)[:200]}`")
        return
    
    if text == "cloneback":
        try:
            photos = await client.get_profile_photos(await client.get_me(), limit=1)
            if photos:
                await client(DeletePhotosRequest(id=[photos[0]]))
            
            if ORIGINAL_PHOTO:
                try:
                    photo_path = await client.download_media(ORIGINAL_PHOTO, file="orig_profile.jpg")
                    if photo_path:
                        await client(UploadProfilePhotoRequest(
                            file=await client.upload_file(photo_path)
                        ))
                        try:
                            os.remove(photo_path)
                        except:
                            pass
                except:
                    pass
            
            if ORIGINAL_NAME:
                await client(UpdateProfileRequest(
                    first_name=ORIGINAL_NAME,
                    last_name=""
                ))
            
            await event.reply(" You're back to original")
        except Exception as e:
            await event.reply(f" Failed to restore: `{str(e)[:100]}`")
        return
    

    if text == "ping":
        start = time.perf_counter()
        await event.reply(" Pinging")  
        end = time.perf_counter()
        ping_ms = (end - start) * 1000
        await event.reply(f"**ping is** `{ping_ms:.2f} ms`")
        return
    
    if text == "status":
        status_msg = f"""
📊 **BOT STATUS**

 **Admins:** {len(ADMIN_IDS)} users
 **Foshlist size:** {len(FOSHLIST)} items
 **Spam target:** `{SPAM_TARGET or 'Not set'}`
 **Spam text:** `{SPAM_TEXT[:50]}...`
 **Spam speed:** `{SPAM_SPEED} seconds`
**Spam active:** {SPAM_ACTIVE}
 **Enemy target:** `{ENEMY_TARGET or 'None'}`
 **Enemy active:** {ENEMY_ACTIVE}
"""
        await event.reply(status_msg)
        return
    
    if text.startswith("addadmin "):
        try:
            new_admin = int(text[9:].strip())
            if new_admin == user_id:
                await event.reply(" You are already an admin!")
                return
            if new_admin in ADMIN_IDS:
                await event.reply(" User is already an admin.")
                return
            ADMIN_IDS.add(new_admin)
            await event.reply(f" User `{new_admin}` is now an admin")
            print(f"[BOT]  New admin added: {new_admin}")
            print(f"[BOT]  Current admins: {ADMIN_IDS}")
            
            try:
                await client.send_message(
                    new_admin,
                    "you are new admin\n"
                    "• `help` - Show all commands\n"
                    "• `spam` - Start spamming\n"
                    "• `spamoff` - Stop spamming\n"
                    "• `speed <1-60>` - Set spam speed (silent)\n"
                    "• `setfosh <text>` - Set spam message\n"
                    "• `id` - Get chat ID\n"
                    "• `setid <chat_id>` - Set target chat\n"
                    "• `addfosh` - Save replied message\n"
                    "• `listfosh` - Show all saved\n"
                    "• `setenemy` - Mark enemy\n"
                    "• `clone @user` - Clone profile\n"
                    "• `ping` - Check latency\n"
                    "• `status` - Show config\n\n"
                )
                print(f"[BOT]  Welcome message sent to {new_admin}")
            except Exception as e:
                print(f"[BOT]  Could not send welcome: {e}")
                await event.reply(f" Could not send welcome to {new_admin}. They need to message the bot first.")
                
        except ValueError:
            await event.reply(" Invalid user ID. Must be a number.")
        return
    
    if text.startswith("removeadmin "):
        try:
            rem_admin = int(text[12:].strip())
            if rem_admin not in ADMIN_IDS:
                await event.reply("ℹ User is not an admin.")
                return
            if len(ADMIN_IDS) <= 1:
                await event.reply(" Cannot remove the last admin.")
                return
            ADMIN_IDS.remove(rem_admin)
            await event.reply(f" User `{rem_admin}` root killed from admin list")
            print(f"[BOT]  Admin killed: {rem_admin}")
            print(f"[BOT]  Current admins: {ADMIN_IDS}")
        except ValueError:
            await event.reply(" Invalid user ID.")
        return


async def main():
    global client
    
    print("=" * 60)
    print("[BOT] 🚀 Starting Rebel Bot...")
    print(f"[BOT] 👑 Admins: {ADMIN_IDS}")
    print("[BOT] 🔇 Non-admins: COMPLETE SILENCE")
    print("[BOT] 🎯 Enemy auto-reply: ACTIVE (private only)")
    print("[BOT] 📝 NO SLASH MODE: Just type commands")
    print("[BOT] 📍 RESPONSE MODE: EVERYWHERE (Private, Groups, Channels)")
    print(f"[BOT] ⏱️ Default spam speed: {SPAM_SPEED}s")
    print("=" * 60)
    
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    
    client.add_event_handler(handle_all_messages, events.NewMessage(incoming=True))
    
    me = await client.get_me()
    print(f"[BOT] ✅ Logged in as: {me.first_name} (@{me.username})")
    print(f"[BOT] 🆔 User ID: {me.id}")
    print("[BOT] ✅ READY!")
    print("=" * 60)
    
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        print("[BOT] Shutting down...")
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
