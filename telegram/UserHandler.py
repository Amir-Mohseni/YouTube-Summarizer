import os
import telebot
from dotenv import load_dotenv
from Summarizer import summarize_yt_video

# Available languages for user selection
LANGUAGE_OPTIONS = {
    'auto': 'Auto-detect',
    'en': 'English',
    'fa': 'Persian',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'zh-cn': 'Chinese (Simplified)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ru': 'Russian',
    'ar': 'Arabic',
    'it': 'Italian',
}


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
            bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown", reply_markup=markup)

        @bot.message_handler(commands=['help'])
        def help(message):
            help_text = ("This bot can summarize the content of a YouTube video.\n"
                         "To get started, use the /summarize command. You will be prompted to enter the URL of the "
                         "YouTube video, choose the summary length: short, medium, or long, and select the target language.\nEnjoy!")
            bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

        def url_handler(message, summary_type, dest_lang):
            url = message.text
            print(f"Received YouTube URL: {url}")
            print(f"Target Language: {dest_lang}")

            try:
                summary = summarize_yt_video(url, summary_type=summary_type, target_language=dest_lang)
                summary = escape_markdown_v2(summary)
            except Exception as e:
                summary = f"Error processing YouTube URL: {e}\nPlease try again."

            bot.send_message(message.chat.id, summary, parse_mode="MarkdownV2")

        @bot.message_handler(commands=['summarize'])
        def message_handler(message):
            # Ask the user to select the target language
            markup_dest_lang = telebot.types.InlineKeyboardMarkup(row_width=3)
            for lang_code, lang_name in LANGUAGE_OPTIONS.items():
                markup_dest_lang.add(telebot.types.InlineKeyboardButton(text=lang_name, callback_data=f'destlang_{lang_code}'))
            bot.send_message(message.chat.id, "Choose the target language:", reply_markup=markup_dest_lang)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('destlang_'))
        def dest_lang_callback_query_handler(call):
            dest_lang = call.data.split('_')[1]

            # Ask for summary length after selecting target language
            markup_length = telebot.types.InlineKeyboardMarkup(row_width=3)
            short_btn = telebot.types.InlineKeyboardButton(text='Short', callback_data=f'summary_short_{dest_lang}')
            medium_btn = telebot.types.InlineKeyboardButton(text='Medium', callback_data=f'summary_medium_{dest_lang}')
            long_btn = telebot.types.InlineKeyboardButton(text='Long', callback_data=f'summary_long_{dest_lang}')
            extra_long_btn = telebot.types.InlineKeyboardButton(text='Extra Long', callback_data=f'summary_extra_long_{dest_lang}')
            markup_length.add(short_btn, medium_btn, long_btn, extra_long_btn)

            bot.send_message(call.message.chat.id, "Choose the summary length:", reply_markup=markup_length)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('summary_'))
        def summary_callback_query_handler(call):
            _, summary_type, dest_lang = call.data.split('_')
            text = "Please enter the URL of the YouTube video you would like to summarize."
            sent_msg = bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
            bot.register_next_step_handler(sent_msg, lambda message: url_handler(message, summary_type, dest_lang))

        bot.infinity_polling()

    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == '__main__':
    main()