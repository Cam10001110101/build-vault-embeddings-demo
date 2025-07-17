#!/usr/bin/env python3
"""
Simplified Demo Pipeline for The Build Vault
Educational presentation and walkthrough
"""

import time
import sys
from typing import Dict, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from rich.markdown import Markdown

from demo_config import (
    DEMO_VIDEO_URL, DEMO_EPISODE, DEMO_SEGMENTS, 
    DEMO_INSIGHTS, DEMO_PRODUCTS, DEMO_LINKS, DEMO_SETTINGS
)

console = Console()

class DemoPipeline:
    def __init__(self):
        self.console = console
        self.state = {
            "video_downloaded": False,
            "transcription_complete": False,
            "segments_processed": False,
            "summary_generated": False,
            "insights_extracted": False,
            "products_extracted": False,
            "links_extracted": False,
            "embeddings_generated": False
        }
        
    def display_welcome(self):
        """Display welcome message and pipeline overview"""
        welcome_text = """
# The Build Vault Pipeline Demo

This is an educational walkthrough of The Build Vault's AI-powered podcast processing pipeline.

## Pipeline Stages:
1. **Audio Download** - Download audio from YouTube
2. **Transcription** - Convert audio to text with speaker diarization
3. **Segment Processing** - Process transcript segments
4. **Episode Summary** - Generate AI-powered summaries
5. **Insight Extraction** - Extract categorized insights
6. **Product Extraction** - Identify mentioned products
7. **Link Processing** - Extract and enrich links
8. **Vector Embeddings** - Generate semantic search embeddings

Let's walk through each step!
        """
        
        self.console.print(Panel(Markdown(welcome_text), title="Welcome", border_style="cyan"))
        self.pause()
    
    def pause(self, message="Press Enter to continue..."):
        """Pause for user input"""
        input(f"\n[cyan]{message}[/cyan]")
    
    def show_step_header(self, step_num: int, title: str, description: str):
        """Display step header"""
        self.console.print(f"\n[bold cyan]Step {step_num}: {title}[/bold cyan]")
        self.console.print(f"[dim]{description}[/dim]\n")
    
    def simulate_processing(self, task_name: str, duration: float = 2.0):
        """Simulate processing with progress indicator"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=self.console
        ) as progress:
            task = progress.add_task(f"[green]{task_name}...", total=None)
            time.sleep(duration)
            progress.update(task, description=f"[green]{task_name} complete")
        time.sleep(0.5)
    
    def step_1_audio_download(self):
        """Demo audio download step"""
        self.show_step_header(
            1, 
            "Audio Download",
            "Downloads audio from YouTube videos using youtube-dl"
        )
        
        self.console.print(f"[yellow]Video URL:[/yellow] {DEMO_VIDEO_URL}")
        self.console.print(f"[yellow]Episode:[/yellow] {DEMO_EPISODE['title']}")
        
        self.simulate_processing("Downloading audio")
        
        self.console.print("\nAudio downloaded successfully")
        self.console.print("[dim]File: audio_storage/episode_999.mp3[/dim]")
        
        self.state["video_downloaded"] = True
        self.pause()
    
    def step_2_transcription(self):
        """Demo transcription step"""
        self.show_step_header(
            2,
            "Transcription Service", 
            "Converts audio to text using AssemblyAI with speaker diarization"
        )
        
        self.simulate_processing("Uploading audio to AssemblyAI")
        self.simulate_processing("Transcribing with speaker diarization", 3.0)
        
        # Show sample transcript
        table = Table(title="Sample Transcript Segments")
        table.add_column("Time", style="cyan")
        table.add_column("Speaker", style="yellow")
        table.add_column("Text", style="white")
        
        for seg in DEMO_SEGMENTS[:3]:
            table.add_row(
                f"{seg['start']}s - {seg['end']}s",
                seg['speaker'],
                seg['text'][:50] + "..."
            )
        
        self.console.print(table)
        
        self.state["transcription_complete"] = True
        self.pause()
    
    def step_3_segment_processing(self):
        """Demo segment processing step"""
        self.show_step_header(
            3,
            "Segment Processing",
            "Groups transcript segments for efficient AI processing"
        )
        
        self.console.print("[yellow]Processing strategy:[/yellow]")
        self.console.print("Group segments by speaker continuity")
        self.console.print("Maintain 800-word chunks for API efficiency")
        self.console.print("Preserve temporal flow")
        
        self.simulate_processing("Grouping segments")
        self.simulate_processing("Optimizing for token usage")
        
        self.console.print(f"\nProcessed {len(DEMO_SEGMENTS)} segments")
        self.console.print(f"[dim]Grouped into 2 processing chunks[/dim]")
        
        self.state["segments_processed"] = True
        self.pause()
    
    def step_4_episode_summary(self):
        """Demo episode summary generation"""
        self.show_step_header(
            4,
            "Episode Summary Generation",
            "Creates concise summaries following The Build podcast style"
        )
        
        self.console.print("[yellow]Summary guidelines:[/yellow]")
        self.console.print("150-250 words")
        self.console.print("Third-person present tense")
        self.console.print("Technical focus")
        self.console.print("Forward-looking ending")
        
        self.simulate_processing("Generating summary with GPT-4", 3.0)
        
        summary = """
In Episode 999 of The Build, Cameron Rohn and Tom Spencer explore the architecture behind 
The Build Vault, their AI-powered podcast insight extraction system. They discuss how 
LangChain provides powerful abstractions for building LLM applications, making complex 
AI workflows more manageable. The conversation shifts to their database choice, with 
Supabase's PostgreSQL and pgvector extension enabling sophisticated semantic search 
capabilities. Tom highlights Vercel's edge functions as their deployment solution, 
praising the performance benefits for their FastAPI backend. Throughout the episode, 
they emphasize the importance of modular pipeline design for fault-tolerant processing. 
Looking ahead, they tease next week's deep dive into prompt engineering strategies, 
promising to share specific techniques they've developed for extracting high-quality 
insights from podcast content.
        """
        
        self.console.print(Panel(summary.strip(), title="Generated Summary", border_style="green"))
        
        self.state["summary_generated"] = True
        self.pause()
    
    def step_5_insight_extraction(self):
        """Demo insight extraction step"""
        self.show_step_header(
            5,
            "Insight Extraction",
            "Extracts categorized insights using Sophisticated Prompts v2.0.0"
        )
        
        self.console.print("[yellow]Insight categories:[/yellow]")
        categories = [
            "Frameworks & Exercises",
            "Points of View",
            "Business Ideas",
            "Stories & Anecdotes",
            "Quotes",
            "Products"
        ]
        
        for cat in categories:
            self.console.print(f"  {cat}")
        
        self.simulate_processing("Extracting insights with GPT-4", 4.0)
        
        # Show extracted insights
        table = Table(title="Extracted Insights")
        table.add_column("Category", style="cyan")
        table.add_column("Insight", style="white", width=60)
        
        for insight in DEMO_INSIGHTS:
            table.add_row(
                insight['category'],
                insight['content']
            )
        
        self.console.print(table)
        
        self.state["insights_extracted"] = True
        self.pause()
    
    def step_6_product_extraction(self):
        """Demo product extraction step"""
        self.show_step_header(
            6,
            "Product Extraction",
            "Identifies and tracks mentioned developer tools and platforms"
        )
        
        self.simulate_processing("Scanning insights for products")
        self.simulate_processing("Deduplicating and categorizing")
        
        # Show extracted products
        table = Table(title="Extracted Products")
        table.add_column("Product", style="yellow")
        table.add_column("Category", style="cyan")
        table.add_column("Description", style="white", width=40)
        
        for product in DEMO_PRODUCTS:
            table.add_row(
                product['name'],
                product['category'],
                product['description']
            )
        
        self.console.print(table)
        
        self.state["products_extracted"] = True
        self.pause()
    
    def step_7_link_processing(self):
        """Demo link extraction and enrichment"""
        self.show_step_header(
            7,
            "Link Processing",
            "Extracts links from descriptions and enriches with AI summaries"
        )
        
        self.simulate_processing("Extracting links from description")
        self.simulate_processing("Fetching page metadata")
        self.simulate_processing("Generating AI summaries", 3.0)
        
        # Show enriched links
        for link in DEMO_LINKS:
            panel_content = f"""
[yellow]URL:[/yellow] {link['url']}
[yellow]Title:[/yellow] {link['title']}
[yellow]Category:[/yellow] {link['category']}
[yellow]Description:[/yellow] {link['description']}
            """
            self.console.print(Panel(panel_content.strip(), title="Enriched Link", border_style="blue"))
        
        self.state["links_extracted"] = True
        self.pause()
    
    def step_8_embeddings(self):
        """Demo embedding generation step"""
        self.show_step_header(
            8,
            "Vector Embeddings",
            "Generates semantic search embeddings for insights and segments"
        )
        
        self.console.print("[yellow]Embedding configuration:[/yellow]")
        self.console.print("Model: text-embedding-3-large")
        self.console.print("Dimensions: 3072")
        self.console.print("Storage: pgvector in Supabase")
        
        self.simulate_processing("Generating embeddings for segments")
        self.simulate_processing("Generating embeddings for insights")
        self.simulate_processing("Storing in vector database")
        
        self.console.print("\nGenerated embeddings for:")
        self.console.print(f"  {len(DEMO_SEGMENTS)} segments")
        self.console.print(f"  {len(DEMO_INSIGHTS)} insights")
        
        self.state["embeddings_generated"] = True
        self.pause()
    
    def show_final_summary(self):
        """Display final summary and statistics"""
        summary_text = """
# Pipeline Complete!

## Processing Summary:
- **Episode**: Episode 999 - Building AI Applications with The Build Vault
- **Duration**: 5 minutes
- **Segments**: 5 processed
- **Insights**: 4 extracted
- **Products**: 3 identified
- **Links**: 2 enriched

## Key Features Demonstrated:
- Fault-tolerant pipeline design
- AI-powered content extraction
- Semantic search preparation
- Comprehensive metadata enrichment

## Next Steps:
- Data available via web interface
- Searchable through vector embeddings
- Admin panel for product management
- API endpoints for integration

Thank you for exploring The Build Vault pipeline!
        """
        
        self.console.print(Panel(Markdown(summary_text), title="Demo Complete", border_style="green"))
    
    def run(self):
        """Run the complete demo pipeline"""
        self.display_welcome()
        
        # Run each step
        self.step_1_audio_download()
        self.step_2_transcription()
        self.step_3_segment_processing()
        self.step_4_episode_summary()
        self.step_5_insight_extraction()
        self.step_6_product_extraction()
        self.step_7_link_processing()
        self.step_8_embeddings()
        
        self.show_final_summary()

def main():
    """Main entry point"""
    demo = DemoPipeline()
    
    try:
        demo.run()
    except KeyboardInterrupt:
        console.print("\n[red]Demo interrupted by user[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()