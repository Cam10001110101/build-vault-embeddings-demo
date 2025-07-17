#!/usr/bin/env python3
"""
The Build Vault Pipeline Demo - Real API Version

This script demonstrates The Build Vault pipeline using real API calls to process actual podcast content.

Prerequisites:
1. API Keys Required:
   - YOUTUBE_API_KEY - YouTube Data API v3
   - ASSEMBLYAI_API_KEY - Transcription service
   - OPENAI_API_KEY - GPT models
   - SUPABASE_URL & SUPABASE_ANON_KEY - Database

2. Set up environment variables before running this script
3. Note: This will incur API costs!

Usage:
    python pipeline_demo.py [--full] [--episode-url URL] [--episode-id ID]

Options:
    --full              Process full episode (disables demo mode)
    --episode-url URL   YouTube URL to process
    --episode-id ID     Existing episode ID to process
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Try to import required packages
try:
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing required package: {e}")
    print("\nInstalling required packages...")
    packages = [
        "pandas", "matplotlib", "seaborn", "python-dotenv",
        "supabase", "langchain-openai", "assemblyai", 
        "youtube-dl", "requests", "beautifulsoup4"
    ]
    for package in packages:
        subprocess.run(["pip", "install", package])
    print("\nPlease restart the script after installation.")
    sys.exit(1)

# Configure visualization
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'YOUTUBE_API_KEY',
        'ASSEMBLYAI_API_KEY',
        'OPENAI_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("\n❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables before continuing.")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True


def load_environment():
    """Load environment variables from .env file"""
    env_path = os.path.join(parent_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(f"⚠️ No .env file found at {env_path}")
        print("Make sure to set environment variables manually or create a .env file")
    
    # Verify key variables are loaded
    for var in ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'OPENAI_API_KEY']:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"❌ {var}: Not set")


def import_pipeline_modules():
    """Import all required pipeline modules"""
    print("🔄 Importing pipeline modules...")
    
    try:
        # Import configuration
        from shared.config import (
            YOUTUBE_API_KEY, ASSEMBLYAI_API_KEY, OPENAI_API_KEY,
            SUPABASE_URL, SUPABASE_ANON_KEY
        )
        print("✅ Configuration loaded")
        
        # Import Supabase client
        from shared.supabase_client import get_supabase_client
        print("✅ Supabase client imported")
        
        # Import pipeline modules
        from pipeline.audio_downloader import AudioDownloader
        print("✅ AudioDownloader imported")
        
        from pipeline.transcription_service import TranscriptionService
        print("✅ TranscriptionService imported")
        
        from pipeline.segment_processor import SegmentProcessor
        print("✅ SegmentProcessor imported")
        
        from pipeline.episode_summary_generator import EpisodeSummaryGenerator
        print("✅ EpisodeSummaryGenerator imported")
        
        from pipeline.insight_extractor import InsightExtractor
        print("✅ InsightExtractor imported")
        
        from pipeline.product_extractor import ProductExtractor
        print("✅ ProductExtractor imported")
        
        # Note: LinkExtractor import was failing in the notebook
        try:
            from pipeline.link_extractor import LinkExtractor
            print("✅ LinkExtractor imported")
        except ImportError:
            print("⚠️ LinkExtractor not available")
            LinkExtractor = None
        
        try:
            from pipeline.link_enricher import LinkEnricher
            print("✅ LinkEnricher imported")
        except ImportError:
            print("⚠️ LinkEnricher not available")
            LinkEnricher = None
        
        print("\n🎉 Successfully imported pipeline modules!")
        
        return {
            'get_supabase_client': get_supabase_client,
            'AudioDownloader': AudioDownloader,
            'TranscriptionService': TranscriptionService,
            'SegmentProcessor': SegmentProcessor,
            'EpisodeSummaryGenerator': EpisodeSummaryGenerator,
            'InsightExtractor': InsightExtractor,
            'ProductExtractor': ProductExtractor,
            'LinkExtractor': LinkExtractor,
            'LinkEnricher': LinkEnricher
        }
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTry installing missing dependencies:")
        print("  pip install supabase python-dotenv langchain-openai assemblyai youtube-dl")
        return None


def display_episode_info(episode_data):
    """Display episode information"""
    print("\n📺 Episode Information")
    print("-" * 50)
    print(f"Title: {episode_data['title']}")
    print(f"YouTube ID: {episode_data.get('youtube_video_id', 'N/A')}")
    print(f"Duration: {episode_data.get('duration', 0)} seconds")
    print(f"Published: {episode_data.get('published_at', 'Unknown')}")
    print(f"Status: {episode_data.get('status', 'Unknown')}")
    print("-" * 50)


def process_audio_download(modules, youtube_url, existing_episode_id, skip_existing):
    """Step 2: Download audio from YouTube or use existing episode"""
    downloader = modules['AudioDownloader']()
    supabase = modules['get_supabase_client']()
    
    episode_id = None
    episode_data = None
    
    if existing_episode_id:
        # Use existing episode
        result = supabase.table('podcast_episodes').select('*').eq('id', existing_episode_id).single().execute()
        if result.data:
            episode_data = result.data
            episode_id = episode_data['id']
            print(f"✅ Using existing episode: {episode_data['title']}")
        else:
            print(f"❌ Episode {existing_episode_id} not found!")
    else:
        # Download new episode
        print(f"🎵 Downloading audio from: {youtube_url}")
        
        try:
            # Check if already exists
            video_id = youtube_url.split('v=')[-1].split('&')[0]
            existing = supabase.table('podcast_episodes').select('*').eq('youtube_video_id', video_id).execute()
            
            if existing.data and skip_existing:
                episode_data = existing.data[0]
                episode_id = episode_data['id']
                print(f"✅ Episode already exists: {episode_data['title']}")
            else:
                # Download new
                result = downloader.download_audio(youtube_url)
                if result:
                    episode_id = result['episode_id']
                    episode_data = supabase.table('podcast_episodes').select('*').eq('id', episode_id).single().execute().data
                    print(f"✅ Downloaded: {episode_data['title']}")
                else:
                    print("❌ Failed to download audio")
        except Exception as e:
            print(f"❌ Download error: {e}")
    
    if episode_data:
        display_episode_info(episode_data)
    
    return episode_id, episode_data


def process_transcription(modules, episode_id, episode_data, skip_existing, max_segments):
    """Step 3: Transcribe audio using AssemblyAI"""
    if not episode_id:
        return []
    
    supabase = modules['get_supabase_client']()
    segments = []
    
    existing_segments = supabase.table('segments').select('*').eq('episode_id', episode_id).order('start_time').execute()
    
    if existing_segments.data and skip_existing:
        segments = existing_segments.data
        print(f"✅ Found existing transcription with {len(segments)} segments")
    else:
        # Transcribe audio
        print("🎙️ Starting transcription with AssemblyAI...")
        transcriber = modules['TranscriptionService']()
        
        try:
            # Get audio file path
            audio_path = f"../audio_storage/{episode_data['youtube_id']}.mp3"
            
            if os.path.exists(audio_path):
                # Start transcription
                start_time = time.time()
                
                # Simplified progress display for CLI
                print("Transcribing... (this may take several minutes)")
                
                # Note: The notebook version had a progress display that we'll simplify
                transcriber.transcribe_with_progress(audio_path, episode_id)
                
                # Get results
                segments = supabase.table('segments').select('*').eq('episode_id', episode_id).order('start_time').execute().data
                elapsed = time.time() - start_time
                print(f"\n✅ Transcription complete! {len(segments)} segments in {elapsed:.1f}s")
            else:
                print(f"❌ Audio file not found: {audio_path}")
                
        except Exception as e:
            print(f"❌ Transcription error: {e}")
    
    # Apply demo limit
    if max_segments and len(segments) > max_segments:
        segments = segments[:max_segments]
        print(f"📌 Demo mode: Using first {max_segments} segments")
    
    # Display segment samples
    if segments:
        print("\n📝 Transcript Sample (first 3 segments):")
        print("-" * 80)
        for segment in segments[:3]:
            print(f"[{segment['start_time']:.1f}s - {segment['end_time']:.1f}s] "
                  f"{segment['speaker']}: {segment['text'][:100]}...")
        print("-" * 80)
        
        # Speaker distribution
        if segments and 'speaker' in segments[0]:
            speakers = {}
            for segment in segments:
                speaker = segment['speaker']
                duration = segment['end_time'] - segment['start_time']
                speakers[speaker] = speakers.get(speaker, 0) + duration
            
            print("\n👥 Speaker Time Distribution:")
            total_time = sum(speakers.values())
            for speaker, duration in speakers.items():
                percentage = (duration / total_time) * 100
                print(f"   {speaker}: {duration:.1f}s ({percentage:.1f}%)")
    
    return segments


def process_segments(modules, episode_id, segments, skip_existing):
    """Step 4: Process segments for efficient API calls"""
    if not episode_id or not segments:
        return
    
    supabase = modules['get_supabase_client']()
    processor = modules['SegmentProcessor']()
    
    # Check if already processed
    episode_data = supabase.table('podcast_episodes').select('is_processed').eq('id', episode_id).single().execute().data
    
    if episode_data.get('is_processed') and skip_existing:
        print("✅ Segments already processed")
    else:
        print("✂️ Processing segments...")
        try:
            processor.process_episode(episode_id)
            print("✅ Segment processing complete!")
        except Exception as e:
            print(f"❌ Processing error: {e}")
    
    # Show grouping statistics
    segments_data = supabase.table('segments').select('segment_group').eq('episode_id', episode_id).execute().data
    if segments_data:
        groups = set(s['segment_group'] for s in segments_data if s.get('segment_group'))
        
        print("\n✂️ Segment Grouping Results:")
        print(f"   Total Segments: {len(segments_data)}")
        print(f"   Processing Groups: {len(groups)}")
        print(f"   Optimization: {((len(segments_data) - len(groups)) / len(segments_data) * 100):.0f}% fewer API calls")


def generate_episode_summary(modules, episode_id, skip_existing):
    """Step 5: Generate AI-powered episode summary"""
    if not episode_id:
        return None
    
    supabase = modules['get_supabase_client']()
    generator = modules['EpisodeSummaryGenerator']()
    
    # Check existing summary
    episode_data = supabase.table('podcast_episodes').select('*').eq('id', episode_id).single().execute().data
    existing_summary = episode_data.get('summary') or episode_data.get('description')
    
    if existing_summary and len(existing_summary) > 100 and skip_existing:
        print("✅ Summary already exists")
        summary = existing_summary
    else:
        print("📝 Generating episode summary with GPT-4...")
        try:
            summary = generator.generate_summary(episode_id)
            print("✅ Summary generated!")
        except Exception as e:
            print(f"❌ Summary generation error: {e}")
            summary = existing_summary or "No summary available"
    
    # Display summary
    if summary:
        print("\n📝 Episode Summary:")
        print("-" * 80)
        print(summary[:500] + ('...' if len(summary) > 500 else ''))
        print("-" * 80)
        print(f"Word count: {len(summary.split())} words")
    
    return summary


def extract_insights(modules, episode_id, skip_existing, max_insights):
    """Step 6: Extract categorized insights"""
    if not episode_id:
        return []
    
    supabase = modules['get_supabase_client']()
    extractor = modules['InsightExtractor']()
    
    # Check existing insights
    existing_insights = supabase.table('insights').select('*').eq('episode_id', episode_id).execute()
    
    if existing_insights.data and skip_existing:
        insights = existing_insights.data
        print(f"✅ Found {len(insights)} existing insights")
    else:
        print("💡 Extracting insights with GPT-4...")
        try:
            # Extract insights
            extractor.extract_insights_for_episode(episode_id)
            
            # Get results
            insights = supabase.table('insights').select('*').eq('episode_id', episode_id).execute().data
            print(f"✅ Extracted {len(insights)} insights!")
        except Exception as e:
            print(f"❌ Insight extraction error: {e}")
            insights = []
    
    # Apply demo limit
    if max_insights and len(insights) > max_insights:
        insights = insights[:max_insights]
        print(f"📌 Demo mode: Showing first {max_insights} insights")
    
    # Display insights by category
    if insights:
        df_insights = pd.DataFrame(insights)
        categories = df_insights['category'].value_counts()
        
        print("\n💡 Extracted Insights:")
        print("-" * 80)
        
        for category, count in categories.items():
            print(f"\n{category} ({count}):")
            cat_insights = df_insights[df_insights['category'] == category].head(3)
            for _, insight in cat_insights.iterrows():
                print(f"  • {insight['content'][:150]}...")
        
        # Save visualization
        plt.figure(figsize=(10, 5))
        categories.plot(kind='bar')
        plt.title('Insight Distribution by Category')
        plt.xlabel('Category')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('insight_distribution.png')
        print("\n📊 Saved insight distribution chart to 'insight_distribution.png'")
        plt.close()
    
    return insights


def extract_products(modules, episode_id, insights):
    """Step 7: Extract developer tools and platforms mentioned"""
    if not episode_id or not insights:
        return []
    
    supabase = modules['get_supabase_client']()
    product_extractor = modules['ProductExtractor']()
    
    print("📦 Extracting products from insights...")
    try:
        # Extract products
        extracted_count = product_extractor.extract_products_from_insights(insights)
        print(f"✅ Extracted {extracted_count} product mentions")
        
        # Get unique products
        products_result = supabase.table('products').select('*').execute()
        products = products_result.data
        
        # Show products mentioned in this episode
        episode_products = []
        for product in products:
            if episode_id in (product.get('episode_ids') or []):
                episode_products.append(product)
        
        if episode_products:
            print("\n📦 Products Mentioned:")
            print("-" * 50)
            for product in episode_products[:6]:
                print(f"  • {product['name']} (Mentions: {product.get('mention_count', 1)})")
            if len(episode_products) > 6:
                print(f"  ... and {len(episode_products) - 6} more")
            print("-" * 50)
        
        return episode_products
        
    except Exception as e:
        print(f"❌ Product extraction error: {e}")
        return []


def process_links(modules, episode_id, skip_existing, demo_mode):
    """Step 8: Extract and enrich links from episode description"""
    if not episode_id:
        return []
    
    LinkExtractor = modules.get('LinkExtractor')
    LinkEnricher = modules.get('LinkEnricher')
    
    if not LinkExtractor:
        print("⚠️ LinkExtractor not available, skipping link processing")
        return []
    
    supabase = modules['get_supabase_client']()
    link_extractor = LinkExtractor()
    
    # Check existing links
    existing_links = supabase.table('episode_links').select('*').eq('episode_id', episode_id).execute()
    
    if existing_links.data and skip_existing:
        links = existing_links.data
        print(f"✅ Found {len(links)} existing links")
    else:
        print("🔗 Extracting links from description...")
        try:
            # Extract links
            link_extractor.extract_links_for_episode(episode_id)
            
            # Get extracted links
            links = supabase.table('episode_links').select('*').eq('episode_id', episode_id).execute().data
            print(f"✅ Extracted {len(links)} links")
            
            # Enrich links (limit for demo)
            if links and not demo_mode and LinkEnricher:
                print("🔍 Enriching links with AI summaries...")
                link_enricher = LinkEnricher()
                enriched = link_enricher.enrich_links(limit=3)
                print(f"✅ Enriched {enriched} links")
                
                # Refresh links data
                links = supabase.table('episode_links').select('*').eq('episode_id', episode_id).execute().data
                
        except Exception as e:
            print(f"❌ Link processing error: {e}")
            links = []
    
    # Display links
    if links:
        print("\n🔗 Episode Links:")
        print("-" * 80)
        for link in links[:5]:
            enriched = link.get('enriched', False)
            status = '✓ Enriched' if enriched else '○ Pending'
            print(f"  [{status}] {link.get('title', link['url'])}")
            if link.get('description'):
                print(f"         {link['description'][:100]}...")
        if len(links) > 5:
            print(f"  ... and {len(links) - 5} more links")
        print("-" * 80)
    
    return links


def generate_embeddings(modules, episode_id, demo_mode):
    """Step 9: Generate vector embeddings for semantic search"""
    if not episode_id or demo_mode:
        if demo_mode:
            print("\n⚠️ Embeddings skipped in demo mode")
            print("In production, this step generates 3072-dimensional vectors for semantic search.")
        return
    
    supabase = modules['get_supabase_client']()
    
    print("🔢 Generating vector embeddings...")
    
    try:
        from langchain_openai import OpenAIEmbeddings
        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
        
        # Check what needs embeddings
        segments_need = supabase.table('segments').select('id, text').eq('episode_id', episode_id).is_('embedding', 'null').execute().data
        insights_need = supabase.table('insights').select('id, content').eq('episode_id', episode_id).is_('embedding', 'null').execute().data
        
        total_needed = len(segments_need) + len(insights_need)
        
        if total_needed > 0:
            print(f"📊 Need to generate embeddings for:")
            print(f"   - {len(segments_need)} segments")
            print(f"   - {len(insights_need)} insights")
            
            # Generate segment embeddings
            if segments_need:
                texts = [s['text'] for s in segments_need[:5]]
                vectors = embeddings_model.embed_documents(texts)
                
                for i, (segment, vector) in enumerate(zip(segments_need[:5], vectors)):
                    supabase.table('segments').update({
                        'embedding': vector
                    }).eq('id', segment['id']).execute()
                
                print(f"✅ Generated embeddings for {len(vectors)} segments")
            
            # Generate insight embeddings
            if insights_need:
                texts = [i['content'] for i in insights_need[:5]]
                vectors = embeddings_model.embed_documents(texts)
                
                for i, (insight, vector) in enumerate(zip(insights_need[:5], vectors)):
                    supabase.table('insights').update({
                        'embedding': vector
                    }).eq('id', insight['id']).execute()
                
                print(f"✅ Generated embeddings for {len(vectors)} insights")
        else:
            print("✅ All items already have embeddings")
            
    except Exception as e:
        print(f"❌ Embedding error: {e}")


def display_summary(episode_id, episode_data, segments, insights, products, links):
    """Display final processing summary"""
    if not episode_id:
        print("❌ No episode was processed. Check the configuration and try again.")
        return
    
    # Gather statistics
    stats = {
        "Episode": episode_data.get('title', 'Unknown'),
        "Duration": f"{episode_data.get('duration', 0)} seconds",
        "Segments": len(segments),
        "Insights": len(insights),
        "Products": len(products),
        "Links": len(links),
        "Status": episode_data.get('status', 'Unknown')
    }
    
    print("\n" + "=" * 80)
    print("🎉 Pipeline Complete!")
    print("=" * 80)
    
    # Display stats
    print("\nProcessing Statistics:")
    for stat, value in stats.items():
        print(f"  {stat:.<20} {value}")
    
    # Cost estimation
    costs = {
        "AssemblyAI Transcription": 0.00025 * episode_data.get('duration', 0),
        "GPT-4 Summary": 0.03 * 0.5,
        "GPT-4 Insights": 0.03 * len(segments) * 0.3,
        "Embeddings": 0.00013 * (len(segments) + len(insights)),
    }
    total_cost = sum(costs.values())
    
    print("\n💰 Estimated API Costs:")
    for service, cost in costs.items():
        print(f"  {service:.<30} ${cost:.4f}")
    print(f"  {'Total':.<30} ${total_cost:.4f}")
    print("\nNote: These are rough estimates. Actual costs may vary.")
    
    print("\n🚀 Next Steps:")
    print("1. View in Web Interface:")
    print("   cd ../web && python app.py")
    print("   Then visit http://localhost:8000")
    print("\n2. Search Insights: Use the web interface to search across all extracted insights")
    print("3. Browse Products: View all mentioned developer tools in the products directory")
    print("4. API Access: Query the data via FastAPI endpoints")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Process podcast episodes through The Build Vault pipeline')
    parser.add_argument('--full', action='store_true', help='Process full episode (disables demo mode)')
    parser.add_argument('--episode-url', help='YouTube URL to process')
    parser.add_argument('--episode-id', help='Existing episode ID to process')
    parser.add_argument('--skip-existing', action='store_true', default=True, 
                       help='Skip stages that have already been completed (default: True)')
    
    args = parser.parse_args()
    
    # Configuration
    DEMO_MODE = not args.full
    YOUTUBE_URL = args.episode_url or "https://www.youtube.com/watch?v=3vk8uT0p39w"
    EXISTING_EPISODE_ID = args.episode_id
    SKIP_EXISTING = args.skip_existing
    MAX_INSIGHTS = 10 if DEMO_MODE else None
    MAX_SEGMENTS = 5 if DEMO_MODE else None
    
    print("=" * 80)
    print("The Build Vault Pipeline Demo")
    print("=" * 80)
    
    if DEMO_MODE:
        print("\n🎯 Demo Mode Active")
        print("Processing will be limited to save API costs:")
        print(f"  - Max {MAX_INSIGHTS} insights")
        print(f"  - Max {MAX_SEGMENTS} segments")
        print("  - Using smaller models where possible")
        print("\nUse --full flag to process complete episodes")
    
    # Load environment
    load_environment()
    
    # Check environment
    if not check_environment():
        return
    
    # Import modules
    modules = import_pipeline_modules()
    if not modules:
        return
    
    # Initialize database connection
    print("\n🔄 Connecting to Supabase...")
    try:
        supabase = modules['get_supabase_client']()
        result = supabase.table('podcast_episodes').select('id').limit(1).execute()
        print("✅ Successfully connected to Supabase!")
        
        count_result = supabase.table('podcast_episodes').select('id', count='exact').execute()
        print(f"📊 Database contains {count_result.count} episodes")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return
    
    # Process pipeline steps
    episode_id = None
    episode_data = None
    segments = []
    insights = []
    products = []
    links = []
    
    try:
        # Step 1: Audio Download
        print("\n" + "="*50)
        print("Step 1: Audio Download")
        print("="*50)
        episode_id, episode_data = process_audio_download(
            modules, YOUTUBE_URL, EXISTING_EPISODE_ID, SKIP_EXISTING
        )
        
        if not episode_id:
            print("❌ Failed to get episode. Exiting.")
            return
        
        # Step 2: Transcription
        print("\n" + "="*50)
        print("Step 2: Transcription")
        print("="*50)
        segments = process_transcription(
            modules, episode_id, episode_data, SKIP_EXISTING, MAX_SEGMENTS
        )
        
        # Step 3: Segment Processing
        print("\n" + "="*50)
        print("Step 3: Segment Processing")
        print("="*50)
        process_segments(modules, episode_id, segments, SKIP_EXISTING)
        
        # Step 4: Episode Summary
        print("\n" + "="*50)
        print("Step 4: Episode Summary")
        print("="*50)
        generate_episode_summary(modules, episode_id, SKIP_EXISTING)
        
        # Step 5: Insight Extraction
        print("\n" + "="*50)
        print("Step 5: Insight Extraction")
        print("="*50)
        insights = extract_insights(modules, episode_id, SKIP_EXISTING, MAX_INSIGHTS)
        
        # Step 6: Product Extraction
        print("\n" + "="*50)
        print("Step 6: Product Extraction")
        print("="*50)
        products = extract_products(modules, episode_id, insights)
        
        # Step 7: Link Processing
        print("\n" + "="*50)
        print("Step 7: Link Processing")
        print("="*50)
        links = process_links(modules, episode_id, SKIP_EXISTING, DEMO_MODE)
        
        # Step 8: Generate Embeddings
        print("\n" + "="*50)
        print("Step 8: Generate Embeddings")
        print("="*50)
        generate_embeddings(modules, episode_id, DEMO_MODE)
        
        # Display summary
        display_summary(episode_id, episode_data, segments, insights, products, links)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
