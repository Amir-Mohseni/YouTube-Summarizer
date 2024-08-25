import os
import telebot
from dotenv import load_dotenv
from Summarizer import summarize_yt_video
import openai

def escape_markdown_v2(text):
    """
    Helper function to escape characters for Telegram MarkdownV2.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])

def main():
    try:
        load_dotenv()
        telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
        bot = telebot.TeleBot(telegram_bot_token)

        welcome_message = "Welcome to the YouTube Video Summarizer Bot!."

        @bot.message_handler(commands=['start'])
        def start(message):
            markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            itembtn1 = telebot.types.KeyboardButton(text='/summarize')
            itembtn2 = telebot.types.KeyboardButton(text='/help')
            markup.add(itembtn1, itembtn2)
            bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown")

        @bot.message_handler(commands=['help'])
        def help(message):
            help_text = "This bot can summarize the content of a YouTube video.\nTo get started, use the /summarize " \
                        "command. You will be prompted to enter the URL of the YouTube video you would like to summarize. " \
                        "The bot will then process the video and provide you with a summary of its content.\nEnjoy!"
            bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

        def url_handler(message):
            url = message.text
            print(f"Received YouTube URL: {url}")

            try:
                summary = summarize_yt_video(url)
                summary = escape_markdown_v2(summary)  # Escape special characters for MarkdownV2
            except Exception as e:
                summary = f"Error processing YouTube URL: {e}\nPlease try again."

            bot.send_message(message.chat.id, summary, parse_mode="MarkdownV2")

        @bot.message_handler(commands=['summarize'])
        def message_handler(message):
            text = "Please enter the URL of the YouTube video you would like to summarize."
            sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
            bot.register_next_step_handler(sent_msg, url_handler)

        bot.infinity_polling()

    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == '__main__':
    main()
