from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import *
from . import *
import json
from datetime import datetime, timedelta
from .make_calendar import *

views = Blueprint('views', __name__)

@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    current_month = datetime.now().strftime("%B")

    calendar = Calendar(current_user.id, datetime.now())

    workout_data = WorkoutData.query.filter_by(user_id = current_user.id).all()

    

    if request.method == 'POST':
        note = request.form.get('note')
        if len(note) < 1:
            flash('Note is too short', category = 'error')
        else:
            new_note = Note(data = note, user_id = current_user.id, date = datetime.now())
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category = 'success')
    return render_template("home.html", user = current_user, month = current_month, calendar = calendar)

@views.route('/delete-note', methods = ['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

def get_current_month_data(workout_data, calendar):
    return [wd for wd in workout_data if wd.date.month == calendar.dt.month]

def add_workouts_to_dates(workout_data, calendar):

    workout_dict = {} # Keys: num. day of the month, Values: Name of workout

    for w in workout_data:
        if w.date.month == calendar.dt.month:
            workout_dict[w.date.day] = w.workout_name

    return workout_dict

