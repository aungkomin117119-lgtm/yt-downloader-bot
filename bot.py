import os
import uuid
import requests
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Render Port Detection ကျော်လွှားရန် Flask Server
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is running perfectly!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

TOKEN = "8842598630:AAFNOSbt4K8Eg8zZWjQHwnHwy_TKKEv9Xkg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    await update.message.reply_text(f"မင်္ဂလာပါ။ YouTube Link ပို့ပေးပါ။ MP3 ဒေါင်းပေးပါမယ် {user_first_name}။")

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("ကျေးဇူးပြု၍ မှန်ကန်သော YouTube Link ကိုသာ ပို့ပေးပါ။")
        return

    status_message = await update.message.reply_text("ဒေါင်းလုဒ်ဆွဲနေပါသည်။ ခဏစောင့်ပေးပါ...")

    unique_id = str(uuid.uuid4())[:8]
    mp3_filename = f"song_{unique_id}.mp3"

    try:
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "downloadMode": "audio",
            "audioFormat": "mp3"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        res_data = response.json()

        if response.status_code == 200 and res_data.get("status") in ["stream", "redirect"]:
            download_link = res_data.get("url")
            
            audio_data = requests.get(download_link, stream=True)
            with open(mp3_filename, 'wb') as f:
                for chunk in audio_data.iter_content(chunk_size=8192):
                    f.write(chunk)

            if os.path.exists(mp3_filename):
                with open(mp3_filename, 'rb') as audio_file:
                    await update.message.reply_audio(
                        audio=audio_file,
                        caption="ရပါပြီခင်ဗျာ!"
                    )
                await status_message.delete()
            else:
                await status_message.edit_text("အမှားအယွင်းရှိပါသည်။ MP3 ဖိုင် သိမ်းဆည်း၍ မရပါ။")

        else:
            await status_message.edit_text("YouTube ဘက်မှ Audio ထုတ်ယူ၍ မရပါ။ ခဏကြာမှ ပြန်စမ်းပေးပါ။")

    except Exception as e:
        await status_message.edit_text(f"အမှားအယွင်းရှိပါသည်။ ERROR: {str(e)}")

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
