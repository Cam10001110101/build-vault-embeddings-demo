# The Build Vault Pipeline Demo

Educational demonstration of The Build Vault's AI-powered podcast processing pipeline.

## Overview

This demo provides a simplified, interactive walkthrough of how The Build Vault processes podcast episodes through its sophisticated pipeline.

## Demo Modes

### 1. Jupyter Notebook - Real API Version
```bash
cd demo
jupyter notebook pipeline_demo.ipynb
```
- **Uses real API calls** to process actual podcast content
- Requires API keys (YouTube, AssemblyAI, OpenAI, Supabase)
- Interactive cells for each pipeline stage
- Live progress tracking and results
- Cost estimation included
- ⚠️ **Will incur API costs!**

### 2. Jupyter Notebook - Simulation Version
```bash
cd demo
jupyter notebook pipeline_demo_simulation.ipynb
```
- **No API calls required** - uses pre-defined demo data
- Interactive cells for each pipeline stage
- Rich visualizations and charts
- Progress animations
- Perfect for workshops and tutorials
- **Cost-free demonstrations**

### 3. Interactive CLI Walkthrough
```bash
cd demo
python run_demo.py
```
- Step-by-step presentation
- Pauses between each stage
- Detailed explanations
- Simulated processing with progress indicators

### 4. Quick CLI Overview
```bash
cd demo
python quick_demo.py
```
- Complete pipeline visualization
- Results summary
- No pauses or interaction

## What's Demonstrated

1. **Audio Download** - YouTube video to MP3 conversion
2. **Transcription** - AssemblyAI with speaker diarization
3. **Segment Processing** - Intelligent grouping for API efficiency
4. **Episode Summary** - AI-generated 150-250 word summaries
5. **Insight Extraction** - 6 categories using Sophisticated Prompts v2
6. **Product Extraction** - Developer tool identification
7. **Link Processing** - URL extraction and AI enrichment
8. **Vector Embeddings** - 3072-dimensional semantic search preparation

## Demo Data

The demo uses pre-defined sample data to simulate processing:
- Sample transcript segments with Cameron and Tom
- Example insights across all categories
- Popular developer tools (LangChain, Supabase, Vercel)
- Enriched links with metadata

## Customization

Edit `demo_config.py` to:
- Change the demo video URL
- Modify sample segments and insights
- Adjust timing and display settings
- Add your own example data

## Requirements

```bash
pip install rich
```

## Presentation Tips

1. **For live demos**: Use interactive mode to explain each step
2. **For recordings**: Quick mode shows everything at once
3. **For workshops**: Modify delays in `demo_config.py`
4. **For customization**: Replace sample data with real examples

## Architecture Highlights

- **Modular Design**: Each step can fail/resume independently
- **AI Integration**: Multiple models for different tasks
- **Token Optimization**: Intelligent segment grouping
- **Vector Search**: Modern semantic search capabilities
- **Production Ready**: Same patterns as the real pipeline