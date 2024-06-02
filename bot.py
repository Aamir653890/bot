from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from moviepy.editor import VideoFileClip
import numpy as np
import cv2
import os

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome! Please upload a video file."
    )

def handle_video(update: Update, context: CallbackContext) -> None:
    file = update.message.video.get_file()
    file.download('input_video.mp4')
    
    keyboard = [
        [InlineKeyboardButton("2", callback_data='2')],
        [InlineKeyboardButton("3", callback_data='3')],
        [InlineKeyboardButton("6", callback_data='6')],
        [InlineKeyboardButton("9", callback_data='9')],
        [InlineKeyboardButton("12", callback_data='12')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "How many screenshots do you need?",
        reply_markup=reply_markup
    )

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    num_screenshots = int(query.data)
    
    screenshots = extract_screenshots('input_video.mp4', num_screenshots)
    collage = create_collage(screenshots)
    
    collage_path = 'collage.jpg'
    cv2.imwrite(collage_path, collage)
    
    query.message.reply_photo(photo=open(collage_path, 'rb'))
    
    os.remove('input_video.mp4')
    os.remove(collage_path)
    for screenshot in screenshots:
        os.remove(screenshot)

def extract_screenshots(video_path, num_screenshots):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    times = np.linspace(0, duration, num_screenshots + 2)[1:-1]  # Avoid first and last frames
    screenshots = []
    for i, t in enumerate(times):
        frame = clip.get_frame(t)
        screenshot_path = f'screenshot_{i}.jpg'
        cv2.imwrite(screenshot_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        screenshots.append(screenshot_path)
    return screenshots

def create_collage(image_paths):
    images = [cv2.imread(image) for image in image_paths]
    collage = np.hstack(images)
    return collage

def main():
    updater = Updater(TOKEN, use_context=True)
    
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    dp.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()
    
    updater.idle()

if __name__ == '__main__':
    main()
