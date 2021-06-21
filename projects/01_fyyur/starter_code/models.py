#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# Set up flask migrate
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String(120)), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref = 'venue', lazy=True)

    def __repr__(self):
      return f'<Venue ID: {self.id}, Name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column("genres", db.ARRAY(db.String(120)), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable = False, default = False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref = 'artist', lazy=True)

    def __repr__(self):
      return f'<Artist ID: {self.id}, Name: {self.name}>'
    

# Show Model
class Show(db.Model):
  __tablename__ = 'Show'
 
  id = db.Column(db.Integer, primary_key = True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False),
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
  start_time = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

  def __repr__(self):
      return f'<Venue ID: {self.id}, Name: {self.name}>'
