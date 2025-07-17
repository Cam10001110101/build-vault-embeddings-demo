"""
Insight Extractor - Extracts categorized insights from transcript
"""
import json
import uuid
from openai import OpenAI
from shared.config import OPENAI_API_KEY
from shared.supabase_client import get_supabase_client

class InsightExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.supabase = get_supabase_client()
    
    def extract_insights_for_episode(self, episode_id: str):
        """Extract insights from episode segments"""
        try:
            # Get segments
            segments = self.supabase.table('segments').select('*').eq('episode_id', episode_id).order('start_time').execute()
            
            if not segments.data:
                return
            
            # Process in batches
            batch_size = 10
            all_insights = []
            
            for i in range(0, min(len(segments.data), 30), batch_size):  # Limit for demo
                batch = segments.data[i:i+batch_size]
                # Check which text column to use
                text_col = 'display_text' if 'display_text' in batch[0] else 'raw_text' if 'raw_text' in batch[0] else 'text'
                transcript = "\n".join([f"{s['speaker']}: {s.get(text_col, '')}" for s in batch])
                
                # Extract insights
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": """Extract key insights from this podcast transcript. 
                        Return a JSON array with objects containing:
                        - category: one of "🧠 Frameworks & Exercises", "📦 Products", "💡 Business Ideas", "🔧 Technical Insights"
                        - content: the insight text (1-2 sentences)
                        - confidence: confidence score 0.0-1.0"""},
                        {"role": "user", "content": transcript}
                    ],
                    response_format={"type": "json_object"}
                )
                
                try:
                    insights_data = json.loads(response.choices[0].message.content)
                    insights = insights_data.get('insights', [])
                    
                    for insight in insights:
                        all_insights.append({
                            'id': str(uuid.uuid4()),
                            'episode_id': episode_id,
                            'category': insight.get('category', '💡 Business Ideas'),
                            'content': insight.get('content', ''),
                            'confidence_score': insight.get('confidence', 0.8),
                            'segment_start': batch[0]['start_time'],
                            'segment_end': batch[-1]['end_time']
                        })
                except:
                    pass
            
            # Save insights
            if all_insights:
                self.supabase.table('insights').insert(all_insights).execute()
                
        except Exception as e:
            print(f"Insight extraction error: {e}")