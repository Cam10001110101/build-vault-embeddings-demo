"""
Episode Summary Generator - Creates AI-powered summaries
"""
from openai import OpenAI
from shared.config import OPENAI_API_KEY
from shared.supabase_client import get_supabase_client

class EpisodeSummaryGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.supabase = get_supabase_client()
    
    def generate_summary(self, episode_id: str) -> str:
        """Generate episode summary using GPT-4"""
        try:
            # Get episode and segments
            episode = self.supabase.table('podcast_episodes').select('*').eq('id', episode_id).single().execute()
            segments = self.supabase.table('segments').select('*').eq('episode_id', episode_id).order('start_time').execute()
            
            if not segments.data:
                return "No transcript available for summary."
            
            # Combine transcript text - check which column to use
            text_col = 'display_text' if 'display_text' in segments.data[0] else 'raw_text' if 'raw_text' in segments.data[0] else 'text'
            transcript = "\n".join([f"{s['speaker']}: {s.get(text_col, '')}" for s in segments.data[:20]])  # Limit for demo
            
            # Generate summary
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a podcast summarizer. Create a concise, engaging summary of the podcast episode."},
                    {"role": "user", "content": f"Summarize this podcast transcript:\n\n{transcript[:4000]}"}  # Token limit
                ],
                max_tokens=300
            )
            
            summary = response.choices[0].message.content
            
            # Update episode with summary
            self.supabase.table('podcast_episodes').update({
                'summary': summary
            }).eq('id', episode_id).execute()
            
            return summary
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return "Error generating summary"