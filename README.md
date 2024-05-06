# YouTube Video to Text Summary Tool

This Jupyter Notebook tool transforms YouTube videos into concise text summaries using Whisper and ChatGPT 4.

## Overview

Leverage `pytube`, `openai`, and `whisper` Python libraries to:

1. **Download Audio:** Extract audio from YouTube URLs via `pytube`.
2. **Transcribe Audio:** Convert audio to text with the Whisper library.
3. **Summarize Text:** Create succinct summaries from transcriptions using ChatGPT 4, emphasizing key points and context.

## Usage Guide

1. **Set Up:** Install required libraries with pip:
    ```
    pip install -r requirements.txt
    ```

2. **Get Started:** Clone the repository with the Jupyter Notebook.

3. **Launch Notebook:** Open `YoutubeScript.ipynb` in Jupyter.

4. **Run Notebook:** Sequentially execute cells, inputting the YouTube URL when asked.

5. **Generate Summary:** Follow on-screen prompts to download audio, transcribe, and summarize.

6. **Review Summary:** Access the final summary in `summary.txt`.

## Using the Code for Telegram Bot

**To use the Telegram bot that generates text summaries from YouTube URLs:**

1.  Visit [YT\_SummaryBot](https://t.me/YT_SummaryBot) on Telegram.
2.  Send the command `/summarize` to the bot.
3.  The bot will ask you for the YouTube URL.
4.  Reply to the bot with the YouTube URL.
5.  The bot will provide you with the text summary.

## Acknowledgments

- **pytube:** YouTube video downloads.
- **OpenAI:** ChatGPT models and Whisper for audio transcription.
