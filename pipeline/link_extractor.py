"""
Link Extractor - Extracts links from episode description
"""
import re
import uuid
from shared.supabase_client import get_supabase_client

class LinkExtractor:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def extract_links_for_episode(self, episode_id: str):
        """Extract links from episode description"""
        try:
            # Get episode
            episode = self.supabase.table('podcast_episodes').select('*').eq('id', episode_id).single().execute()
            
            if not episode.data:
                return
            
            description = episode.data.get('description', '')
            
            # Find URLs
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:/[^\s<>"{}|\\^`\[\]]*)?'
            urls = re.findall(url_pattern, description)
            
            links = []
            for url in urls:
                # Clean URL
                url = url.rstrip('.,;:)')
                
                # Extract domain for title
                domain = url.split('/')[2] if len(url.split('/')) > 2 else url
                
                links.append({
                    'id': str(uuid.uuid4()),
                    'episode_id': episode_id,
                    'url': url,
                    'title': domain,
                    'description': f'Link from {episode.data["title"]}',
                    'link_type': 'resource',
                    'enriched': False
                })
            
            # Save links
            if links:
                self.supabase.table('episode_links').insert(links).execute()
                
        except Exception as e:
            print(f"Link extraction error: {e}")