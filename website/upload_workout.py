from flask import Blueprint, render_template, request, flash, send_file
from flask_login import login_required, current_user
from .models import Note
import json
from datetime import datetime
from .models import *
import pandas as pd
from io import BytesIO
import numpy as np
from .create_default_split import *
from .views import *

upload_workout = Blueprint('upload_workout', __name__)

class StoredWorkout:

    def __init__(self) -> None:
        self.workout = None
    
    def setWorkout(self, w):
        self.workout = w

    def getStoredWorkout(self):
        return self.workout

swkrt = StoredWorkout()

@upload_workout.route('/upload-workout', methods=['GET', 'POST'])
@login_required
def upload():
    if not swkrt.getStoredWorkout():
        swkrt.setWorkout(current_user.get_active_split().get_curr_workout())
    if request.method == 'POST':
        print(swkrt.getStoredWorkout())
        print('hello')
        try:
            current_workout = swkrt.getStoredWorkout()
            print(current_workout)
        except:
            flash('No workout is currently active.', category='error')
            return render_template("upload_workout.html", user=current_user)

        print(current_workout)
        # Collect form data
        workout_data = []
        for m_index, movement in enumerate(current_workout.movements):
            for s_index in range(movement.sets):
                weight_key = f"weight-{m_index}-{s_index}"
                reps_key = f"reps-{m_index}-{s_index}"
                weight = request.form.get(weight_key)
                reps = request.form.get(reps_key)

                if weight and reps:  # Check if the fields are not empty
                    workout_data.append({
                        'movement': movement.mov_name,
                        'weight': weight,
                        'reps': reps,
                        'set': s_index + 1
                    })
        
        user_workout_notes = request.form.get("workoutNotes")

        # Perform data validation and saving
        if any(not data['weight'].isdigit() or not data['reps'].isdigit() for data in workout_data):
            flash('Weight and reps must be numeric values.', category='error')
        elif not workout_data:
            flash('Please enter valid workout data.', category='error')
        elif datetime.now() < get_all_day().day_time:
            flash('Cannot store workout data in the future! Please select a different day.', category='error')
        else:
        # Upload workout data:
            for data in workout_data:
                new_data = WorkoutData(
                    workout_id=current_workout.id,
                    date=get_all_day().day_time,
                    movement_name=data['movement'],
                    weight=int(data['weight']),
                    reps=int(data['reps']),
                    set_number=data['set'],
                    user_id=current_user.id,
                    session_id = 0

                )
                db.session.add(new_data)
            new_note = Note(
                workout_id = current_workout.id,
                date = get_all_day().day_time,
                data = user_workout_notes,
                user_id = current_user.id
            )
            db.session.add(new_note)
            db.session.commit()
            flash('Upload Successful! Nice Workout!', category='success')

            # Update workout in split if uploaded workout matches the next workout in the split:
            if (swkrt.getStoredWorkout() == current_user.get_active_split().get_curr_workout()):
                current_user.get_active_split().move_to_next_workout()
        
    
    return render_template("upload_workout.html", user=current_user, wrkt=swkrt.getStoredWorkout())

@upload_workout.route('/download-template', methods=['GET', 'POST'])
@login_required
def download_template():
    workout_name = request.form.get('workout_name')
    workout = Workout.query.filter_by(workout_name = workout_name, user_id = current_user.id).first()
    swkrt.workout = workout
    print(swkrt.getStoredWorkout())
    return render_template("upload_workout.html", user=current_user, wrkt= swkrt.getStoredWorkout())