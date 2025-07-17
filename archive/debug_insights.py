#!/usr/bin/env python3
"""Debug script to test insights extraction"""

import os
import json
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Test OpenAI connection
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load segments
segments_df = pd.read_csv('local_data/segments.csv')
print(f"✅ Loaded {len(segments_df)} segments")

# Get first few segments
test_segments = segments_df.head(5).to_dict('records')

# Create test transcript
transcript = "\n".join([f"{s['speaker']}: {s['display_text']}" for s in test_segments])
print(f"\n📝 Test transcript ({len(transcript)} chars):")
print(transcript[:500] + "...")

# Test GPT-4 call
print("\n🤖 Testing GPT-4 API call...")
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """Extract key insights from this podcast transcript.
            You must return a valid JSON object with an 'insights' array containing objects with:
            - category: one of "🧠 Frameworks & Exercises", "📦 Products", "💡 Business Ideas", "🔧 Technical Insights"
            - content: the insight text (1-2 sentences)
            - confidence: confidence score 0.0-1.0
            
            Example:
            {
              "insights": [
                {
                  "category": "📦 Products",
                  "content": "OpenAI released new ChatGPT connectors.",
                  "confidence": 0.9
                }
              ]
            }
            
            Return ONLY the JSON object, no other text."""},
            {"role": "user", "content": f"Extract insights from:\n\n{transcript[:1000]}"}
        ],
        temperature=0.7
    )
    
    print("✅ Got response from GPT-4")
    result = response.choices[0].message.content
    print(f"\n📊 Response:\n{result}")
    
    # Parse JSON
    data = json.loads(result)
    insights = data.get('insights', [])
    print(f"\n✅ Successfully parsed {len(insights)} insights")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()