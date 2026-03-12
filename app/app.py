import os
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, redirect, url_for, flash

# ------------------------
# Flask app setup
# ------------------------
APP_VERSION = "1.0.0"

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for flashing messages

# ------------------------
# Firestore initialization (Cloud Run only)
# ------------------------
try:
    # Use Application Default Credentials (provided automatically in Cloud Run)
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firestore initialized successfully!")
except Exception as e:
    print(f"Error initializing Firestore: {e}")
    db = None

# ------------------------
# Routes
# ------------------------

@app.route('/')
def index():
    notes = []
    if db:
        try:
            notes_ref = db.collection('notes').order_by(
                'timestamp', direction=firestore.Query.DESCENDING
            ).stream()
            for doc in notes_ref:
                note = doc.to_dict()
                note['id'] = doc.id
                notes.append(note)
        except Exception as e:
            flash(f"Error fetching notes: {e}", "error")
            print(f"Error fetching notes: {e}")
    else:
        flash("Firestore is not initialized. Cannot fetch notes.", "error")
    return render_template('index.html', notes=notes, app_version=APP_VERSION)


@app.route('/add', methods=['POST'])
def add_note():
    if db:
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            try:
                db.collection('notes').add({
                    'title': title,
                    'content': content,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                flash("Note added successfully!", "success")
            except Exception as e:
                flash(f"Error adding note: {e}", "error")
                print(f"Error adding note: {e}")
        else:
            flash("Title and content cannot be empty.", "error")
    else:
        flash("Firestore is not initialized. Cannot add note.", "error")
    return redirect(url_for('index'))


@app.route('/edit/<note_id>')
def edit_note_form(note_id):
    note = None
    if db:
        try:
            note_ref = db.collection('notes').document(note_id).get()
            if note_ref.exists:
                note = note_ref.to_dict()
                note['id'] = note_ref.id
            else:
                flash("Note not found.", "error")
        except Exception as e:
            flash(f"Error fetching note for editing: {e}", "error")
            print(f"Error fetching note for editing: {e}")
    else:
        flash("Firestore is not initialized. Cannot edit note.", "error")
    return render_template('edit.html', note=note, app_version=APP_VERSION)


@app.route('/update/<note_id>', methods=['POST'])
def update_note(note_id):
    if db:
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            try:
                db.collection('notes').document(note_id).update({
                    'title': title,
                    'content': content,
                })
                flash("Note updated successfully!", "success")
            except Exception as e:
                flash(f"Error updating note: {e}", "error")
                print(f"Error updating note: {e}")
        else:
            flash("Title and content cannot be empty.", "error")
    else:
        flash("Firestore is not initialized. Cannot update note.", "error")
    return redirect(url_for('index'))


@app.route('/delete/<note_id>', methods=['POST'])
def delete_note(note_id):
    if db:
        try:
            db.collection('notes').document(note_id).delete()
            flash("Note deleted successfully!", "success")
        except Exception as e:
            flash(f"Error deleting note: {e}", "error")
            print(f"Error deleting note: {e}")
    else:
        flash("Firestore is not initialized. Cannot delete note.", "error")
    return redirect(url_for('index'))


# ------------------------
# Entry point
# ------------------------
if __name__ == "__main__":
    # Cloud Run sets PORT automatically
    port = int(os.environ.get("PORT", 8080))
    
    # Start Flask server
    app.run(host="0.0.0.0", port=port)