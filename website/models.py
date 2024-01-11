from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

split_workout = db.Table('split_workout',
    db.Column('split_id', db.Integer, db.ForeignKey('split.id'), primary_key=True),
    db.Column('workout_id', db.Integer, db.ForeignKey('workout.id'), primary_key=True)
)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key = True)
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

class Movement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

    def get_workout_list(self):
        return [w for w in self.workouts]
    
    def get_curent_workout(self, update):
        current_workout = self.get_workout_list()[self.next_workout_ind]
        if update:
            if self.next_workout_ind < len(self.get_workout_list()):
                self.next_workout_ind += 1
            else:
                self.next_workout_ind = 0
        return current_workout

class WorkoutData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_name = db.Column(db.String(100))
    movement_name = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone = True), default = func.now)
    weight = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    set_number = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

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