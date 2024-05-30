from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
import json
from datetime import datetime
from .models import *

workouts = Blueprint('workouts', __name__)

@workouts.route('/splits', methods = ['GET', 'POST'])
@login_required
def splits():
    if request.method == 'POST':
        workout_name = request.form.get('workout_name')
        num_movements = bool_int_check(request.form.get('num_movements'))
        existing_workout = Workout.query.filter_by(workout_name=workout_name, user_id = current_user.id).first()

        if not workout_name:
            flash('Please enter a workout name.', category = 'error')
        elif existing_workout:
            flash('Workout already exists. Choose a different name!', category = 'error')
            # return render_template("splits.html", user = current_user)
        elif num_movements:
            new_workout = Workout(workout_name = workout_name, num_movements = num_movements, movements = [], user_id = current_user.id)
            mov_names, num_sets, num_reps = [], [], []
            for i in range(num_movements):
                mov_names.append(request.form.get(f'movement_name{i}'))
                num_sets.append(request.form.get(f'num_sets_mvmnt{i}'))
                num_reps.append(request.form.get(f'num_reps_mvmnt{i}'))
            
            if not all([len(name) for name in mov_names]):
                flash('Make sure all name entries are filled', category = 'error')
            elif (not all([bool_int_check(el) for el in num_sets])) and (not all([bool_int_check(el)  for el in num_reps])):
                flash('Make sure all sets & reps are valid', category = 'error')
            else:
                movements = []
                for i in range(num_movements):
                    new_mov = Movement(mov_name = mov_names[i], reps = num_reps[i], sets = num_sets[i], workout_id = new_workout.id, user_id = current_user.id)
                    movements.append(new_mov)
                    db.session.add(new_mov)
                new_workout.movements = movements
                db.session.add(new_workout)
                db.session.commit()
            flash('Workout created!', category='success')
        else:
            flash('Invalid number of movements.', category = 'error')

    return render_template("splits.html", user = current_user,
                                          movement_names = current_user.get_all_movements())

@workouts.route('/add-movement', methods=['GET', 'POST'])
@login_required
def add_movement():
    mov_name = request.form['new_mov']
    if not Movement.query.filter_by(user_id = current_user.id, mov_name = mov_name, reps = 0, sets = 0, workout_id = -1).all():
        new_mov = Movement(user_id = current_user.id,
                        mov_name = mov_name, 
                        reps = 0,
                        sets = 0,
                        workout_id = -1)
        db.session.add(new_mov)
        db.session.commit()
        flash('Movement added!', category='success')
    else:
        flash('Movement already exists.', category='error')
    return redirect(url_for('workouts.splits'))

def bool_int_check(str_input):
    try:
        output = int(str_input)
        if output > 0:
            return output
        else:
            return False
    except:
        return False
    