from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, current_app
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required, current_user
from .models import *
from . import *
import json
from datetime import datetime, timedelta
from .make_calendar import *

class CurrentDay:

    all_days = []

    def __init__(self):
        self.day_time = datetime.now()
        CurrentDay.all_day = self
        if len(CurrentDay.all_days) == 0:
            CurrentDay.all_days.append(self)
        else:
            CurrentDay.all_days[0] = self
    
    def get_day(self):
        return self.day_time
    
class SelectedWorkoutData:

    def __init__(self):
        self.workout_name = None
        self.workout_data = None
    
    def set_data(self, data, name):
        self.workout_name = name
        self.workout_data = data
    
    def get_workout_data(self):
        return self.workout_data

    def get_workout_name(self):
        return self.workout_name
    
    def is_stored(self):
        if self.workout_data == None:
            return True
        return False

views = Blueprint('views', __name__)
current_day = CurrentDay()
stored_data = SelectedWorkoutData()

@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    calendar = Calendar(current_user.id, current_day.get_day())
    workout_data = WorkoutData.query.filter_by(user_id = current_user.id).all()
    workout_dict = add_workouts_to_dates(workout_data, calendar)
    workout_data = WorkoutData.query.filter_by(user_id=current_user.id).order_by(WorkoutData.date.asc()).all()

    current_view_workout = current_user.get_active_split().get_curr_workout()
    movement_view_name = current_view_workout.movements[0].mov_name

    if request.method == 'POST':
        workout_name = request.form.get('changeWorkout')
        if workout_name:
            current_view_workout = Workout.query.filter_by(user_id = current_user.id, workout_name = workout_name).first()
        movement_name = request.form.get('changeMovement')
        if movement_name:
            movement_view_name = movement_name

    filtered_data = filter_workouts(workout_data, current_view_workout)
    movement_data = WorkoutData.query.filter_by(user_id=current_user.id, movement_name = movement_view_name).order_by(WorkoutData.date.asc()).all()
    volume_by_date = calculate_volume(filtered_data)
    volume_by_date_movement = calculate_volume(movement_data)

    assert isinstance(volume_by_date, dict), "volume_by_date must be a dictionary"

    current_day_display_dt = get_all_day().day_time
    current_day_display = f'{current_day_display_dt.month}/{current_day_display_dt.day}/{current_day_display_dt.year}'
    print(current_day_display)
    if stored_data.is_stored():
        workout_data = current_user.get_last_workout_data(user_id=current_user.id)
        print(workout_data)
        if current_user.get_last_workout():
            workout_display_name = current_user.get_last_workout().workout_name
        else:
            workout_display_name = ""
    else:
        workout_data = stored_data.get_workout_data()
        workout_display_name = stored_data.get_workout_name()

    return render_template("home.html", 
                           user = current_user,
                           calendar = calendar, 
                           workout_dict = workout_dict, 
                           volume_data=volume_by_date, 
                           movement_volume_data = volume_by_date_movement,
                           current_view_workout = current_view_workout,
                           current_day = current_day_display_dt, 
                           workout_data = workout_data,
                           workout_display_name = workout_display_name,
                           movement_names = current_user.get_all_movements(),
                           movement_view_name = movement_view_name)

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
        
        # Convert to Data class format
        labels = sorted(volume_by_date.keys())
        values = [volume_by_date[date] for date in labels]
        processed_data[movement] = {'name': movement, 'labels': labels, 'values': values}
                
    return processed_data

def filter_workouts(workout_data, workout):
    filtered_data = []
    movement_names = [mov.mov_name for mov in workout.movements]
    for w in workout_data:
        if Workout.query.filter_by(id = w.workout_id).first().id == workout.id or w.movement_name in movement_names:
            filtered_data.append(w)
    return filtered_data

def filter_by_movement(workout_data, movement_name):
    return None

@views.route('/update-workout', methods=['GET', 'POST'])
@login_required
def update_selected_workout():
    date_string = request.form['date']
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    date = datetime.strptime(date_string, date_format)

    workout_name = request.form['workout']
    index = int(request.form['index'])

    workout_data = get_workout_date_from_index(current_user.id, index, date)
    stored_data.set_data(workout_data, workout_name)
    return redirect(url_for('views.home'))

@login_required
def get_workout_date_from_index(user_id, index, date):
        query = WorkoutData.query.filter_by(user_id=user_id).filter(
            extract('year', WorkoutData.date) == date.year,
            extract('month', WorkoutData.date) == date.month,
            extract('day', WorkoutData.date) == date.day
        ).order_by(desc(WorkoutData.movement_name)).all()
        if not query:
            return None
        dates = [q.date for q in query]
        ordered_dates = list(dict.fromkeys(dates))

        # Ensure that index exists within ordered_dates
        assert(index < len(ordered_dates))
        return current_user.get_workout_from_id_date(ordered_dates[index])

@views.route('/increase-day', methods=['GET', 'POST'])
@login_required    
def increase_day():
    date = get_all_day()
    date.day_time = date.day_time + timedelta(days= 1)
    return redirect(url_for('views.home'))

@views.route('/decrease-day', methods=['GET', 'POST'])
@login_required 
def decrease_day():
    date = get_all_day()
    date.day_time = date.day_time - timedelta(days = 1)
    return redirect(url_for('views.home'))

@views.route('/increase-month', methods=['GET', 'POST'])
@login_required 
def increase_month():
    date = get_all_day()
    date.day_time = get_next_month(date.day_time)
    return redirect(url_for('views.home'))

@views.route('/decrease-month', methods=['GET', 'POST'])
@login_required 
def decrease_month():
    date = get_all_day()
    date.day_time = get_prev_month(date.day_time)
    return redirect(url_for('views.home'))

def get_all_day():
    return CurrentDay.all_days[0]

def get_prev_month(date):
    init_date = date
    while(init_date.month == date.month):
        date = date - timedelta(days = 1)
    if date.day < init_date.day:
        return date
    while(init_date.day != date.day):
        date = date - timedelta(days = 1)
    return date

def get_next_month(date):
    init_date = date
    while(init_date.month == date.month):
        date = date + timedelta(days = 1)
    while(init_date.day != date.day):
        if ((date + timedelta(days = 1)).month > date.month):
            return date
        date = date + timedelta(days = 1)
    return date