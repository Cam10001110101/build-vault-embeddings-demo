"""
Demo Configuration for The Build Vault Pipeline
"""

# Pre-selected demo video URL
DEMO_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with actual demo video

# Demo episode metadata
DEMO_EPISODE = {
    "title": "Building AI Applications with The Build Vault",
    "description": "A demo episode showcasing the pipeline process",
    "duration": 300,  # 5 minutes
    "episode_number": 999
}

# Pre-defined segments for demo
DEMO_SEGMENTS = [
    {
        "start": 0,
        "end": 60,
        "text": "Welcome to The Build podcast. Today we're discussing how to build AI applications using modern tools and frameworks.",
        "speaker": "Cameron Rohn"
    },
    {
        "start": 60,
        "end": 120,
        "text": "One framework I've been really excited about is LangChain. It provides a great abstraction for building LLM applications.",
        "speaker": "Tom Spencer"
    },
    {
        "start": 120,
        "end": 180,
        "text": "We've also been using Supabase for our database needs. The vector support with pgvector is fantastic for semantic search.",
        "speaker": "Cameron Rohn"
    },
    {
        "start": 180,
        "end": 240,
        "text": "For deployment, Vercel has been our go-to platform. The edge functions work great with our FastAPI backend.",
        "speaker": "Tom Spencer"
    },
    {
        "start": 240,
        "end": 300,
        "text": "Next week we'll dive deeper into prompt engineering strategies. Thanks for joining us on The Build!",
        "speaker": "Cameron Rohn"
    }
]

# Pre-defined insights for demo
DEMO_INSIGHTS = [
    {
        "category": "🧠 Frameworks & Exercises",
        "content": "LangChain provides a comprehensive abstraction layer for building LLM applications, simplifying complex AI workflows.",
        "segment_index": 1
    },
    {
        "category": "📦 Products",
        "content": "Supabase offers PostgreSQL with pgvector extension, enabling powerful vector search capabilities for AI applications.",
        "segment_index": 2
    },
    {
        "category": "💡 Business Ideas",
        "content": "Building AI-powered podcast insight extraction systems can help content creators and listeners derive more value from audio content.",
        "segment_index": 0
    },
    {
        "category": "📦 Products",
        "content": "Vercel's edge functions provide excellent performance for FastAPI backends, making it ideal for AI application deployment.",
        "segment_index": 3
    }
]

# Pre-defined products for demo
DEMO_PRODUCTS = [
    {
        "name": "LangChain",
        "category": "AI Framework",
        "description": "Framework for developing applications powered by language models"
    },
    {
        "name": "Supabase",
        "category": "Database",
        "description": "Open source Firebase alternative with PostgreSQL"
    },
    {
        "name": "Vercel",
        "category": "Deployment Platform",
        "description": "Frontend cloud platform for deploying web applications"
    }
]

# Pre-defined links for demo
DEMO_LINKS = [
    {
        "url": "https://langchain.com",
        "title": "LangChain - Build LLM Applications",
        "description": "Framework for developing applications powered by language models",
        "category": "tool"
    },
    {
        "url": "https://supabase.com",
        "title": "Supabase - Open Source Firebase Alternative",
        "description": "Build production-grade applications with PostgreSQL",
        "category": "tool"
    }
]

# Demo settings
DEMO_SETTINGS = {
    "delay_between_steps": 2,  # seconds
    "show_progress": True,
    "mock_api_calls": True,
    "skip_embeddings": True  # Don't generate real embeddings in demo
}