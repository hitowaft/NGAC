from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os

app = Flask(__name__)
app.config.from_object(Config)

if os.environ["APP_BASE_URL"] == "http://0.0.0.0:8080/":
    app.config["DEBUG"] = True

    # from werkzeug.contrib.profiler import ProfilerMiddleware
    # app.config['PROFILE'] = True
    # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, sort_by=['tottime'], restrictions=[20])

db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app_mod import routes, models
