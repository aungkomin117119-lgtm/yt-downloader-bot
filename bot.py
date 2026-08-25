import os
import uuid
import requests
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is running live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

TOKEN = "8842598630:AAFNOSbt4K8Eg8zZWjQHwnHwy_TKKEv9Xkg"

def extract_video_id(url):
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0].split("&")[0]
    elif "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name or "မိတ်ဆွေ"
    await update.message.reply_text(f"မင်္ဂလာပါ။ YouTube Link ပို့ပေးပါ။ MP3 ဒေါင်းပေးပါမယ် {user_first_name}။")

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    video_id = extract_video_id(url)

    if not video_id:
        await update.message.reply_text("ကျေးဇူးပြု၍ မှန်ကန်သော YouTube Link ကိုသာ ပို့ပေးပါ။")
        return

    status_message = await update.message.reply_text("ဒေါင်းလုဒ်ဆွဲနေပါသည်။ ခဏစောင့်ပေးပါ...")

    unique_id = str(uuid.uuid4())[:8]
    mp3_filename = f"song_{unique_id}.mp3"

    try:
        # Direct Reliable API Endpoint
        api_url = f"https://api.co/download?id={video_id}&type=mp3"
        
        # Fallback fast download API
        fallback_api = f"https://youtube-mp36.p.rapidapi.com/dl?id={video_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        # Invidious Instance API
        inv_url = f"https://invidious.nerdvpn.de/api/v1/videos/{video_id}"
        res = requests.get(inv_url, headers=headers, timeout=10)

        if res.status_code == 200:
            data = res.json()
            title = data.get('title', 'Audio')
            uploader = data.get('author', 'Unknown Artist')
            
            # Extract audio stream directly
            adaptive_formats = data.get('adaptiveFormats', [])
            audio_url = None
            for fmt in adaptive_formats:
                if 'audio/' in fmt.get('type', ''):
                    audio_url = fmt.get('url')
                    break

            if audio_url:
                audio_resp = requests.get(audio_url, stream=True, headers=headers)
                with open(mp3_filename, 'wb') as f:
                    for chunk in audio_resp.iter_content(chunk_size=8192):
                        f.write(chunk)

                if os.path.exists(mp3_filename) and os.path.getsize(mp3_filename) > 0:
                    with open(mp3_filename, 'rb') as audio_file:
                        await update.message.reply_audio(
                            audio=audio_file,
                            title=title,
                            performer=uploader,
                            caption="ရပါပြီခင်ဗျာ!"
                        )
                    await status_message.delete()
                    return

        await status_message.edit_text("YouTube ဘက်မှ Audio ထုတ်ယူ၍ မရပါ။ အခြား Song Link ဖြင့် စမ်းပေးပါ။")

    except Exception as e:
        await status_message.edit_text(f"ဒေါင်းလုဒ်ဆွဲရာတွင် အမှားအယွင်းရှိနေပါသည်: {str(e)}")

    finally:
        if os.path.exists(mp3_filename):
            os.remove(mp3_filename)

def main():
    if not TOKEN:
        print("Error: TOKEN မရှိပါ။")
        return

    Thread(target=run_flask).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_audio))

    print("Bot စတင်ပွင့်နေပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()
