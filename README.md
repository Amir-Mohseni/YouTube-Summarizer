# YouTube Video to Text Summary Tool

This tool transforms YouTube videos into concise text summaries using the `youtube-transcript-api` for transcript retrieval and GPT-4o-mini for summarization.

## Overview

Utilize `youtube-transcript-api` and `openai` Python libraries to:

1. **Retrieve Transcript:** Extract text transcripts from YouTube videos using `youtube-transcript-api`.
2. **Summarize Text:** Generate summaries with GPT-4o-mini, offering options for different summary lengths: short, medium, long, or extra long.

## Usage Guide

1. **Set Up:** Install required libraries with pip:
    ```
    pip install -r requirements.txt
    ```

2. **Get Started:** Clone the repository with the Jupyter Notebook.

3. **Launch Notebook:** Open `YoutubeScript.ipynb` in Jupyter.

4. **Run Notebook:** Input the YouTube URL and select the desired summary length.

5. **Review Summary:** Access the final summary in `summary.txt`.

## Using the Code for Telegram Bot

**To use the Telegram bot that generates text summaries from YouTube URLs:**

1. Visit [YT\_SummaryBot](https://t.me/YT_SummaryBot) on Telegram.
2. Send the command `/summarize` to the bot.
3. Choose the summary length (short, medium, long, or extra long).
4. Reply with the YouTube URL.
5. Receive the text summary.

**To run the Telegram bot:**

1. Navigate to the `telegram` directory.
2. Run `UserHandler.py` to start the bot.

## Acknowledgments

- **youtube-transcript-api:** YouTube transcript retrieval.
- **OpenAI:** GPT-4o-mini for summarization.
