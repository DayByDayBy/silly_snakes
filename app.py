import os
import random
import requests
import ollama
from flask import Flask, request, render_template
from googleapiclient.discovery import build
import re
from dotenv import load_dotenv
# from flask_caching import Cache


app = Flask(__name__)

load_dotenv()
title_context = ''

def get_video_id(url):
    """
    extracts video ID from a YouTube URL.

    parameters:
    url (str): URL of the YouTube video.

    returns:
    str: The extracted video ID.
    """
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return match.group(1) if match else None

def get_video_title(api_key, video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(part="snippet", id= video_id)
    response = request.execute()
    if 'items' in response and len(response['items']) > 0:
        video_title = response['items'][0]['snippet']['title']
        return video_title
    return None

def get_comments(api_key, video_id, max_results=2000):
    """
    fetches youtube comments via API because why not

    parameters:
    api_key (str): The API key for authenticating with the YouTube Data API.
    video_id (str): The ID of the YouTube video for which to retrieve comments.
    max_results (int): The maximum number of comments to retrieve.
    returns:
    list: list of comments.
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results
        )
        response = request.execute()
        

        comments = [item['snippet']['topLevelComment']['snippet']['textOriginal'] for item in response['items']]        
        return comments
    
    except request.HttpError as e:
        error_message = e.content.decode('utf-8')
        return {"error": error_message}

def generate_prompts(comments, num_prompts=3, slice_size=50):
    """
    generate a list of random prompts from a list of comments.

    Parameters:
    comments (list): list of comments.
    num_prompts (int): no. of prompts to generate.
    slice_size (int): no. of words per prompt slice.
    returns:
    list: List of generated prompts.
    """

    all_comments = ' '.join(comments)
    words = all_comments.split()
    if len(words) < slice_size:
        return ["not enough words in comments to create slices."]
    
    slices = [' '.join(words[i:i+slice_size]) for i in range(len(words) - slice_size + 1)]
    
    prompts = []

    for _ in range(num_prompts):
        slice_ = random.choice(slices)
        if slice_[-1] not in '.!?':
            slice_ += '.'
        prompts.append(slice_)

    return prompts


def generate_responses(prompts, video_title, model_name='llama3.1:8b'):
    responses = []
    title_context = f"Video Title: {video_title}"

    for p in prompts:
        response = ollama.generate(model=model_name, prompt=p, context=title_context)
        responses.append(response['response'])
    return responses

@app.route('/', methods=['GET', 'POST'])
def index():
    prompts = []
    responses = []
    video_title = None
    if request.method == 'POST':
        api_key = os.getenv("YOUTUBE_API_KEY")  # Ensure you have this environment variable set
        video_url = request.form['video_url']
        video_id = get_video_id(video_url)

        if video_id:
            video_title = get_video_title(api_key, video_id)
            comments = get_comments(api_key, video_id)
            if comments:
                prompts = generate_prompts(comments)
                responses = generate_responses(prompts, title_context)
            else:
                prompts = ["no comments found or unable to retrieve comments."]
        else:
            prompts = ["invalid youtube url."]
    
    return render_template('index.html', prompts=prompts, responses=responses, video_title=video_title)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    