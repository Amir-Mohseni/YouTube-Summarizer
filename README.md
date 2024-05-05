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
    pip install pytube openai git+https://github.com/openai/whisper.git
    ```

2. **Get Started:** Clone the repository with the Jupyter Notebook.

3. **Launch Notebook:** Open `YoutubeScript.ipynb` in Jupyter.

4. **Run Notebook:** Sequentially execute cells, inputting the YouTube URL when asked.

5. **Generate Summary:** Follow on-screen prompts to download audio, transcribe, and summarize.

6. **Review Summary:** Access the final summary in `summary.txt`.

## Acknowledgments

- **pytube:** YouTube video downloads.
- **OpenAI:** ChatGPT 4 model provision.
- **Whisper:** Audio transcription.
