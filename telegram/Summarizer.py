import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable
from openai import OpenAI
from pytube import YouTube
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
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"], proxies=proxies)
        print("Manually created transcript found.")
    except (TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable) as e:
        print(f"Manual transcript not found: {e}")
        print("Attempting to fetch auto-generated transcript...")
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"], proxies=proxies, preserve_formatting=True)
            print("Auto-generated transcript found.")
        except (TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable) as inner_e:
            print(f"Failed to fetch auto-generated transcript: {inner_e}")
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
        transcript_str = ' '.join([item['text'] for item in transcript])
        return {
            "error": False,
            "transcript": transcript_str
        }

    return {
        "error": True,
        "message": "Transcript could not be retrieved."
    }


def summarize_text_gpt(transcript, max_tokens=128):
    system_msg = 'You are a model that receives a transcription of a YouTube video. Your task is to correct any words ' \
                 'that may be incorrect based on the context, and transform it into a well-structured summary of the ' \
                 'entire video. Your summary should highlight important details and provide additional context when ' \
                 'necessary. Aim to be detailed, particularly when addressing non-trivial aspects of the content. The ' \
                 'summary should encompass at least 20-30% of the original text length.'
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


def summarize_yt_video(url, summary_type='medium'):
    try:
        transcript_data = get_youtube_transcript(url)
        if transcript_data['error']:
            return transcript_data['message']
        
        transcript = transcript_data['transcript']
        length_dict = {'short': 128, 'medium': 256, 'long': 512, 'extra_long': 2048}
        max_tokens = length_dict[summary_type]

        summary = summarize_text_gpt(transcript, max_tokens=max_tokens)
        return summary
    except Exception as e:
        return f"Error processing YouTube URL: {e}"


if __name__ == '__main__':
    print("This file contains functions for YouTube video summarization.")

    # Example URL for testing
    test_url = "https://www.youtube.com/watch?v=81JgczyzXy8"

    # Test the process_youtube_url function
    try:
        summary = summarize_yt_video(test_url)
        print("Summary:", summary)
    except Exception as e:
        print("Error during testing:", e)
