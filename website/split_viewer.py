from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import Note
import json
from datetime import datetime
from .models import *

split_viewer = Blueprint('split_viewer', __name__)

@split_viewer.route('/split-viewer', methods=['GET', 'POST'])
@login_required
def editor():
    if request.method == 'POST':

        if 'split_name' in request.form:
            split_name = request.form.get('split_name')

            if Split.query.filter_by(split_name=split_name, user_id=current_user.id).first():
                flash('Split name already exists. Please choose another one!', category='error')
            else:
                workout_ids = []
                for i in range(1, len(request.form)):
                    workout_name = request.form.get('workout' + str(i))
                    workout = Workout.query.filter_by(workout_name=workout_name, user_id=current_user.id).first()
                    if workout:
                        workout_ids.append(workout.id)

                new_split = Split(split_name=split_name, is_active=False, user_id=current_user.id, next_workout_ind = 0)
                db.session.add(new_split)
                db.session.commit()

                # Associate workouts with the new split
                for workout_id in workout_ids:
                    new_split.workouts.append(Workout.query.get(workout_id))

                new_split.order = workout_ids
                print(new_split.get_curr_workout())

                db.session.commit()
                flash('Split created!', category='success')
                
        elif 'selectedSplit' in request.form:
            selected_split_id = request.form.get('selectedSplit')
            if selected_split_id:
                # Set all splits to inactive first
                Split.query.filter_by(user_id=current_user.id).update({'is_active': False})
                # Set the selected split to active
                selected_split = Split.query.get(selected_split_id)
                if selected_split and selected_split.user_id == current_user.id:
                    selected_split.is_active = True
                    db.session.commit()
                    flash(f'Set {selected_split.split_name} as active split!', category='success')
                else:
                    flash('Invalid split selected', category='error')

    return render_template("split_viewer.html", user=current_user)
