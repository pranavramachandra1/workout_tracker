from datetime import datetime, timedelta


calendar_dict = {"Sunday": 0,
                "Monday": 1,
                "Tuesday": 2,
                "Wednesday": 3,
                "Thursday": 4,
                "Friday": 5,
                "Saturday": 6
                }

def get_first_day_of_the_month(dt):
    orig_dt = dt
    while dt.month == orig_dt.month:
        dt = dt - timedelta(days = 1)
    return dt + timedelta(days = 1)

def generate_week(dt_list, dt):
    orig_dt = dt
    if dt_list == []:
        dt = dt + timedelta(days = 1)
        while len(dt_list) < 7 and dt.month == orig_dt.month:
            dt_list.append(Day(dt = dt, completed_workouts=[]))
            dt = dt + timedelta(days = 1)
    else:
        while (dt.strftime("%A") != 'Sunday' or dt_list == []) and dt.month == orig_dt.month:
            dt_list.append(Day(dt = dt, completed_workouts= []))
            dt = dt + timedelta(days = 1)
    return dt_list, dt_list[-1].dt

def generate_calendar(dt):
    calendar, orig_dt = [], dt
    current_day = get_first_day_of_the_month(dt)
    first_week = [None for d in range(calendar_dict[current_day.strftime("%A")])]
    first_week, current_day = generate_week(first_week, current_day)
    calendar.append(first_week)

    while (current_day + timedelta(days = 1)).month == orig_dt.month:
        new_week, current_day = generate_week([], current_day)
        while len(new_week) < 7:
            new_week.append(None)
        calendar.append(new_week)

    return calendar

class Calendar:

    def __init__(self, user_id, dt) -> None:
        self.dt = dt
        self.user_id = user_id
        self.calendar = generate_calendar(dt = dt)
    
    def __repr__(self):
        return f'{self.calendar}'

class Day:
    def __init__(self, completed_workouts, dt) -> None:
        self.dt = dt
        self.completed_workouts = completed_workouts
    
    def __repr__(self) -> str:
        return f'{self.dt.strftime("%A")}, {self.dt.month} {self.dt.day}'