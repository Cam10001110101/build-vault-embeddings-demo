"""
Link Enricher - Enriches links with AI summaries
"""
from shared.supabase_client import get_supabase_client

class LinkEnricher:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def enrich_links(self, limit: int = 3) -> int:
        """Enrich links with metadata (simplified for demo)"""
        try:
            # Get unenriched links
            links = self.supabase.table('episode_links').select('*').eq('enriched', False).limit(limit).execute()
            
            enriched_count = 0
            for link in links.data:
                # Simple enrichment - just mark as enriched
                # In production, this would fetch page content and summarize
                self.supabase.table('episode_links').update({
                    'enriched': True,
                    'description': f'Resource about {link["title"]} (auto-enriched)'
                }).eq('id', link['id']).execute()
                
                enriched_count += 1
            
            return enriched_count
            
        except Exception as e:
            print(f"Link enrichment error: {e}")
            return 0