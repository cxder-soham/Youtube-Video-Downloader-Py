# Streamlit main application
'''
    pytube video download logic
    Quality selection
    Error handling
'''
import streamlit as st
import os
from src.utils import validate_youtube_url
from src.downloader import download_video
from src.config import DEFAULT_DOWNLOAD_PATH

def main():
    st.title("🎥 YouTube Video Downloader")
    
    # URL Input
    url = st.text_input("Enter YouTube Video URL")
    
    # Download Path Selection
    download_path = st.text_input(
        "Download Path", 
        value=DEFAULT_DOWNLOAD_PATH
    )
    # st.folder_selector = st.button("Browse")
    # if st.folder_selector:
    #     download_path = st.text_input("Select Download Folder", 
    #                                   value=str(st.folder_selector()))

    if st.button("Browse"):
        st.info("Manually enter the folder path below.")

    # Text input for download folder
    download_path = st.text_input("Select Download Folder", value=os.getcwd())
    
    # Debugging output
    st.write(f"Selected Download Path: {download_path}")    

    
    # Quality Selection
    quality_choice = st.selectbox(
        "Select Video Quality", 
        ['High', 'Medium', 'Low']
    )
    
    # Audio Extraction Checkbox
    extract_audio = st.checkbox("Extract Audio")
    
    # Download Button
    if st.button("Download"):
        # Validate URL
        if not validate_youtube_url(url):
            st.error("Invalid YouTube URL")
            return
        
        # Progress Bar
        progress_bar = st.progress(0)
        
        # Download Process
        with st.spinner('Downloading...'):
            success, folder = download_video(
                url, 
                download_path, 
                quality_choice, 
                extract_audio
            )
        
        # Update Progress and Notification
        progress_bar.progress(100)
        
        if success:
            st.success(f"Download Complete! Saved in: {folder}")
        else:
            st.error("Download Failed")

if __name__ == "__main__":
    main()