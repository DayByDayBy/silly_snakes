# you can ignore this, it was a first draft/quick sketch of the idea
# that has since been left behind for the flask app version (also in this repo, run app.py)




import os
import random
from googleapiclient.discovery import build


def get_comments(api_key, parent_id, max_results=100):
    """
    fetches comments using the YouTube Data API.

    parameters:
    api_key (str): API key for authentication
    parent_id (str):  ID of the parent comment or video for which to retrieve replies
    max_results (int):  maximum number of comments to retrieve

    returns list of comments.
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.comments().list(
        part="snippet",
        parentId=parent_id,
        maxResults=max_results
    )
    response = request.execute()

    comments = [item['snippet']['textOriginal'] for item in response['items']]
    return comments

def generate_prompts(comments, num_prompts=5, slice_size=5):
    """
    generate a list of random prompts from a list of comments

    parameters:
    comments (list): list of comments.
    num_prompts (int): no. of prompts to generate.
    slice_size (int): no. of words per prompt slice.
    
    returns list of generated prompts.
    """
    all_comments = ' '.join(comments)
    words = all_comments.split()
    if len(words) < slice_size:
        print("not enough words in comments to create slices.")
        return []
    
    slices = [' '.join(words[i:i+slice_size]) for i in range(len(words) - slice_size + 1)]
    
    prompts = []
    for _ in range(num_prompts):
        slice_ = random.choice(slices)
        slice_cap = slice_.capitalize()
        if slice_cap[-1] not in '.!?':
            slice_cap += '.'
        prompts.append(f"prompt: {slice_cap}")
    
    return prompts

def main():
    api_key = "YOUR_API_KEY"
    parent_id = "UgzDE2tasfmrYLyNkGt4AaABAg"  # Example parent comment ID or video ID

    comments = get_comments(api_key, parent_id)
    if comments:
        prompts = generate_prompts(comments)
        for prompt in prompts:
            print(prompt)

if __name__ == "__main__":
    main()
    
