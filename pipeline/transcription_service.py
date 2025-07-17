"""
Transcription Service - Uses AssemblyAI for transcription
"""
import assemblyai as aai
from shared.config import ASSEMBLYAI_API_KEY
from shared.supabase_client import get_supabase_client
import uuid

class TranscriptionService:
    def __init__(self):
        aai.settings.api_key = ASSEMBLYAI_API_KEY
        self.supabase = get_supabase_client()
        self.client = aai.Client()
    
    def transcribe_audio(self, audio_path: str, episode_id: str) -> list:
        """Transcribe audio file and save segments"""
        try:
            # Upload and transcribe
            transcriber = aai.Transcriber()
            config = aai.TranscriptionConfig(
                speaker_labels=True,
                speakers_expected=2
            )
            
            transcript = transcriber.transcribe(audio_path, config=config)
            
            if transcript.status == aai.TranscriptStatus.error:
                print(f"Transcription error: {transcript.error}")
                return []
            
            # Process utterances into segments
            segments = []
            for utterance in transcript.utterances:
                segment = {
                    'id': str(uuid.uuid4()),
                    'episode_id': episode_id,
                    'start_time': utterance.start / 1000,  # Convert to seconds
                    'end_time': utterance.end / 1000,
                    'raw_text': utterance.text,
                    'display_text': utterance.text,  # Same as raw_text for now
                    'speaker': f"Speaker {utterance.speaker}",
                    'confidence': utterance.confidence if hasattr(utterance, 'confidence') else 0.9,
                    'duration': (utterance.end - utterance.start) / 1000,
                    'segment_type': 'speaker_utterance',
                    'ai_enhanced': False
                }
                segments.append(segment)
            
            # Save to database
            if segments:
                self.supabase.table('segments').insert(segments).execute()
            
            return segments
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return []
    
    def transcribe_with_progress(self, audio_path: str, episode_id: str):
        """Wrapper for progress tracking"""
        class ProgressTracker:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def __iter__(self):
                yield {'status': 'Uploading audio...', 'message': 'Preparing file for transcription'}
                yield {'status': 'Processing...', 'message': 'Transcribing with AssemblyAI'}
                yield {'status': 'Complete!', 'message': 'Transcription finished'}
        
        # Do actual transcription
        segments = self.transcribe_audio(audio_path, episode_id)
        return ProgressTracker()