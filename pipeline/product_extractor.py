"""
Product Extractor - Identifies products and tools mentioned
"""
import re
from shared.supabase_client import get_supabase_client

class ProductExtractor:
    def __init__(self):
        self.supabase = get_supabase_client()
        
        # Common dev tools and platforms
        self.known_products = {
            'langchain': {'name': 'LangChain', 'category': 'AI Framework'},
            'supabase': {'name': 'Supabase', 'category': 'Database'},
            'vercel': {'name': 'Vercel', 'category': 'Deployment'},
            'nextjs': {'name': 'Next.js', 'category': 'Framework'},
            'react': {'name': 'React', 'category': 'Framework'},
            'openai': {'name': 'OpenAI', 'category': 'AI Provider'},
            'github': {'name': 'GitHub', 'category': 'Version Control'},
            'docker': {'name': 'Docker', 'category': 'DevOps'},
            'kubernetes': {'name': 'Kubernetes', 'category': 'DevOps'},
            'aws': {'name': 'AWS', 'category': 'Cloud Provider'},
        }
    
    def extract_products_from_insights(self, insights: list) -> int:
        """Extract product mentions from insights"""
        try:
            products_found = {}
            
            for insight in insights:
                text = insight['content'].lower()
                
                # Check for known products
                for key, product_info in self.known_products.items():
                    if key in text:
                        name = product_info['name']
                        if name not in products_found:
                            products_found[name] = {
                                'name': name,
                                'category': product_info['category'],
                                'description': f"{name} mentioned in podcast insights",
                                'mention_count': 0,
                                'episode_ids': []
                            }
                        products_found[name]['mention_count'] += 1
                        if insight['episode_id'] not in products_found[name]['episode_ids']:
                            products_found[name]['episode_ids'].append(insight['episode_id'])
            
            # Save to database
            for product in products_found.values():
                # Check if product exists
                existing = self.supabase.table('products').select('*').eq('name', product['name']).execute()
                
                if existing.data:
                    # Update existing
                    self.supabase.table('products').update({
                        'mention_count': existing.data[0]['mention_count'] + product['mention_count'],
                        'episode_ids': list(set(existing.data[0].get('episode_ids', []) + product['episode_ids']))
                    }).eq('name', product['name']).execute()
                else:
                    # Insert new
                    self.supabase.table('products').insert(product).execute()
            
            return len(products_found)
            
        except Exception as e:
            print(f"Product extraction error: {e}")
            return 0