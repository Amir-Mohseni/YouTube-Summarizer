from dotenv import load_dotenv
import os
import telebot
from Summarizer import *


# Define a function to process the YouTube URL and generate a summary
def process_youtube_url(url):
    try:
        # Use the 'process' function from your summarizer module
        summary = process_subtitles(url)
        return summary
    except Exception as e:
        # Handle any errors that may occur during processing
        return f"Error processing YouTube URL: {e}"


# Set up the Telegram Bot
def main():
    # Retrieve the Telegram bot token from environment variables
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
    bot = telebot.TeleBot(telegram_bot_token)

    # Define a welcome message
    welcome_message = "Welcome to the YouTube Video Summarizer Bot! To get started, use the /summarize command."

    # Define a command handler for the '/start' command
    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown")

    # Set button for the user to click to get start the bot, and one for the summarizer
    @bot.message_handler(commands=['/start'])
    def button(message):
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = telebot.types.KeyboardButton('/start')
        itembtn1.text = "Start"
        itembtn2 = telebot.types.KeyboardButton('/summarize')
        itembtn2.text = "Summarize"
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, "Choose a command:", reply_markup=markup)


    # Define a function to handle the user's input  (e.g., the YouTube URL)
    def url_handler(message):
        # Get the user's input
        url = message.text
        print(f"Received YouTube URL: {url}")

        # Process the YouTube URL and generate a summary
        summary = process_youtube_url(url)

        # Send the summary back to the user
        bot.send_message(message.chat.id, summary, parse_mode="Markdown")

    @bot.message_handler(commands=['summarize'])
    def message_handler(message):
        text = "Please enter the URL of the YouTube video you would like to summarize."
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, url_handler)

    # Start the bot
    bot.infinity_polling()


# Entry point of the script
if __name__ == '__main__':
    load_dotenv()
    main()
