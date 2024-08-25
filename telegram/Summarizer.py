from pytube import YouTube
import os
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable
from openai import OpenAI

def get_youtube_transcript(url):
   # Extract the video ID from the URL considering different formats
    if "youtube.com" in url:
        video_id = url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        video_id = url.split("/")[-1]
    else:
        raise ValueError("Invalid YouTube URL. Please provide a valid YouTube video URL.")
    
    try:
        # Attempt to get the manually created transcript first
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except (TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable):
        # If manual transcript is not available, get the auto-generated one
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], preserve_formatting=True)
    
    # Convert transcript to a string
    transcript_str = '\n'.join([item['text'] for item in transcript])
    return transcript_str

def summarize_text_gpt(transcript):
    system_msg = 'You are a model that receives a transcription of a YouTube video. Your task is to correct any words that may be incorrect based on the context, and transform it into a well-structured summary of the entire video. Your summary should highlight important details and provide additional context when necessary. Aim to be detailed, particularly when addressing non-trivial aspects of the content. The summary should encompass at least 20-30% of the original text length.'
    client = OpenAI(api_key=userdata.get('OPENAI_API_KEY'))
    token_limit = max(len(transcript) // 2, 4096)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": transcript},
            ],
            max_tokens=token_limit,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Encountered error when summarizing the transcript")

def summarize_yt_video(url):
    try:
        transcript = get_youtube_transcript(url)
        summary = summarize_text_gpt(transcript)
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
