import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

API_KEY = "9d29aa8fedmshe0475eb04ccd58ep16d1c3jsna0ddf802b1f9"
BOT_TOKEN = "8359485704:AAG3A965CMeFOkZGbx2wlPMtB6M4Mnrhfrc"

def start(update, context):
    update.message.reply_text("Send me a YouTube link 🎬")

def fetch_details(video_url):
    api = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"

    if "youtu.be" in video_url:
        video_id = video_url.split("/")[-1]
    else:
        video_id = video_url.split("v=")[-1].split("&")[0]

    qs = {
        "videoId": video_id,
        "urlAccess": "normal",
        "videos": "auto",
        "audios": "auto"
    }

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com"
    }

    res = requests.get(api, headers=headers, params=qs).json()
    return res

def handle_message(update, context):
    url = update.message.text

    if "youtube.com" not in url and "youtu.be" not in url:
        update.message.reply_text("Send a valid YouTube link ❗")
        return

    update.message.reply_text("Fetching info... ⏳")

    data = fetch_details(url)
    title = data.get("title", "Unknown Title")

    try:
        video_url = data["videos"]["items"][0]["url"]
        audio_url = data["audios"]["items"][0]["url"]
    except:
        update.message.reply_text("Failed to fetch download URLs ❌")
        return

    context.user_data["video"] = video_url
    context.user_data["audio"] = audio_url
    context.user_data["title"] = title

    buttons = [
        [InlineKeyboardButton("📹 Download Video", callback_data="download_video")],
        [InlineKeyboardButton("🎧 Download Audio", callback_data="download_audio")]
    ]

    update.message.reply_text(
        f"{title}\nChoose format 👇",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def callback_handler(update, context):
    query = update.callback_query
    query.answer()

    video_url = context.user_data.get("video")
    audio_url = context.user_data.get("audio")
    title = context.user_data.get("title", "file")

    if query.data == "download_video":
        query.edit_message_text("Sending video…")
        try:
            query.message.reply_video(video_url)
        except:
            query.message.reply_text("Video too large or failed!")

    elif query.data == "download_audio":
        query.edit_message_text("Sending audio…")
        try:
            query.message.reply_audio(audio_url)
        except:
            query.message.reply_text("Audio failed!")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_handler(CallbackQueryHandler(callback_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
