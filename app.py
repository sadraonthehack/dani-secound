from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from flask import Flask, render_template_string, jsonify, request, send_from_directory
import threading
import random
import os
import time
import asyncio
from collections import deque
from datetime import datetime

# ========== TELEGRAM BOT CONFIG ==========
api_id = 19594385
api_hash = 'b5d9cce165795f9a0501f07f6a31a094'
session_name = 'user_session'
client = TelegramClient(session_name, api_id, api_hash)

jende_list = {}
replied_messages = set()
forward_enabled = True

# ========== LIVE LOG STORAGE ==========
live_logs = deque(maxlen=200)
recent_messages = deque(maxlen=50)
media_messages = deque(maxlen=30)

# ========== MEDIA FOLDER ==========
MEDIA_FOLDER = "media_files"
if not os.path.exists(MEDIA_FOLDER):
    os.mkdir(MEDIA_FOLDER)

def add_log(msg_type, content):
    timestamp = time.strftime("%H:%M:%S")
    live_logs.append({
        "time": timestamp,
        "type": msg_type,
        "content": content
    })
    print(f"[{timestamp}] {msg_type}: {content}")

# ========== INSULTS ==========
INSULTS = []
def load_insults():
    global INSULTS
    try:
        with open('fosh.txt', 'r', encoding='utf-8') as f:
            INSULTS = [line.strip() for line in f if line.strip()]
        add_log("system", f"✅ {len(INSULTS)} insults loaded")
    except FileNotFoundError:
        INSULTS = ["کص ننت", "مادر جنده", "کونی"]
        with open('fosh.txt', 'w', encoding='utf-8') as f:
            for i in INSULTS:
                f.write(i + '\n')
load_insults()

def get_insult():
    return random.choice(INSULTS) if INSULTS else "کص ننت"

async def is_admin_in_chat(event):
    try:
        chat = await event.get_chat()
        me = await client.get_me()
        participant = await client(GetParticipantRequest(chat.id, me.id))
        return isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
    except:
        return False

# ========== MEDIA HANDLING ==========
def get_media_type(message):
    if not message.media:
        return None, None
    
    if message.photo:
        return "📸 Photo", message.photo
    elif message.document:
        mime = message.document.mime_type or ""
        if "video" in mime:
            return "🎬 Video", message.document
        elif "audio" in mime:
            if "voice" in mime or "ogg" in mime:
                return "🎙️ Voice", message.document
            else:
                return "🎵 Audio", message.document
        elif "image" in mime:
            return "🖼️ Image", message.document
        elif "gif" in mime or (message.document.attributes and any(attr for attr in message.document.attributes if hasattr(attr, 'alt') and 'gif' in str(attr).lower())):
            return "🎞️ GIF", message.document
        elif "sticker" in mime:
            return "🏷️ Sticker", message.document
        else:
            return "📎 File", message.document
    elif message.sticker:
        return "🏷️ Sticker", message.sticker
    elif message.gif:
        return "🎞️ GIF", message.gif
    elif message.video_note:
        return "📹 Video Note", message.video_note
    elif message.voice:
        return "🎙️ Voice", message.voice
    elif message.audio:
        return "🎵 Audio", message.audio
    elif message.web_preview:
        return "🌐 Web Preview", message.web_preview
    
    return "📎 Unknown", None

async def download_media(message, media_obj, media_type):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sender = await message.get_sender()
        sender_name = sender.first_name or sender.username or "unknown"
        
        if "Voice" in media_type or "Audio" in media_type:
            ext = ".ogg"
        elif "Video" in media_type:
            ext = ".mp4"
        elif "GIF" in media_type:
            ext = ".gif"
        elif "Sticker" in media_type:
            ext = ".webp"
        elif "Photo" in media_type or "Image" in media_type:
            ext = ".jpg"
        else:
            ext = ".file"
        
        filename = f"{timestamp}_{sender_name}_{random.randint(100,999)}{ext}"
        filepath = os.path.join(MEDIA_FOLDER, filename)
        
        path = await message.download_media(file=filepath)
        
        if path:
            media_info = {
                "filename": filename,
                "path": path,
                "type": media_type,
                "from": sender_name,
                "from_id": sender.id,
                "time": time.strftime("%H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "caption": message.text or "بدون کپشن"
            }
            media_messages.append(media_info)
            add_log("📎 MEDIA", f"{media_type} از {sender_name}")
            return media_info
        return None
    except Exception as e:
        add_log("❌ ERROR", f"خطا در دانلود مدیا: {e}")
        return None

# ========== TELEGRAM HANDLERS ==========
@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    me = await client.get_me()
    if event.sender_id == me.id:
        return
    
    sender = event.sender_id
    sender_entity = await event.get_sender()
    
    # ========== پردازش مدیا - فقط PV ==========
    if event.media and event.is_private:
        media_type, media_obj = get_media_type(event)
        if media_type and media_obj:
            await download_media(event, media_obj, media_type)
    
    # ========== ذخیره پیام متنی - فقط PV ==========
    if event.is_private and event.text:
        if sender_entity:
            if sender_entity.username:
                display_name = f"@{sender_entity.username}"
            elif sender_entity.first_name:
                display_name = sender_entity.first_name
                if sender_entity.last_name:
                    display_name += f" {sender_entity.last_name}"
            else:
                display_name = str(sender)
        else:
            display_name = str(sender)
        
        recent_messages.append({
            "from": display_name,
            "from_id": sender,
            "text": f"📥 {event.text[:100]}",
            "time": time.strftime("%H:%M:%S")
        })
        add_log("💬 IN", f"از {display_name}: {event.text[:50]}")
    
    # ========== فحش دادن ==========
    if sender in jende_list:
        msg_id = event.message.id
        if msg_id not in replied_messages:
            replied_messages.add(msg_id)
            insult = get_insult()
            await event.reply(insult)
            add_log("💩 CURSED", f"{jende_list[sender]} → {insult}")
            
            if event.is_private:
                await event.delete()
                add_log("🗑️ DELETED", f"Private message from {jende_list[sender]}")
            elif event.is_group and await is_admin_in_chat(event):
                await event.delete()
                add_log("🗑️ DELETED", f"Group message from {jende_list[sender]}")
            
            if len(replied_messages) > 1000:
                replied_messages.clear()

@client.on(events.NewMessage(outgoing=True))
async def store_my_messages(event):
    if not event.is_private:
        return
    
    # ========== مدیا ارسالی - فقط PV ==========
    if event.media:
        media_type, media_obj = get_media_type(event)
        if media_type and media_obj:
            await download_media(event, media_obj, media_type)
    
    # ========== پیام متنی ارسالی ==========
    if event.text:
        me = await client.get_me()
        my_name = me.first_name or me.username or "Me"
        
        try:
            chat = await event.get_chat()
            if chat.first_name:
                receiver_name = chat.first_name
                if chat.last_name:
                    receiver_name += f" {chat.last_name}"
            elif chat.username:
                receiver_name = f"@{chat.username}"
            else:
                receiver_name = str(chat.id)
        except:
            receiver_name = str(event.chat_id)
        
        recent_messages.append({
            "from": f"{my_name} (من) → {receiver_name}",
            "from_id": me.id,
            "text": f"📤 {event.text[:100]}",
            "time": time.strftime("%H:%M:%S")
        })
        add_log("📤 OUT", f"به {receiver_name}: {event.text[:50]}")

@client.on(events.NewMessage(incoming=True))
async def silent_forward(event):
    if not forward_enabled or not event.is_private:
        return
    me = await client.get_me()
    if event.sender_id != me.id:
        try:
            await client.forward_messages('me', event.message)
            add_log("📨 FORWARDED", f"From {event.sender_id} to Saved")
        except:
            pass

# ========== COMMANDS ==========
@client.on(events.NewMessage(pattern=r'تنظیم مادر جنده', outgoing=True))
async def add_jende(event):
    if not event.is_reply:
        await event.edit("❌ Must reply to a message")
        return
    
    replied = await event.get_reply_message()
    uid = replied.sender_id
    name = replied.sender.first_name if replied.sender else str(uid)
    
    jende_list[uid] = name
    add_log("➕ ADDED", f"{name} ({uid}) to jende list")
    await event.edit(f"✅ {name} مادر جنده اضافه شد")

@client.on(events.NewMessage(pattern=r'حذف مادر جنده', outgoing=True))
async def remove_jende(event):
    if not event.is_reply:
        await event.edit("❌ Must reply to a message")
        return
    
    replied = await event.get_reply_message()
    uid = replied.sender_id
    
    if uid in jende_list:
        name = jende_list[uid]
        del jende_list[uid]
        add_log("➖ REMOVED", f"{name} ({uid}) from jende list")
        await event.edit(f"✅ مادر جنده حذف شد")
    else:
        await event.edit("⚠️ Not in list")

@client.on(events.NewMessage(pattern=r'فوروارد روشن', outgoing=True))
async def fon(event):
    global forward_enabled
    forward_enabled = True
    add_log("🔛 FORWARD", "Enabled")
    await event.edit("✅ Forward ON")

@client.on(events.NewMessage(pattern=r'فوروارد خاموش', outgoing=True))
async def foff(event):
    global forward_enabled
    forward_enabled = False
    add_log("🔚 FORWARD", "Disabled")
    await event.edit("❌ Forward OFF")

@client.on(events.NewMessage(pattern=r'بارگیری فحش', outgoing=True))
async def reload_fosh(event):
    load_insults()
    await event.edit(f"✅ {len(INSULTS)} insults loaded")

# ========== FLASK WEB DASHBOARD ==========
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>🔥 Jende Bot Live Dashboard</title>
    <style>
        body {
            background: #0a0e27;
            color: #0f0;
            font-family: monospace;
            padding: 20px;
        }
        h1 {
            color: #ff3366;
            text-align: center;
            border-bottom: 1px solid #ff3366;
            padding-bottom: 10px;
        }
        .container {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .panel {
            background: #11151f;
            border: 1px solid #2a3a5a;
            border-radius: 10px;
            padding: 15px;
            flex: 1;
            min-width: 300px;
        }
        .panel h3 {
            color: #ffaa44;
            margin-top: 0;
            border-bottom: 1px solid #2a3a5a;
        }
        .log {
            background: #000000aa;
            height: 400px;
            overflow-y: scroll;
            font-size: 12px;
            padding: 10px;
            border-radius: 5px;
            display: flex;
            flex-direction: column;
        }
        .log-entry {
            border-bottom: 1px solid #1a2a3a;
            padding: 5px;
            font-family: monospace;
        }
        .type-💩 { color: #ff6666; }
        .type-➕ { color: #66ff66; }
        .type-➖ { color: #ffaa66; }
        .type-📨 { color: #66aaff; }
        .type-🗑️ { color: #ff8888; }
        .type-💬 { color: #88ffaa; }
        .type-📤 { color: #ffaa66; }
        .type-📎 { color: #ff66ff; }
        .type-system { color: #aaaaaa; }
        .type-❌ { color: #ff0000; }
        .jende-list {
            background: #000000aa;
            padding: 10px;
            border-radius: 5px;
            max-height: 300px;
            overflow-y: auto;
        }
        .messages-container {
            background: #000000aa;
            height: 400px;
            overflow-y: scroll;
            padding: 10px;
            border-radius: 5px;
            display: flex;
            flex-direction: column;
        }
        .message-item {
            background: #0a0e27;
            margin: 5px 0;
            padding: 5px;
            border-right: 3px solid #ff3366;
        }
        .media-container {
            background: #000000aa;
            height: 400px;
            overflow-y: scroll;
            padding: 10px;
            border-radius: 5px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .media-item {
            background: #0a0e27;
            padding: 10px;
            border-radius: 8px;
            border-right: 3px solid #ff66ff;
        }
        .media-item img, .media-item video {
            max-width: 100%;
            max-height: 200px;
            border-radius: 5px;
        }
        .media-item audio {
            width: 100%;
            margin-top: 8px;
        }
        .media-item .media-info {
            font-size: 11px;
            color: #888;
            margin-top: 5px;
        }
        .status {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 15px;
            font-size: 12px;
        }
        .online { background: #00aa00; color: white; }
        .offline { background: #aa0000; color: white; }
        button {
            background: #2a3a5a;
            color: white;
            border: none;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background: #ff3366; }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #555;
            font-size: 11px;
        }
        .live-badge {
            background: #00aa00;
            color: white;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 12px;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            50% { opacity: 0.3; }
        }
        .voice-label {
            font-size: 10px;
            color: #666;
            margin-top: 3px;
        }
        .pv-only-badge {
            display: inline-block;
            background: #ff3366;
            color: white;
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 10px;
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <h1>🔥 JENDE BOT — COMMAND CENTER <span class="live-badge">● LIVE</span></h1>
    
    <div class="container">
        <div class="panel">
            <h3>📡 LIVE LOGS</h3>
            <div class="log" id="logs">
                {% for log in logs|reverse %}
                <div class="log-entry type-{{ log.type }}">
                    [{{ log.time }}] {{ log.type }}: {{ log.content }}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="panel">
            <h3>👺 JENDE LIST ({{ jende_list|length }})</h3>
            <div class="jende-list" id="jendeList">
                {% if jende_list %}
                    {% for uid, name in jende_list.items() %}
                    <div>🔴 {{ name }} ({{ uid }})</div>
                    {% endfor %}
                {% else %}
                    <div style="color: #888;">📭 لیست خالی است</div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="panel">
            <h3>📨 PRIVATE MESSAGES (جدیدترین اول)</h3>
            <div class="messages-container" id="messages">
                {% if recent_messages %}
                    {% for msg in recent_messages|reverse %}
                    <div class="message-item">
                        [{{ msg.time }}] <strong>{{ msg.from }}</strong>: {{ msg.text }}
                    </div>
                    {% endfor %}
                {% else %}
                    <div style="color: #888;">📭 No private messages yet</div>
                {% endif %}
            </div>
        </div>
        
        <div class="panel">
            <h3>📎 MEDIA GALLERY <span class="pv-only-badge">فقط PV</span> ({{ media_messages|length }})</h3>
            <div class="media-container" id="mediaContainer">
                {% if media_messages %}
                    {% for media in media_messages|reverse %}
                    <div class="media-item">
                        <div><strong>{{ media.type }}</strong> از <strong>{{ media.from }}</strong> [{{ media.time }}]</div>
                        {% if 'Photo' in media.type or 'Image' in media.type %}
                            <img src="/media/{{ media.filename }}" alt="Media" loading="lazy">
                        {% elif 'Video' in media.type or 'GIF' in media.type %}
                            <video controls preload="metadata">
                                <source src="/media/{{ media.filename }}">
                            </video>
                        {% elif 'Sticker' in media.type %}
                            <img src="/media/{{ media.filename }}" alt="Sticker" style="max-width: 128px;">
                        {% elif 'Voice' in media.type or 'Audio' in media.type %}
                            <audio controls preload="metadata">
                                <source src="/media/{{ media.filename }}" type="audio/ogg">
                                <source src="/media/{{ media.filename }}" type="audio/mpeg">
                                مرورگر شما پشتیبانی نمیکند
                            </audio>
                            <div class="voice-label">🔊 {{ media.filename }}</div>
                        {% else %}
                            <div style="color: #888; padding: 10px;">
                                📎 {{ media.filename }} 
                                <br><span style="font-size: 10px;">{{ media.caption[:50] }}</span>
                            </div>
                        {% endif %}
                        <div class="media-info">📝 {{ media.caption[:100] }}{% if media.caption|length > 100 %}...{% endif %}</div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div style="color: #888;">📭 No media yet</div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="panel">
            <h3>🎮 CONTROL PANEL</h3>
            <div>
                <span class="status {% if forward_enabled %}online{% else %}offline{% endif %}">
                    فوروارد: {% if forward_enabled %}فعال{% else %}خاموش{% endif %}
                </span>
            </div>
            <div style="margin-top: 10px;">
                <button onclick="sendCommand('فوروارد روشن')">▶️ فعال کردن فوروارد</button>
                <button onclick="sendCommand('فوروارد خاموش')">⏹️ غیرفعال کردن فوروارد</button>
                <button onclick="sendCommand('بارگیری فحش')">🔄 بارگیری مجدد فحش‌ها</button>
            </div>
        </div>
        
        <div class="panel">
            <h3>ℹ️ SYSTEM STATUS</h3>
            <div>🤖 Telegram Bot: <span class="status online">RUNNING</span></div>
            <div>🌐 Web Dashboard: <span class="status online">LIVE</span></div>
            <div>💩 Insults loaded: {{ insults_count }}</div>
            <div>📩 PV messages tracked: {{ recent_count }}</div>
            <div>📎 Media files (PV only): {{ media_count }}</div>
            <div>🔄 Auto-refresh: هر ۳ ثانیه</div>
        </div>
    </div>
    
    <div class="footer">
        🔥 پس‌زمینه رفرش — فقط مدیاهای پی‌وی ذخیره می‌شوند
    </div>
    
    <script>
        let lastMessageCount = {{ recent_messages|length }};
        let lastLogCount = {{ logs|length }};
        let lastMediaCount = {{ media_messages|length }};
        
        async function fetchUpdates() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                if (data.messages && data.messages.length > lastMessageCount) {
                    const messagesContainer = document.getElementById('messages');
                    const newMessages = data.messages.slice(lastMessageCount);
                    for (let i = newMessages.length - 1; i >= 0; i--) {
                        const msg = newMessages[i];
                        const msgDiv = document.createElement('div');
                        msgDiv.className = 'message-item';
                        msgDiv.innerHTML = `[${msg.time}] <strong>${msg.from}</strong>: ${msg.text}`;
                        messagesContainer.insertBefore(msgDiv, messagesContainer.firstChild);
                    }
                    lastMessageCount = data.messages.length;
                }
                
                if (data.logs && data.logs.length > lastLogCount) {
                    const logsContainer = document.getElementById('logs');
                    const newLogs = data.logs.slice(lastLogCount);
                    for (let i = newLogs.length - 1; i >= 0; i--) {
                        const log = newLogs[i];
                        const logDiv = document.createElement('div');
                        logDiv.className = `log-entry type-${log.type}`;
                        logDiv.innerHTML = `[${log.time}] ${log.type}: ${log.content}`;
                        logsContainer.insertBefore(logDiv, logsContainer.firstChild);
                    }
                    lastLogCount = data.logs.length;
                }
                
                if (data.media && data.media.length > lastMediaCount) {
                    const mediaContainer = document.getElementById('mediaContainer');
                    const newMedia = data.media.slice(lastMediaCount);
                    for (let i = newMedia.length - 1; i >= 0; i--) {
                        const media = newMedia[i];
                        const mediaDiv = document.createElement('div');
                        mediaDiv.className = 'media-item';
                        
                        let content = `<div><strong>${media.type}</strong> از <strong>${media.from}</strong> [${media.time}]</div>`;
                        
                        if (media.type.includes('Photo') || media.type.includes('Image')) {
                            content += `<img src="/media/${media.filename}" alt="Media" loading="lazy">`;
                        } else if (media.type.includes('Video') || media.type.includes('GIF')) {
                            content += `<video controls preload="metadata"><source src="/media/${media.filename}"></video>`;
                        } else if (media.type.includes('Sticker')) {
                            content += `<img src="/media/${media.filename}" alt="Sticker" style="max-width:128px;">`;
                        } else if (media.type.includes('Voice') || media.type.includes('Audio')) {
                            content += `
                                <audio controls preload="metadata">
                                    <source src="/media/${media.filename}" type="audio/ogg">
                                    <source src="/media/${media.filename}" type="audio/mpeg">
                                    مرورگر شما پشتیبانی نمیکند
                                </audio>
                                <div class="voice-label">🔊 ${media.filename}</div>
                            `;
                        } else {
                            content += `<div style="color:#888;padding:10px;">📎 ${media.filename}<br><span style="font-size:10px;">${media.caption.slice(0,50)}</span></div>`;
                        }
                        
                        content += `<div class="media-info">📝 ${media.caption.slice(0,100)}</div>`;
                        mediaDiv.innerHTML = content;
                        mediaContainer.insertBefore(mediaDiv, mediaContainer.firstChild);
                    }
                    lastMediaCount = data.media.length;
                }
                
            } catch(e) {
                console.error('Fetch error:', e);
            }
        }
        
        setInterval(fetchUpdates, 3000);
        fetchUpdates();
        
        function sendCommand(cmd) {
            fetch('/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: cmd})
            }).then(() => {
                console.log('Command sent:', cmd);
            });
        }
    </script>
</body>
</html>
"""

# ========== API Routes ==========
@app.route('/api/data')
def api_data():
    return jsonify({
        "messages": list(recent_messages),
        "logs": list(live_logs),
        "media": list(media_messages),
        "jende_count": len(jende_list),
        "timestamp": time.time()
    })

@app.route('/api/jende')
def api_jende():
    return jsonify({"list": jende_list})

@app.route('/media/<filename>')
def serve_media(filename):
    return send_from_directory(MEDIA_FOLDER, filename)

@app.route('/')
def dashboard():
    return render_template_string(
        HTML_TEMPLATE,
        logs=list(live_logs),
        jende_list=jende_list,
        recent_messages=list(recent_messages),
        media_messages=list(media_messages),
        forward_enabled=forward_enabled,
        insults_count=len(INSULTS),
        recent_count=len(recent_messages),
        media_count=len(media_messages)
    )

@app.route('/api/status')
def api_status():
    return jsonify({
        "jende_count": len(jende_list),
        "forward_enabled": forward_enabled,
        "insults_loaded": len(INSULTS),
        "recent_messages": len(recent_messages),
        "media_count": len(media_messages),
        "logs": len(live_logs)
    })

@app.route('/command', methods=['POST'])
def web_command():
    data = request.json
    cmd = data.get('command', '')
    
    async def send():
        me = await client.get_me()
        await client.send_message(me.id, cmd)
    
    asyncio.run_coroutine_threadsafe(send(), client.loop)
    
    add_log("🌐 WEB", f"Command sent: {cmd}")
    return jsonify({"status": "sent", "command": cmd})

# ========== RUN BOTH ==========
def run_flask():
    app.run(host='0.0.0.0', port=443, debug=False, use_reloader=False, threaded=True)

async def main():
    await client.start()
    add_log("system", "🔥 Telegram bot started - Media only from PV")
    print("✅ Bot running — Flask dashboard on http://localhost:443")
    print("📌 Media files saved in: media_files/ (PV only)")
    print("🎙️ Voice messages supported with audio player")
    print("🚫 Media from groups/channels is IGNORED")
    await client.run_until_disconnected()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    with client:
        client.loop.run_until_complete(main())
