"""
Speech Routes (Speech Recognition + Text-to-Speech)
=====================================================
Handles voice input (speech-to-text) and audio output (text-to-speech).

WHY THIS FILE EXISTS:
    Speech features are a unique I/O channel separate from text-based APIs.
    Speech recognition lets users search jobs or ask questions by voice.
    Text-to-speech reads back AI career advice or job descriptions aloud.
    
Endpoints:
    POST /api/speech/recognize       - Convert uploaded audio to text (STT)
    POST /api/speech/synthesize      - Convert text to audio file (TTS)
    POST /api/speech/voice-search    - Search jobs using voice input
    POST /api/speech/voice-command   - Process voice commands
"""

import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.speech_service import SpeechService

speech_bp = Blueprint('speech', __name__)
speech_service = SpeechService()


@speech_bp.route('/recognize', methods=['POST'])
@jwt_required()
def speech_to_text():
    """
    Convert uploaded audio file to text using speech recognition.
    
    Accepts: audio file (WAV, MP3, FLAC) via multipart form data.
    Returns: transcribed text.
    """
    if 'audio' not in request.files:
        return jsonify({'success': False, 'message': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    # Save uploaded audio temporarily
    upload_dir = current_app.config.get('SPEECH_UPLOAD_FOLDER', 'uploads/audio')
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"{uuid.uuid4().hex}_{audio_file.filename}"
    filepath = os.path.join(upload_dir, filename)
    audio_file.save(filepath)
    
    try:
        transcribed_text = speech_service.recognize_speech(filepath)
        
        # Clean up temp file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': True,
            'text': transcribed_text,
        }), 200
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'success': False, 'message': f'Speech recognition failed: {str(e)}'}), 500


@speech_bp.route('/synthesize', methods=['POST'])
@jwt_required()
def text_to_speech():
    """
    Convert text to speech audio file.
    
    Accepts: JSON with 'text' field and optional 'language' field.
    Returns: audio file path or streams the audio.
    """
    data = request.get_json()
    
    text = data.get('text', '')
    language = data.get('language', 'en')
    
    if not text:
        return jsonify({'success': False, 'message': 'text is required'}), 400
    
    if len(text) > 5000:
        return jsonify({'success': False, 'message': 'Text too long. Max 5000 characters.'}), 400
    
    try:
        output_dir = current_app.config.get('TTS_OUTPUT_FOLDER', 'static/audio')
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = f"tts_{uuid.uuid4().hex}.mp3"
        output_path = os.path.join(output_dir, output_filename)
        
        speech_service.synthesize_speech(text, output_path, language)
        
        return jsonify({
            'success': True,
            'audio_url': f'/static/audio/{output_filename}',
            'message': 'Speech synthesized successfully',
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Text-to-speech failed: {str(e)}'}), 500


@speech_bp.route('/voice-search', methods=['POST'])
@jwt_required()
def voice_search():
    """
    Search for jobs using voice input.
    Records audio → transcribes → searches jobs.
    """
    if 'audio' not in request.files:
        return jsonify({'success': False, 'message': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    # Save and transcribe
    upload_dir = current_app.config.get('SPEECH_UPLOAD_FOLDER', 'uploads/audio')
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"{uuid.uuid4().hex}_{audio_file.filename}"
    filepath = os.path.join(upload_dir, filename)
    audio_file.save(filepath)
    
    try:
        # Step 1: Transcribe voice to text
        search_query = speech_service.recognize_speech(filepath)
        
        # Step 2: Search jobs with transcribed text
        from app.models.job import Job
        from app.extensions import db
        
        jobs = Job.query.filter(
            Job.status == 'active',
            db.or_(
                Job.title.ilike(f'%{search_query}%'),
                Job.description.ilike(f'%{search_query}%'),
                Job.required_skills.ilike(f'%{search_query}%'),
            )
        ).limit(20).all()
        
        # Clean up temp file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': True,
            'transcribed_query': search_query,
            'jobs': [job.to_dict() for job in jobs],
            'total': len(jobs),
        }), 200
        
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'success': False, 'message': f'Voice search failed: {str(e)}'}), 500


@speech_bp.route('/voice-command', methods=['POST'])
@jwt_required()
def voice_command():
    """
    Process a voice command (e.g., 'show my applications', 'find Python jobs').
    Transcribes audio and interprets the command using AI.
    """
    if 'audio' not in request.files:
        return jsonify({'success': False, 'message': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    upload_dir = current_app.config.get('SPEECH_UPLOAD_FOLDER', 'uploads/audio')
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"{uuid.uuid4().hex}_{audio_file.filename}"
    filepath = os.path.join(upload_dir, filename)
    audio_file.save(filepath)
    
    try:
        command_text = speech_service.recognize_speech(filepath)
        
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Parse the command
        parsed = speech_service.parse_voice_command(command_text)
        
        return jsonify({
            'success': True,
            'transcribed_text': command_text,
            'parsed_command': parsed,
        }), 200
        
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'success': False, 'message': f'Voice command failed: {str(e)}'}), 500
