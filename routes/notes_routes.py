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
    try:
        if not file:
            logger.warning("No file provided to save_voice_recording")
            return None

        if not allowed_audio_file(file.filename):
            logger.warning(f"File type not allowed: {file.filename}")
            return None

        # Generate a unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"

        # Ensure directory exists
        voice_dir = os.path.join('static', 'voice_recordings')
        os.makedirs(voice_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(voice_dir, unique_filename)
        file.save(file_path)
        logger.info(f"Voice recording saved: {unique_filename}")
        return unique_filename
    except Exception as e:
        log_exception(logger, e, "saving voice recording")
        return None

@notes_bp.route('/')
@login_required
def list_notes():
    """List user's clinical notes"""
    try:
        logger.info(f"User {current_user.id} requesting notes list")
        notes = ClinicalNote.query.filter_by(user_id=current_user.id).order_by(ClinicalNote.created_at.desc()).all()
        return render_template('notes/list.html', notes=notes, title="Clinical Notes")
    except Exception as e:
        log_exception(logger, e, "listing notes")
        flash('An error occurred while retrieving your notes', 'danger')
        # Fallback to empty list on error
        return render_template('notes/list.html', notes=[], title="Clinical Notes - Error Loading")

@notes_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_note():
    """Create a new clinical note"""
    try:
        patients = Patient.query.all()
        simulations = Simulation.query.all()

        if request.method == 'POST':
            try:
                # Get form data
                title = request.form.get('title')
                text_content = request.form.get('text_content')
                patient_id = request.form.get('patient_id')
                simulation_id = request.form.get('simulation_id')
                is_private = request.form.get('is_private') == 'on'
                tags = request.form.get('tags', '').split(',')
                tags = [tag.strip() for tag in tags if tag.strip()]

                # Validate input
                if not title:
                    logger.warning(f"New note creation attempt without title by user {current_user.id}")
                    flash('Title is required', 'danger')
                    return redirect(url_for('notes.new_note' _external=True))

                # Handle voice recording if provided
                voice_recording_path = None
                if 'voice_recording' in request.files:
                    voice_file = request.files['voice_recording']
                    if voice_file.filename:
                        logger.info(f"Processing voice recording for new note by user {current_user.id}")
                        voice_recording_path = save_voice_recording(voice_file)
                        if not voice_recording_path:
                            flash('Could not save voice recording. Note created without audio.', 'warning')

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

                # Process file attachments
                attachments = []
                if 'attachments' in request.files:
                    files = request.files.getlist('attachments')
                    for file in files:
                        if file and file.filename:
                            filename = secure_filename(file.filename)
                            unique_filename = f"{uuid.uuid4()}_{filename}"
                            file_type = determine_file_type(filename)
                            storage_dir = os.path.join('static', 'attachments', file_type)
                            os.makedirs(storage_dir, exist_ok=True)
                            file_path = os.path.join(storage_dir, unique_filename)
                            file.save(file_path)
                            attachments.append({
                                'filename': filename,
                                'path': file_path,
                                'type': file_type,
                                'size': os.path.getsize(file_path)
                            })

                if attachments:
                    note.attachment = {
                        'files': attachments,
                        'count': len(attachments)
                    }

                db.session.add(note)
                db.session.commit()

                logger.info(f"Note created successfully by user {current_user.id}, note_id: {note.id}")
                flash('Note created successfully', 'success')
                return redirect(url_for('notes.view_note', note_id=note.id, _external=True))

            except Exception as e:
                db.session.rollback()
                log_exception(logger, e, "creating new note")
                flash(f'Error creating note: {str(e)}', 'danger')
                return redirect(url_for('notes.new_note' _external=True))

        return render_template('notes/new.html', 
                              patients=patients, 
                              simulations=simulations,
                              title="New Clinical Note")

    except Exception as e:
        log_exception(logger, e, "loading note creation page")
        flash('An error occurred while loading the page. Please try again.', 'danger')
        return redirect(url_for('notes.list_notes' _external=True))

@notes_bp.route('/<int:note_id>')
@login_required
def view_note(note_id):
    """View a clinical note"""
    try:
        # Get the note or return 404
        note = ClinicalNote.query.get_or_404(note_id)

        # Check if user has permission to view the note
        if note.user_id != current_user.id and note.is_private:
            logger.warning(f"Unauthorized view attempt for private note {note_id} by user {current_user.id}")
            flash('You do not have permission to view this note', 'danger')
            return redirect(url_for('notes.list_notes' _external=True))

        logger.info(f"Note {note_id} viewed by user {current_user.id}")

        # Get related data
        patient = None
        simulation = None

        try:
            if note.patient_id:
                patient = Patient.query.get(note.patient_id)
            if note.simulation_id:
                simulation = Simulation.query.get(note.simulation_id)
        except Exception as related_error:
            log_exception(logger, related_error, "loading related data for note")
            # Don't block viewing the note if related data can't be loaded
            flash("Some related information couldn't be loaded", "warning")

        return render_template('notes/view.html', 
                            note=note, 
                            patient=patient, 
                            simulation=simulation,
                            title=note.title)

    except Exception as e:
        log_exception(logger, e, f"viewing note {note_id}")
        flash('An error occurred while trying to view the note', 'danger')
        return redirect(url_for('notes.list_notes' _external=True))

@notes_bp.route('/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    """Edit a clinical note"""
    try:
        # Get the note or return 404
        note = ClinicalNote.query.get_or_404(note_id)

        # Check if user has permission to edit the note
        if note.user_id != current_user.id:
            logger.warning(f"Unauthorized edit attempt for note {note_id} by user {current_user.id}")
            flash('You do not have permission to edit this note', 'danger')
            return redirect(url_for('notes.list_notes' _external=True))

        try:
            patients = Patient.query.all()
            simulations = Simulation.query.all()
        except Exception as db_error:
            log_exception(logger, db_error, "loading related data for edit form")
            patients = []
            simulations = []
            flash("Could not load some reference data. Not all options may be available.", "warning")

        if request.method == 'POST':
            try:
                # Get form data
                title = request.form.get('title')
                text_content = request.form.get('text_content')
                patient_id = request.form.get('patient_id')
                simulation_id = request.form.get('simulation_id')
                is_private = request.form.get('is_private') == 'on'
                tags = request.form.get('tags', '').split(',')
                tags = [tag.strip() for tag in tags if tag.strip()]

                # Validate input
                if not title:
                    logger.warning(f"Edit note attempt without title for note {note_id} by user {current_user.id}")
                    flash('Title is required', 'danger')
                    return redirect(url_for('notes.edit_note', note_id=note.id, _external=True))

                # Handle voice recording if provided
                if 'voice_recording' in request.files:
                    voice_file = request.files['voice_recording']
                    if voice_file.filename:
                        logger.info(f"Processing new voice recording for note {note_id}")

                        # Delete old voice recording if exists
                        if note.voice_recording_path:
                            old_path = os.path.join('static', 'voice_recordings', note.voice_recording_path)
                            try:
                                if os.path.exists(old_path):
                                    os.remove(old_path)
                                    logger.info(f"Deleted old voice recording: {note.voice_recording_path}")
                            except Exception as file_error:
                                log_exception(logger, file_error, "deleting old voice recording")

                        # Save new voice recording
                        voice_recording_path = save_voice_recording(voice_file)
                        if voice_recording_path:
                            note.voice_recording_path = voice_recording_path
                        else:
                            flash('Could not save voice recording. Note kept previous recording if any.', 'warning')

                # Update note
                note.title = title
                note.text_content = text_content
                note.patient_id = patient_id if patient_id else None
                note.simulation_id = simulation_id if simulation_id else None
                note.is_private = is_private
                note.tags = tags
                note.updated_at = datetime.datetime.utcnow()

                db.session.commit()

                logger.info(f"Note {note_id} updated successfully by user {current_user.id}")
                flash('Note updated successfully', 'success')
                return redirect(url_for('notes.view_note', note_id=note.id, _external=True))

            except Exception as update_error:
                db.session.rollback()
                log_exception(logger, update_error, f"updating note {note_id}")
                flash(f'Error updating note: {str(update_error)}', 'danger')

                # Reload the note to get original data
                note = ClinicalNote.query.get_or_404(note_id)

        # Convert tags list to comma-separated string for form
        tags_string = ', '.join(note.tags) if note.tags else ''

        return render_template('notes/edit.html', 
                              note=note, 
                              patients=patients, 
                              simulations=simulations,
                              tags_string=tags_string,
                              title="Edit Clinical Note")

    except Exception as e:
        log_exception(logger, e, f"processing edit for note {note_id}")
        flash('An error occurred while editing the note', 'danger')
        return redirect(url_for('notes.list_notes' _external=True))

@notes_bp.route('/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    """Delete a clinical note"""
    try:
        # Get the note or return 404
        note = ClinicalNote.query.get_or_404(note_id)

        # Check if user has permission to delete the note
        if note.user_id != current_user.id:
            logger.warning(f"Unauthorized delete attempt for note {note_id} by user {current_user.id}")
            flash('You do not have permission to delete this note', 'danger')
            return redirect(url_for('notes.list_notes' _external=True))

        # Store information for logging
        note_info = f"note_id={note_id}, title='{note.title}'"
        logger.info(f"Deleting note: {note_info} by user {current_user.id}")

        # Delete voice recording if exists
        if note.voice_recording_path:
            try:
                file_path = os.path.join('static', 'voice_recordings', note.voice_recording_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted voice recording: {note.voice_recording_path}")
                else:
                    logger.warning(f"Voice recording file not found: {file_path}")
            except Exception as file_error:
                # Log but continue with database deletion
                log_exception(logger, file_error, "deleting voice recording file")
                flash("Note deleted but could not remove voice recording file", "warning")

        # Delete from database
        try:
            db.session.delete(note)
            db.session.commit()
            logger.info(f"Successfully deleted note: {note_info}")
            flash('Note deleted successfully', 'success')
        except Exception as db_error:
            db.session.rollback()
            log_exception(logger, db_error, "deleting note from database")
            flash('Error deleting note from database', 'danger')

        return redirect(url_for('notes.list_notes' _external=True))

    except Exception as e:
        log_exception(logger, e, f"processing delete request for note {note_id}")
        flash('An error occurred while deleting the note', 'danger')
        return redirect(url_for('notes.list_notes' _external=True))

@notes_bp.route('/api/transcribe', methods=['POST'])
@login_required
def transcribe_audio():
    """Transcribe audio recording using OPENAI API"""
    temp_path = None

    try:
        # Validate request
        if 'audio' not in request.files:
            logger.warning("Transcription request missing audio file")
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        if not audio_file.filename:
            logger.warning("Transcription request with empty filename")
            return jsonify({'error': 'No audio file selected'}), 400

        if not allowed_audio_file(audio_file.filename):
            logger.warning(f"Transcription request with invalid file type: {audio_file.filename}")
            return jsonify({'error': 'File type not allowed. Supported types: mp3, wav, ogg, webm'}), 400

        # Ensure directory exists
        voice_dir = os.path.join('static', 'voice_recordings')
        os.makedirs(voice_dir, exist_ok=True)

        # Save audio file temporarily
        file_ext = audio_file.filename.rsplit('.', 1)[1].lower()
        temp_filename = f"temp_{uuid.uuid4()}.{file_ext}"
        temp_path = os.path.join(voice_dir, temp_filename)

        logger.info(f"Saving temporary audio file for transcription: {temp_filename}")
        audio_file.save(temp_path)

        # Check for OpenAI API key
        if not os.environ.get('OPENAI_API_KEY'):
            logger.error("OPENAI_API_KEY environment variable not set")
            return jsonify({'error': 'OpenAI API key not configured'}), 500

        from openai import OpenAI

        # Initialize OpenAI client
        client = OpenAI()
        logger.info("Sending audio for transcription")

        # Transcribe audio
        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            temp_path = None

        logger.info("Transcription successful")
        return jsonify({
            'success': True,
            'transcript': transcript.text
        })

    except ModuleNotFoundError:
        logger.error("OpenAI package not installed")
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({
            'error': 'The OpenAI package is not installed. Please install it with pip.'
        }), 500
    except Exception as e:
        # Log the exception with detailed information
        log_exception(logger, e, "transcribing audio")

        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        # Provide appropriate error message based on exception type
        error_message = str(e)
        if "API key" in error_message.lower():
            return jsonify({'error': 'OpenAI API key issue. Please check your API key configuration.'}), 401
        elif "rate limit" in error_message.lower():
            return jsonify({'error': 'OpenAI rate limit exceeded. Please try again later.'}), 429
        else:
            return jsonify({'error': f'Transcription failed: {error_message}'}), 500


def determine_file_type(filename):
    """Determine the file type based on extension"""
    ext = filename.split('.')[-1].lower()

    if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']:
        return 'images'
    elif ext in ['mp4', 'webm', 'mov', 'avi', 'mkv']:
        return 'videos'
    elif ext in ['mp3', 'wav', 'ogg', 'm4a']:
        return 'audio'
    elif ext in ['xlsx', 'xls', 'csv']:
        return 'spreadsheets'
    elif ext in ['pdf', 'doc', 'docx', 'txt', 'rtf']:
        return 'documents'
    else:
        return 'other'