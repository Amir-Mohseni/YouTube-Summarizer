import os
import telebot
from dotenv import load_dotenv
from Summarizer import process_youtube_url, split_message

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
            bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown", reply_markup=markup)

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
                summary = process_youtube_url(url)
            except Exception as e:
                summary = f"Error processing YouTube URL: {e}\nPlease try again."

            summary_chunks = split_message(summary)

            for chunk in summary_chunks:
                bot.send_message(message.chat.id, chunk, parse_mode="Markdown")

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
