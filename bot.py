import os
import logging
import asyncio
import uuid
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '8842598630:AAFNOSbt4K8Eg8zZWjQHwnHwy_TKKEv9Xkg'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ။ YouTube Link ပို့ပေးပါ၊ MP3 ဒေါင်းပေးပါမယ် Ma Shwe Zin Aung။")

async def download_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtu" not in url:
        await update.message.reply_text("ကျေးဇူးပြု၍ တရားဝင် YouTube Link ကို ပို့ပေးပါ Ma Shwe Zin Aung။")
        return

    status_msg = await update.message.reply_text("သီချင်းကို ဒေါင်းလုဒ်ဆွဲနေပါပြီ...")

    unique_id = str(uuid.uuid4())[:8]
    output_template = f"song_{unique_id}.%(ext)s"
    mp3_filename = f"song_{unique_id}.mp3"

   ydl_opts = {
    'format': 'bestaudio/best',
    'cookiefile': 'cookies.txt',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
        }
    },
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': output_template,
}
    try:
        loop = asyncio.get_running_loop()
        
        # YouTube Info မှ Title နှင့် Uploader (Artist) နာမည် ရယူခြင်း
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            song_title = info.get('title', 'Unknown Title')
            song_artist = info.get('uploader', 'Unknown Artist')

        await status_msg.edit_text("Telegram သို့ တင်ပေးနေပါပြီ...")
        
        if os.path.exists(mp3_filename):
            with open(mp3_filename, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio, 
                    title=song_title,       # သီချင်းနာမည် ထည့်ပေးခြင်း
                    performer=song_artist,   # ဆိုသူ/အနုပညာရှင် နာမည် ထည့်ပေးခြင်း
                    caption="ရပါပြီခင်ဗျာ!"
                )
            os.remove(mp3_filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text("အသံဖိုင် ပြောင်းလဲရာတွင် အဆင်မပြေပါ။")

    except Exception as e:
        await status_msg.edit_text(f"အမှားအယွင်းရှိပါသည်: {str(e)}")

def main():
    print("Bot စတင် အလုပ်လုပ်နေပါပြီ ...")
    app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_mp3))

    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
