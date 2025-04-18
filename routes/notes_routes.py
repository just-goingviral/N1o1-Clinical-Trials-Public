"""
Clinical notes routes for Nitrite Dynamics application
Allows doctors to create, view, and manage notes with text and voice capabilities
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
import datetime
import traceback
from models import db, ClinicalNote, Patient, Simulation
from utils.logger import get_module_logger, log_exception

# Configure logger
logger = get_module_logger('notes_routes')

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')

# Helper functions
def allowed_audio_file(filename):
    """Check if uploaded file is an allowed audio format"""
    allowed_extensions = {'mp3', 'wav', 'ogg', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_voice_recording(file):
    """Save voice recording to disk and return filepath"""
    if file and allowed_audio_file(file.filename):
        # Generate a unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        # Save file
        file_path = os.path.join('static', 'voice_recordings', unique_filename)
        file.save(file_path)
        return unique_filename
    return None

@notes_bp.route('/')
@login_required
def list_notes():
    """List user's clinical notes"""
    notes = ClinicalNote.query.filter_by(user_id=current_user.id).order_by(ClinicalNote.created_at.desc()).all()
    return render_template('notes/list.html', notes=notes, title="Clinical Notes")

@notes_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_note():
    """Create a new clinical note"""
    patients = Patient.query.all()
    simulations = Simulation.query.all()
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        text_content = request.form.get('text_content')
        patient_id = request.form.get('patient_id')
        simulation_id = request.form.get('simulation_id')
        is_private = request.form.get('is_private') == 'on'
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        if not title:
            flash('Title is required', 'danger')
            return redirect(url_for('notes.new_note'))
        
        # Handle voice recording if provided
        voice_recording_path = None
        if 'voice_recording' in request.files:
            voice_file = request.files['voice_recording']
            if voice_file.filename:
                voice_recording_path = save_voice_recording(voice_file)
        
        # Create new note
        note = ClinicalNote(
            user_id=current_user.id,
            title=title,
            text_content=text_content,
            patient_id=patient_id if patient_id else None,
            simulation_id=simulation_id if simulation_id else None,
            voice_recording_path=voice_recording_path,
            is_private=is_private,
            tags=tags
        )
        
        db.session.add(note)
        db.session.commit()
        
        flash('Note created successfully', 'success')
        return redirect(url_for('notes.view_note', note_id=note.id))
    
    return render_template('notes/new.html', 
                          patients=patients, 
                          simulations=simulations,
                          title="New Clinical Note")

@notes_bp.route('/<int:note_id>')
@login_required
def view_note(note_id):
    """View a clinical note"""
    note = ClinicalNote.query.get_or_404(note_id)
    
    # Check if user has permission to view the note
    if note.user_id != current_user.id and note.is_private:
        flash('You do not have permission to view this note', 'danger')
        return redirect(url_for('notes.list_notes'))
    
    return render_template('notes/view.html', note=note, title=note.title)

@notes_bp.route('/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    """Edit a clinical note"""
    note = ClinicalNote.query.get_or_404(note_id)
    
    # Check if user has permission to edit the note
    if note.user_id != current_user.id:
        flash('You do not have permission to edit this note', 'danger')
        return redirect(url_for('notes.list_notes'))
    
    patients = Patient.query.all()
    simulations = Simulation.query.all()
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        text_content = request.form.get('text_content')
        patient_id = request.form.get('patient_id')
        simulation_id = request.form.get('simulation_id')
        is_private = request.form.get('is_private') == 'on'
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        if not title:
            flash('Title is required', 'danger')
            return redirect(url_for('notes.edit_note', note_id=note.id))
        
        # Handle voice recording if provided
        if 'voice_recording' in request.files:
            voice_file = request.files['voice_recording']
            if voice_file.filename:
                # Delete old voice recording if exists
                if note.voice_recording_path:
                    old_path = os.path.join('static', 'voice_recordings', note.voice_recording_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                voice_recording_path = save_voice_recording(voice_file)
                note.voice_recording_path = voice_recording_path
        
        # Update note
        note.title = title
        note.text_content = text_content
        note.patient_id = patient_id if patient_id else None
        note.simulation_id = simulation_id if simulation_id else None
        note.is_private = is_private
        note.tags = tags
        note.updated_at = datetime.datetime.utcnow()
        
        db.session.commit()
        
        flash('Note updated successfully', 'success')
        return redirect(url_for('notes.view_note', note_id=note.id))
    
    # Convert tags list to comma-separated string for form
    tags_string = ', '.join(note.tags) if note.tags else ''
    
    return render_template('notes/edit.html', 
                          note=note, 
                          patients=patients, 
                          simulations=simulations,
                          tags_string=tags_string,
                          title="Edit Clinical Note")

@notes_bp.route('/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    """Delete a clinical note"""
    note = ClinicalNote.query.get_or_404(note_id)
    
    # Check if user has permission to delete the note
    if note.user_id != current_user.id:
        flash('You do not have permission to delete this note', 'danger')
        return redirect(url_for('notes.list_notes'))
    
    # Delete voice recording if exists
    if note.voice_recording_path:
        file_path = os.path.join('static', 'voice_recordings', note.voice_recording_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(note)
    db.session.commit()
    
    flash('Note deleted successfully', 'success')
    return redirect(url_for('notes.list_notes'))

@notes_bp.route('/api/transcribe', methods=['POST'])
@login_required
def transcribe_audio():
    """Transcribe audio recording using OPENAI API"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    if not audio_file.filename:
        return jsonify({'error': 'No audio file selected'}), 400
    
    if not allowed_audio_file(audio_file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Save audio file temporarily
    temp_filename = f"temp_{uuid.uuid4()}.{audio_file.filename.rsplit('.', 1)[1].lower()}"
    temp_path = os.path.join('static', 'voice_recordings', temp_filename)
    audio_file.save(temp_path)
    
    try:
        from openai import OpenAI
        
        # Initialize OpenAI client
        client = OpenAI()
        
        # Transcribe audio
        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Delete temporary file
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'transcript': transcript.text
        })
        
    except Exception as e:
        # Delete temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'error': f'Transcription failed: {str(e)}'
        }), 500