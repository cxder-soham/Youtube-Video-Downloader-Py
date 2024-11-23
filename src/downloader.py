import os
from pytubefix import YouTube
import streamlit as st
from src.utils import create_download_folder
from pytube.exceptions import VideoUnavailable, RegexMatchError

def download_video(url, download_path, quality_choice, extract_audio):
    """
    Download YouTube video with specified quality and optional audio extraction.
    Args:
        url (str): YouTube video URL
        download_path (str): Path to download directory
        quality_choice (str): Quality preference ('High', 'Medium', 'Low')
        extract_audio (bool): Whether to extract audio separately
    Returns:
        tuple: (success (bool), download_path (str))
    """
    try:
        # Fetch YouTube video
        yt = YouTube(url)
        
        if quality_choice == 'High':
            # First try adaptive streams for highest quality
            streams = yt.streams.filter(adaptive=True, file_extension='mp4', type='video')
            if streams:
                stream = streams.order_by('resolution').desc().first()
                # Get corresponding audio stream
                audio_stream = yt.streams.filter(adaptive=True, only_audio=True).order_by('abr').desc().first()
            else:
                # Fall back to progressive streams if adaptive not available
                streams = yt.streams.filter(progressive=True, file_extension='mp4')
                stream = streams.order_by('resolution').desc().first()
                audio_stream = None
        else:
            # For medium and low quality, use progressive streams
            streams = yt.streams.filter(progressive=True, file_extension='mp4')
            if quality_choice == 'Medium':
                available_streams = streams.order_by('resolution').desc()
                print(available_streams)
                stream = available_streams[len(available_streams)//2] if len(available_streams) > 1 else streams.first()
            else:  # Low quality
                stream = streams.get_lowest_resolution()
            audio_stream = None

        if not stream:
            raise Exception("No suitable stream found for the selected quality.")

        # Create download folder
        folder_path = create_download_folder(download_path, yt.title)
        
        # Download video
        video_filename = stream.download(output_path=folder_path)
        
        # If using adaptive streams, need to download and merge audio
        if quality_choice == 'High' and audio_stream and not stream.is_progressive:
            import ffmpeg
            
            # Download audio
            audio_filename = audio_stream.download(output_path=folder_path, filename_prefix="temp_audio_")
            
            # Output filename for merged file
            output_filename = os.path.join(folder_path, f"{yt.title}_merged.mp4")
            
            # Merge video and audio using ffmpeg
            try:
                input_video = ffmpeg.input(video_filename)
                input_audio = ffmpeg.input(audio_filename)
                ffmpeg.output(input_video, input_audio, output_filename, vcodec='copy', acodec='aac').run(overwrite_output=True)
                
                # Clean up temporary files
                os.remove(video_filename)
                os.remove(audio_filename)
            except ffmpeg.Error as e:
                st.warning("Could not merge audio and video. Keeping separate files.")

        # Download separate audio if requested
        if extract_audio:
            audio_only_stream = yt.streams.get_audio_only()
            audio_only_stream.download(output_path=folder_path, filename_prefix="(audio)")

        return True, folder_path
        
    except (VideoUnavailable, RegexMatchError) as e:
        st.error(f"Video unavailable: {e}")
        return False, None
    except Exception as e:
        st.error(f"Download failed: {e}")
        return False, None