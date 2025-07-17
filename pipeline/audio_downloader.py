"""
Audio Downloader - Downloads audio from YouTube
"""
import os
import uuid
import yt_dlp
from datetime import datetime
from shared.supabase_client import get_supabase_client

class AudioDownloader:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.audio_dir = os.path.join(os.path.dirname(__file__), '..', 'audio_storage')
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def download_audio(self, youtube_url: str) -> dict:
        """Download audio from YouTube and create episode record"""
        try:
            # Extract video ID
            video_id = youtube_url.split('v=')[-1].split('&')[0]
            
            # Check if already exists
            existing = self.supabase.table('podcast_episodes').select('*').eq('youtube_video_id', video_id).execute()
            if existing.data:
                return {'episode_id': existing.data[0]['id'], 'already_exists': True}
            
            # Download audio using yt-dlp
            output_path = os.path.join(self.audio_dir, f'{video_id}.mp3')
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                
            # Create episode record
            episode_data = {
                'id': str(uuid.uuid4()),
                'title': info.get('title', 'Unknown Title'),
                'description': info.get('description', '')[:500],
                'youtube_video_id': video_id,
                'youtube_url': youtube_url,
                'duration': info.get('duration', 0),
                'published_at': datetime.now().isoformat(),
                'status': 'downloaded',
                'audio_file_path': output_path
            }
            
            # Insert into database
            self.supabase.table('podcast_episodes').insert(episode_data).execute()
            
            return {'episode_id': episode_data['id'], 'already_exists': False}
            
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None