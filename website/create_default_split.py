from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import Note
import json
from datetime import datetime
from .models import *
from .workouts import *

def create_default_split():

    # Create Workouts:
    wrkts = [
        {'name': 'Push Day',
         'num_movements': 3,
         'movements': [
            {'mov_name': 'Barbell Bench Press',
              'reps': 5,
              'sets': 5},
            {'mov_name': 'Shoulder Press',
              'reps': 8,
              'sets': 4},
            {'mov_name': 'Tricep Extensions',
              'reps': 10,
              'sets': 3}
         ]},

         {'name': 'Pull Day',
         'num_movements': 3,
         'movements': [
            {'mov_name': 'Pull-Ups',
              'reps': 5,
              'sets': 5},
            {'mov_name': 'Chest Supported Rows',
              'reps': 8,
              'sets': 4},
            {'mov_name': 'Bicep Curls',
              'reps': 10,
              'sets': 3}
         ]},

         {'name': 'Leg Day',
         'num_movements': 3,
         'movements': [
            {'mov_name': 'Barbell Back Squat',
              'reps': 5,
              'sets': 5},
            {'mov_name': 'Hamstring curls',
              'reps': 8,
              'sets': 4},
            {'mov_name': 'Calf Raises',
              'reps': 10,
              'sets': 3}
         ]}
        ]

    default_split = Split(split_name = "default split", is_active = True, user_id = current_user.id, next_workout_ind = 0)
    db.session.add(default_split)
    db.session.flush()

    workouts = []
    for w in wrkts:
        workout = Workout(workout_name = w['name'], num_movements = w['num_movements'], user_id = current_user.id)
        db.session.flush()
        movements = []
        for m in w['movements']:
            movement = Movement(
                        mov_name = m['mov_name'],
                        reps = m['reps'],
                        sets = m['sets'],
                        workout_id = workout.id,
                        user_id = current_user.id
                    )
            db.session.add(movement)
            movements.append(movement)
        workout.movements = movements
        workouts.append(workout)
        db.session.add(workout)
    default_split.workouts = workouts
    default_split.order = [w.id for w in workouts]
    db.session.commit()
    print('Default Split Created!')
