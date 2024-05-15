from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager

import pymysql.cursors

# # Connect to the database
# connection = pymysql.connect(host='db-mysql-nyc3-82652-do-user-16279925-0.c.db.ondigitalocean.com',
#                              user='doadmin',
#                              password='AVNS_fAJia2yPk9QfAd_pKp3',
#                              database='defaultdb',
#                              cursorclass=pymysql.cursors.DictCursor)

# try:
#     with connection.cursor() as cursor:
#         # Create a new record
#         sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
#         cursor.execute(sql, ('webmaster@example.com', 'very-secret'))

#     # connection is not autocommit by default. So you must commit to save your changes.
#     connection.commit()

#     with connection.cursor() as cursor:
#         # Read a single record
#         sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
#         cursor.execute(sql, ('webmaster@example.com',))
#         result = cursor.fetchone()
#         print(result)
# finally:
#     connection.close()

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'qwertyuiop'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .workouts import workouts
    from .split_viewer import split_viewer
    from .upload_workout import upload_workout

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    app.register_blueprint(workouts, url_prefix = '/')
    app.register_blueprint(split_viewer, url_prefix = '/')
    app.register_blueprint(upload_workout, url_prefix = '/')

    from .models import User, Note

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app = app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
    