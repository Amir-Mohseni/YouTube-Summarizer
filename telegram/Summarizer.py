import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable
from openai import OpenAI
from langdetect import detect
import socks


def get_youtube_transcript(url):
    print("Extracting video ID...")
    if "youtube.com" in url:
        video_id = url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        video_id = url.split("/")[-1]
    else:
        raise ValueError("Invalid YouTube URL. Please provide a valid YouTube video URL.")

    print(f"Video ID extracted: {video_id}")

    # Load environment variables from the .env file
    load_dotenv()

    # Retrieve proxy credentials from environment variables
    proxy_user = os.getenv('PROXY_USER')
    proxy_pass = os.getenv('PROXY_PASS')
    proxy_ip = os.getenv('PROXY_IP')
    proxy_port = os.getenv('PROXY_PORT')

    # Set up the proxies dictionary
    proxies = {
        'http': f'socks5://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}',
        'https': f'socks5://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}'
    }

    transcript = None
    try:
        print("Fetching manually created transcript...")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print("Manually created transcript found.")
    except (TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable) as e:
        print(f"Manual transcript not found: {e}")
        print("Attempting to fetch auto-generated transcript...")
        try:
            # Get available transcripts in any language
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)
            # Attempt to find the first available auto-generated transcript
            for transcript_info in transcript_list:
                if transcript_info.is_generated:
                    print(f"Auto-generated transcript found in language: {transcript_info.language}")
                    transcript = transcript_info.fetch()
                    break

            if not transcript:
                print("No auto-generated transcript available.")
                return {
                    "error": True,
                    "message": "Subtitles are disabled or not available for this video."
                }
        except Exception as inner_e:
            print(f"Unexpected error during fetching auto-generated transcript: {inner_e}")
            return {
                "error": True,
                "message": "An unexpected error occurred while fetching the auto-generated transcript."
            }

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "error": True,
            "message": "An unexpected error occurred."
        }

    if transcript:
        transcript_str = '\n'.join([item['text'] for item in transcript])

        # Detect the language of the transcript
        detected_lang = detect(transcript_str)
        print(f"Detected language: {detected_lang}")

        return {
            "error": False,
            "transcript": transcript_str,
            "language": detected_lang
        }

    return {
        "error": True,
        "message": "Transcript could not be retrieved."
    }


def translate_text(text, src_lang='en', dest_lang='en'):
    system_msg = f"""
                    You are a model that receives a transcription of a YouTube video in the source language "{src_lang}".
                    Your task is to translate the transcription from "{src_lang}" to "{dest_lang}", and then provide a well-structured summary of the entire video.
                    While translating, ensure the accuracy of the translation and make corrections to any words that may be incorrect based on context.
                    After translating, transform the transcription into a detailed summary that highlights important details and provides additional context where necessary.
                    The summary should be clear and well-organized.
                    Make sure that non-trivial aspects of the content are particularly well-addressed in the summary.
        """
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Encountered error when translating the text")


def summarize_text_gpt(transcript, max_tokens):
    # Adjust the system message based on the max_tokens value
    if max_tokens <= 256:
        system_msg = f'You are a model that receives a transcription of a YouTube video. ' \
                     'Your task is to create a concise summary that highlights only the most ' \
                     f'important points, keeping the summary very brief and well within {max_tokens} tokens.'
    else:
        system_msg = f'You are a model that receives a transcription of a YouTube video. Your task is to correct ' \
                     'any words that may be incorrect based on the context, and transform it into a well-structured ' \
                     'summary of the entire video. Your summary should highlight important details and provide ' \
                     'additional context when necessary. Aim to be detailed, particularly when addressing non-trivial ' \
                     f'aspects of the content. The length of the summary should not exceed {max_tokens} tokens.'
            
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": transcript},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Encountered error when summarizing the transcript")


def summarize_yt_video(url, summary_type='medium', target_language='en'):
    try:
        transcript_data = get_youtube_transcript(url)
        if transcript_data['error']:
            return transcript_data['message']

        transcript = transcript_data['transcript']
        detected_lang = transcript_data['language']

        if target_language == 'Auto-detect' or target_language == 'auto':
            target_language = detected_lang

        if detected_lang != target_language:
            transcript = translate_text(transcript, src_lang=detected_lang, dest_lang=target_language)

        length_dict = {'short': 256, 'medium': 512, 'long': 1024, 'extra_long': 2048}
        max_tokens = length_dict[summary_type]

        summary = summarize_text_gpt(transcript, max_tokens=max_tokens)
        return summary
    except Exception as e:
        return f"Error processing YouTube URL: {e}"


if __name__ == '__main__':
    print("This file contains functions for multilingual YouTube video summarization.")

    # Example URL for testing
    # test_url = "https://www.youtube.com/watch?v=81JgczyzXy8"
    test_url = "https://www.youtube.com/watch?v=huOU8MuKOOM"

    # Test the process_youtube_url function
    try:
        summary = summarize_yt_video(test_url, target_language='en')
        print("Summary:", summary)
    except Exception as e:
        print("Error during testing:", e)
