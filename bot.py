import os
import uuid
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Telegram Bot Token (Environment Variable မှ ရယူခြင်း)
TOKEN = os.getenv("8842598630:AAFNOSbt4K8Eg8zZWjQHwnHwy_TKKEv9Xkg")

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
    output_template = f"song_{unique_id}.%(ext)s"
    mp3_filename = f"song_{unique_id}.mp3"

    # YouTube Bot-Detection ကျော်လွှားရန်နှင့် အဆင်ပြေစေရန် ချိန်ညှိထားသော Option များ
    ydl_opts = {
        'format': 'bestaudio/best',
        'cookiefile': 'cookies.txt',
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb'],
            }
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        loop = asyncio.get_running_loop()

        # Download ပြုလုပ်ခြင်း
        def run_yt_dlp():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Audio')
                uploader = info.get('uploader', 'Unknown Artist')
                return title, uploader

        title, uploader = await loop.run_in_executor(None, run_yt_dlp)

        # MP3 ဖိုင် Telegram သို့ ပို့ပေးခြင်း
        if os.path.exists(mp3_filename):
            with open(mp3_filename, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=title,
                    performer=uploader,
                    caption="ရပါပြီခင်ဗျာ!"
                )
            await status_message.delete()
        else:
            await status_message.edit_text("အမှားအယွင်းရှိပါသည်။ MP3 ဖိုင် ရှာမတွေ့ပါ။")

    except Exception as e:
        await status_message.edit_text(f"အမှားအယွင်းရှိပါသည်။ ERROR: {str(e)}")

    finally:
        # ယာယီဖိုင်များကို ပြန်ဖျက်ပေးခြင်း
        if os.path.exists(mp3_filename):
            os.remove(mp3_filename)

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN ကို Environment Variable ထဲတွင် မတွေ့ပါ။")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_audio))

    print("Bot စတင်ပွင့်နေပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()
