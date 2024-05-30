from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import JSON
from sqlalchemy import extract, desc, asc
from flask_login import login_required, current_user
from collections import OrderedDict


split_workout = db.Table('split_workout',
    db.Column('split_id', db.Integer, db.ForeignKey('split.id'), primary_key=True),
    db.Column('workout_id', db.Integer, db.ForeignKey('workout.id'), primary_key=True)
)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    workout_id = db.Column(db.Integer)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone = True), default = func.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_name = db.Column(db.String(10000))
    num_movements = db.Column(db.Integer)
    movements = db.relationship('Movement', backref='workout', lazy=True)
    splits = db.relationship('Split', secondary=split_workout, backref=db.backref('workouts', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  

    def __repr__(self) -> str:
        return f"Workout: {self.workout_name}, Workout ID: {self.id}"

class Movement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    mov_name = db.Column(db.String(100))
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))

class Split(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    split_name = db.Column(db.String(10000))
    is_active = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    next_workout_ind = db.Column(db.Integer)
    order = db.Column(JSON)

    def get_workouts(self):
        return [Workout.query.filter_by(id = self.order[i]).first() for i in range(len(self.order))]
    
    def get_curr_workout(self):
        return Workout.query.filter_by(id = self.order[0]).first()
    
    def move_to_next_workout(self):
        print("Old Order: " + str(self.order))
        old_order = self.order.copy()
        new_order = old_order[1:] + [old_order[0]]
        self.order = new_order
        print("Updated:" + str(self.order))

class WorkoutData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer)
    movement_name = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone = True), default = func.now)
    weight = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    set_number = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session_id = db.Column(db.Integer)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    workouts = db.relationship('Workout')
    splits = db.relationship('Split')

    def get_active_split(self):
        for split in self.splits:
            if split.is_active:
                return split
        return None
    
    def process_workout_data(self, data):
        workout_data = {}
        for d in data:
            if d.movement_name in workout_data:
                workout_data[d.movement_name].append(d)
            else:
                workout_data[d.movement_name] = [d]
        return workout_data
    
    def get_last_workout_data(self, user_id):
        last_workout_data = WorkoutData.query.filter_by(user_id = user_id).order_by(desc(WorkoutData.date), desc(WorkoutData.movement_name)).first()
        if not last_workout_data:
            return
        last_date = last_workout_data.date
        query = WorkoutData.query.filter_by(user_id = user_id, date = last_date).all()
        notes = Note.query.filter_by(user_id = self.id, date = last_date).first().data
        return self.process_workout_data(query), notes
    
    def get_last_workout(self):
        if not WorkoutData.query.filter_by(user_id = self.id).order_by(desc(WorkoutData.date)).first():
            return {}
        last_workout_id = WorkoutData.query.filter_by(user_id = self.id).order_by(desc(WorkoutData.date)).first().workout_id
        last_workout = Workout.query.filter_by(user_id = self.id, id = last_workout_id).first()
        return last_workout
    
    def get_workout_from_id_date(self, date):
        query = WorkoutData.query.filter_by(user_id = self.id, date = date).order_by(desc(WorkoutData.movement_name)).all()
        return self.process_workout_data(query)
    
    def get_all_movements(self):
        movs = Movement.query.filter_by(user_id = self.id).order_by(asc(Movement.mov_name)).distinct().all()
        mov_names = [m.mov_name for m in movs]
        return list(OrderedDict.fromkeys(mov_names))
