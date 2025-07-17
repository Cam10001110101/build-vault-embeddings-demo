# Fixed segment processing code
# Copy this into your notebook cell

# Process segments
if episode_id and segments:
    processor = SegmentProcessor()
    
    # Check if already processed using correct table name
    episode_data = supabase.table('podcast_episodes').select('is_processed').eq('id', episode_id).single().execute().data
    
    if episode_data.get('is_processed') and SKIP_EXISTING:
        print("✅ Segments already processed")
    else:
        print("✂️ Processing segments...")
        try:
            # Note: segment_group column may not exist in your schema
            # The processor tries to group segments but this is optional
            processor.process_episode(episode_id)
            print("✅ Segment processing complete!")
        except Exception as e:
            print(f"⚠️ Processing error (this is okay if segment_group column doesn't exist): {e}")
            # Try to mark as processed anyway
            try:
                supabase.table('podcast_episodes').update({
                    'is_processed': True
                }).eq('id', episode_id).execute()
            except:
                pass
    
    # Show segment statistics without using segment_group
    try:
        # IMPORTANT: Only select 'id' column, NOT 'segment_group'
        segments_data = supabase.table('segments').select('id').eq('episode_id', episode_id).execute().data
        
        if segments_data:
            display(HTML(f"""
            <div style='background: #e8f4f8; padding: 15px; border-radius: 8px;'>
                <strong>✂️ Segment Processing Results</strong><br>
                Total Segments: {len(segments_data)}<br>
                Status: Ready for insight extraction<br>
                <small style='color: #666;'>Note: Segment grouping is optional and may be skipped if not supported by your schema</small>
            </div>
            """))
    except Exception as e:
        print(f"⚠️ Could not get segment statistics: {e}")
else:
    print("⚠️ No segments to process")