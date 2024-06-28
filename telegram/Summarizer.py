from pytube import YouTube
import os
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

def download_youtube_audio(url, destination="."):
    try:
        yt = YouTube(url)
    except Exception as e:
        raise ValueError(f"Failed to initialize YouTube object for URL {url}: {e}")

    # Check video length
    if yt.length > 10 * 60:
        raise ValueError("Video is too long. Please provide a video that is less than 10 minutes long.")

    # Select the audio stream
    audio_stream = yt.streams.filter(only_audio=True).first()
    if not audio_stream:
        raise ValueError("No audio stream available for this video.")

    # Download the audio stream
    out_file = audio_stream.download(output_path=destination)

    # Convert file to mp3 using ffmpeg
    audio_file = os.path.splitext(out_file)[0] + '.mp3'
    try:
        subprocess.run(['ffmpeg', '-i', out_file, audio_file], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg error: {e}")

    # Remove the original file
    os.remove(out_file)

    print(f"Downloaded and converted to MP3: {audio_file}")
    return audio_file

def get_transcript(url):
    # Extract the video ID from the URL considering different formats
    if "youtube.com" in url:
        video_id = url.split("v=")[1]
    elif "youtu.be" in url:
        video_id = url.split("/")[-1]
    else:
        raise ValueError("Invalid YouTube URL. Please provide a valid YouTube video URL.")

    # Retrieve manually created transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
    except Exception as e:
        print(f"Error retrieving manual transcript: {e}")
        # If no manually created transcript is available, use the auto-generated one
        try:
            yt = YouTube(url)
            return yt.captions.get_by_language_code("en").generate_srt_captions()
        except Exception as e:
            raise RuntimeError(f"Error retrieving auto-generated transcript: {e}")

    # Get the transcript for the YouTube video
    text = ""
    for line in transcript:
        text += line["text"] + " "
    return text

def summarize_text_gpt(prompt):
    pre_prompt = 'You are a model that receives a transcription of a YouTube video. Your task is to correct any words that may be incorrect based on the context, and transform it into a well-structured summary of the entire video. Your summary should highlight important details and provide additional context when necessary. Aim to be detailed, particularly when addressing non-trivial aspects of the content. The summary should encompass at least 20-30% of the original text length.'
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    CHUNK_SIZE = 12000

    def generate_completion(chunk, previous_chunk):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": pre_prompt},
                    {"role": "user", "content": f"Here is some additional context from the previous chunk: {previous_chunk}"},
                    {"role": "user", "content":  f"Here is the current chunk: {chunk}"},
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    prompt_chunks = [prompt[i:i + CHUNK_SIZE] for i in range(0, len(prompt), CHUNK_SIZE)]
    completion_chunks = []
    previous_chunk = ""

    for chunk in prompt_chunks:
        completion = generate_completion(chunk, previous_chunk)
        completion_chunks.append(completion)
        previous_chunk = chunk

    summary_result = "".join(completion_chunks)
    return summary_result

def process_subtitles(url):
    prompt = get_transcript(url)
    result_summary = summarize_text_gpt(prompt)
    return result_summary

def process_youtube_url(url):
    try:
        summary = process_subtitles(url)
        return summary
    except Exception as e:
        return f"Error processing YouTube URL: {e}"

def split_message(message, chunk_size=4000):
    return [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]

if __name__ == '__main__':
    print("This file contains functions for YouTube video summarization.")
