"""
Speech Service
================
Handles Speech Recognition (STT) and Text-to-Speech (TTS).

WHY THIS FILE EXISTS:
    Speech processing is computationally distinct from web logic.
    This service wraps the speech_recognition and pyttsx3/gTTS libraries,
    providing a clean API for the speech routes to call.
    Keeping this separate allows swapping speech engines (Google, Azure,
    Whisper) without touching any route code.
"""

import os


class SpeechService:
    """Handles speech-to-text and text-to-speech operations."""
    
    def recognize_speech(self, audio_filepath):
        """
        Convert an audio file to text using speech recognition.
        
        Uses the SpeechRecognition library with Google's free API.
        For production, consider Whisper API or Azure Speech Services.
        
        Args:
            audio_filepath: Path to the audio file (WAV, FLAC, or MP3)
            
        Returns:
            str: Transcribed text
        """
        try:
            import speech_recognition as sr
        except ImportError:
            raise ImportError(
                'speech_recognition package not installed. '
                'Run: pip install SpeechRecognition'
            )
        
        recognizer = sr.Recognizer()
        
        # Handle different audio formats
        if audio_filepath.lower().endswith('.mp3'):
            # Convert MP3 to WAV first
            audio_filepath = self._convert_to_wav(audio_filepath)
        
        with sr.AudioFile(audio_filepath) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
        
        try:
            # Use Google's free speech recognition API
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            raise ValueError('Could not understand the audio. Please try again.')
        except sr.RequestError as e:
            raise ConnectionError(f'Speech recognition service error: {e}')
    
    def synthesize_speech(self, text, output_path, language='en'):
        """
        Convert text to speech and save as an audio file.
        
        Uses gTTS (Google Text-to-Speech) for natural-sounding output.
        
        Args:
            text: The text to convert to speech
            output_path: Where to save the MP3 file
            language: Language code (default: 'en')
        """
        try:
            from gtts import gTTS
        except ImportError:
            raise ImportError(
                'gTTS package not installed. Run: pip install gTTS'
            )
        
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(output_path)
        
        return output_path
    
    def parse_voice_command(self, command_text):
        """
        Parse a transcribed voice command into an actionable intent.
        
        Supported commands:
            - "search for [keyword] jobs" → job search
            - "show my applications" → view applications
            - "find jobs in [location]" → location search
            - "what are trending skills" → skill trends
        
        Args:
            command_text: Transcribed text from speech recognition
            
        Returns:
            dict: Parsed command with intent and parameters
        """
        text = command_text.lower().strip()
        
        # Intent: Job Search
        if any(word in text for word in ['search', 'find', 'look for', 'show me']):
            if 'job' in text or 'position' in text or 'role' in text:
                # Extract the keyword (naive approach — can be enhanced with NLP)
                keywords = text.replace('search for', '').replace('find', '')\
                    .replace('look for', '').replace('show me', '')\
                    .replace('jobs', '').replace('job', '')\
                    .replace('positions', '').replace('position', '')\
                    .replace('roles', '').replace('role', '').strip()
                
                return {
                    'intent': 'search_jobs',
                    'parameters': {'keyword': keywords},
                    'action_url': f'/api/jobs/search?q={keywords}',
                }
        
        # Intent: View Applications
        if 'application' in text or 'applied' in text:
            return {
                'intent': 'view_applications',
                'parameters': {},
                'action_url': '/api/applications',
            }
        
        # Intent: Dashboard
        if 'dashboard' in text or 'stats' in text or 'statistics' in text:
            return {
                'intent': 'view_dashboard',
                'parameters': {},
                'action_url': '/api/dashboard/stats',
            }
        
        # Intent: Trending Skills
        if 'trend' in text or 'popular' in text or 'demand' in text:
            return {
                'intent': 'skill_trends',
                'parameters': {},
                'action_url': '/api/dashboard/skill-trends',
            }
        
        # Intent: Career Advice
        if 'advice' in text or 'help' in text or 'suggest' in text:
            return {
                'intent': 'career_advice',
                'parameters': {'question': command_text},
                'action_url': '/api/ai/career-advice',
            }
        
        # Fallback: Unknown command
        return {
            'intent': 'unknown',
            'parameters': {'raw_text': command_text},
            'message': 'Could not understand the command. Try: "search for Python jobs" or "show my applications"',
        }
    
    def _convert_to_wav(self, mp3_path):
        """Convert MP3 to WAV format for speech recognition."""
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError(
                'pydub package not installed. Run: pip install pydub'
            )
        
        wav_path = mp3_path.rsplit('.', 1)[0] + '.wav'
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format='wav')
        
        return wav_path
