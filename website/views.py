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
    calendar = Calendar(current_user.id, datetime.now())
    workout_data = WorkoutData.query.filter_by(user_id = current_user.id).all()
    workout_dict = add_workouts_to_dates(workout_data, calendar)
    workout_data = WorkoutData.query.filter_by(user_id=current_user.id).order_by(WorkoutData.date.asc()).all()

    current_view_workout = current_user.get_active_split().get_curr_workout()

    if request.method == 'POST':
        workout_name = request.form.get('changeWorkout')
        current_view_workout = Workout.query.filter_by(user_id = current_user.id, workout_name = workout_name).first()

    filtered_data = filter_workouts(workout_data, current_view_workout)
    volume_by_date = calculate_volume(filtered_data)

    print(volume_by_date)

    assert isinstance(volume_by_date, dict), "volume_by_date must be a dictionary"
        
    return render_template("home.html", 
                           user = current_user,
                           calendar = calendar, 
                           workout_dict = workout_dict, 
                           volume_data=volume_by_date)

def get_current_month_data(workout_data, calendar):
    return [wd for wd in workout_data if wd.date.month == calendar.dt.month]

def add_workouts_to_dates(workout_data, calendar):

    workout_dict = {} # Keys: num. day of the month, Values: Name of workout

    for w in workout_data:
        if w.date.month == calendar.dt.month:
            for week in calendar.calendar:
                for day in week:
                    if day and w.date.day == day.dt.day and Workout.query.filter_by(id = w.workout_id).first().workout_name not in day.completed_workouts:
                        day.completed_workouts.append(Workout.query.filter_by(id = w.workout_id).first().workout_name)
            workout_dict[w.date.day] = Workout.query.filter_by(id = w.workout_id).first().workout_name

    return workout_dict

def calculate_volume(workout_data):
    grouped_data = {}
    for data in workout_data:
        # Grouping data by movement name
        if data.movement_name in grouped_data:
            grouped_data[data.movement_name].append(data)
        else:
            grouped_data[data.movement_name] = [data]

    processed_data = {}
    for movement, data_list in grouped_data.items():
        volume_by_date = {}
        count = 0
        for data in data_list:
            # date = data.date.strftime('%Y-%m-%d')
            date = data.date.strftime('%Y-%m-%d %H:%M:%S')
            volume = data.weight * data.reps * data.set_number
            volume_by_date[date] = volume_by_date.get(date, 0) + volume
            count += 1
        
        # print(volume_by_date)
        # Convert to Data class format
        labels = sorted(volume_by_date.keys())
        values = [volume_by_date[date] for date in labels]
        processed_data[movement] = {'name': movement, 'labels': labels, 'values': values}
                
    return processed_data

def filter_workouts(workout_data, workout):
    filtered_data = []
    mov_ids = []
    movement_names = [mov.mov_name for mov in workout.movements]
    for w in workout_data:
        if Workout.query.filter_by(id = w.workout_id).first().id == workout.id or w.movement_name in movement_names:
            filtered_data.append(w)
            if w.movement_name == 'Barbell Bench Press' and w.date.strftime('%Y-%m-%d %H:%M:%S') not in mov_ids:
                mov_ids.append(w.date.strftime('%Y-%m-%d %H:%M:%S'))
    # print(mov_ids)
    return filtered_data
