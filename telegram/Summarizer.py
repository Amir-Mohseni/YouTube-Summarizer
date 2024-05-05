from pytube import YouTube
import whisper
import os
import subprocess
from openai import OpenAI
import ssl
from youtube_transcript_api import YouTubeTranscriptApi


def download_youtube_audio(url, destination="."):
    # Create a YouTube object
    yt = YouTube(url)

    ssl._create_default_https_context = ssl._create_unverified_context

    # Check video length
    if yt.length > 10 * 60:
        raise Exception("Video is too long. Please provide a video that is less than 10 minutes long.")

    # Select the audio stream
    audio_stream = yt.streams.filter(only_audio=True).first()

    # Download the audio stream
    out_file = audio_stream.download(output_path=destination)

    # Set up new filename
    base, ext = os.path.splitext(out_file)
    audio_file = base + '.mp3'

    # Convert file to mp3
    subprocess.run(['ffmpeg', '-i', out_file, audio_file])

    # Remove the original file
    os.remove(out_file)

    print(f"Downloaded and converted to MP3: {audio_file}")
    return audio_file


def transcribe_audio(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]


def write_text_to_file(text, filename="transcribed_text.txt"):
    # Write the text to the file
    with open(filename, "w") as file:
        file.write(text)


def delete_file(file_path):
    os.remove(file_path)


def get_transcript(url):
    # Get the transcript for the YouTube video
    video_id = url.split("=")[1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text = ""
    for line in transcript:
        text += line["text"] + " "
    return text


def process_audio(url):
    # Download the audio from the YouTube video
    file_path = download_youtube_audio(url)

    # Transcribe the audio and delete the file
    prompt = transcribe_audio(file_path)
    delete_file(file_path)

    # Summarize the text
    result_summary = summarize_text(prompt)

    return result_summary


def process_subtitles(url):
    prompt = get_transcript(url)
    result_summary = summarize_text(prompt)
    return result_summary


def summarize_text(prompt):
    pre_prompt = 'You are a model that receives a transcription of a YouTube video. Your task is to correct any words ' \
                 'that ' \
                 'may be incorrect based on the context, and transform it into a well-structured summary of the entire ' \
                 'video. Your summary should highlight important details and provide additional context when ' \
                 'necessary. ' \
                 'Aim to be detailed, particularly when addressing non-trivial aspects of the content. The summary ' \
                 'should ' \
                 'encompass at least 20-30% of the original text length.'
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": pre_prompt},
            {"role": "user", "content": prompt},
        ]
    )

    # The 'response' will contain the completion from the model
    summary_result = response.choices[0].message.content
    return summary_result


#def main():
#    print(process_subtitles("https://www.youtube.com/watch?v=reUZRyXxUs4"))


#if __name__ == "__main__":
#    main()
