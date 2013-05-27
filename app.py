import os

from flask import Flask
from flask.ext.pymongo import PyMongo
from flask_debugtoolbar import DebugToolbarExtension, DebugToolbar
from flask.ext.redis import Redis


app = Flask('findyouflowers')
app.config['MONGO_URI'] = os.environ.get('MONGOHQ_URL', 'mongodb://localhost/flowers')
app.config['DEBUG'] = False if os.environ.get('HEROKU') else True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret_key')
app.config['DEBUG_TB_PANELS'] = DebugToolbar.config['DEBUG_TB_PANELS'] + ('flask_debugtoolbar_mongo.panel.MongoDebugPanel',)
app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://:@localhost:6379/')


redis = Redis(app)

mongo = PyMongo(app)

toolbar = DebugToolbarExtension(app)
