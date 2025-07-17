"""
Segment Processor - Groups segments for efficient processing
"""
from shared.supabase_client import get_supabase_client
import uuid

class SegmentProcessor:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def process_episode(self, episode_id: str):
        """Process segments into groups"""
        try:
            # Get all segments
            segments = self.supabase.table('segments').select('*').eq('episode_id', episode_id).order('start_time').execute()
            
            if not segments.data:
                return
            
            # Check if segment_group column exists by looking at first segment
            has_segment_group = 'segment_group' in segments.data[0] if segments.data else False
            
            if has_segment_group:
                # Group segments (simple grouping by every 5 segments)
                group_size = 5
                for i in range(0, len(segments.data), group_size):
                    group_id = str(uuid.uuid4())
                    group_segments = segments.data[i:i+group_size]
                    
                    # Update segments with group ID
                    for segment in group_segments:
                        self.supabase.table('segments').update({
                            'segment_group': group_id
                        }).eq('id', segment['id']).execute()
            else:
                print("Note: segment_group column not found, skipping grouping")
            
            # Mark episode as processed
            self.supabase.table('podcast_episodes').update({
                'is_processed': True
            }).eq('id', episode_id).execute()
            
        except Exception as e:
            print(f"Segment processing error: {e}")