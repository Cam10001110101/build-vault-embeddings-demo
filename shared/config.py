"""
Configuration for Build Vault Pipeline
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

# Model settings
INSIGHTS_MODEL = os.getenv('INSIGHTS_MODEL', 'gpt-4')
SEGMENTS_MODEL = os.getenv('SEGMENTS_MODEL', 'gpt-4')