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

upload_workout = Blueprint('upload_workout', __name__)

class StoredWorkout:

    def __init__(self) -> None:
        pass
    
    def setWorkout(self, w):
        self.workout = w

    def getStoredWorkout(self):
        return self.workout

swkrt = StoredWorkout()

@upload_workout.route('/upload-workout', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'userUploadedWorkoutData' not in request.files:
            flash('No file uploaded.', category='error')
            return render_template("upload_workout.html", user=current_user)

        # Testing file type:
        if request.files['userUploadedWorkoutData'].filename[-4:] != '.csv':
            flash('Wrong file type. Please resubmit file.', category='error')
            return render_template("upload_workout.html", user=current_user)

        workout_data = pd.read_csv(request.files['userUploadedWorkoutData'])
        current_workout = swkrt.getStoredWorkout()
        # current_workout = current_user.get_active_split().get_curr_workout()
        current_user.get_active_split().move_to_next_workout()
        # Testing if User Submitted Data is Correct:
        if not ([el.lower() for el in workout_data.columns.tolist()][1:] == ['movement', 'weight', 'reps', 'set']):
            flash('Wrong Format. Please double check your template formatting.', category='error')
        elif not ([mov.mov_name for mov in current_workout.movements] == workout_data['Movement'].unique().tolist()):
            flash('Wrong Format. Please double check your template formatting.', category='error')
        else:
            for i in range(len(workout_data)):
                new_data = WorkoutData(
                    workout_id = current_workout.id,
                    date = datetime.now(),
                    movement_name = workout_data.loc[i]['Movement'],
                    weight = workout_data.loc[i]['Weight'].item(),
                    reps = workout_data.loc[i]['Reps'].item(),
                    set_number = workout_data.loc[i]['Set'].item(),
                    user_id = current_user.id
                )

                db.session.add(new_data)
                db.session.commit()
            flash('Upload Successful! Nice Workout!', category='success')
            
    return render_template("upload_workout.html", user=current_user)

@upload_workout.route('/download-template', methods=['GET', 'POST'])
@login_required
def download_template():
    
    workout_name = request.form.get('workout_name')
    workout = Workout.query.filter_by(workout_name = workout_name, user_id = current_user.id).first()
    swkrt.workout = workout

    template = pd.DataFrame(columns = ['Movement', 'Weight', 'Reps', 'Set'])
    count = 0
    for movement in workout.movements:
        for i in range(1, movement.sets + 1):
            template.loc[count] = [movement.mov_name, 0, 0, i]
            count += 1
    template_export = template.to_csv()

    buffer = BytesIO()
    buffer.write(template_export.encode())
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='template.csv', mimetype='text/csv')