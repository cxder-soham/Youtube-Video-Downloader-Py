# Helper functions
'''
    URL validation
File path management
Additional helper functions
'''

import re
import os
from pytube import YouTube
import streamlit as st


def validate_youtube_url(url):
    """
    Validate YouTube URL using regex
    Returns True if valid, False otherwise
    """
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    try:
        return re.match(youtube_regex, url) is not None
    except re.error as e:
        st.error(f"Regex validation failed: {e}")
        return False


def create_download_folder(base_path, video_title):
    """
    Create a folder with video title in specified base path
    """
    # Remove invalid characters and truncate long names
    safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '_')).rstrip()
    safe_title = safe_title[:50]  # Limit folder name to 50 characters
    folder_path = os.path.join(base_path, safe_title)
    
    counter = 1
    while os.path.exists(folder_path):
        # Append a numerical suffix if folder already exists
        folder_path = os.path.join(base_path, f"{safe_title}({counter})")
        counter += 1

    try:
        os.makedirs(folder_path, exist_ok=True)
    except OSError as e:
        st.error(f"Error creating folder '{folder_path}': {e}")
        raise
    
    return folder_path
