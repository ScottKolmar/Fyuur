#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():


  # Instantiate empty data list
  data = []

  # Get all the venues in the table
  venues = Venue.query.all()

  # Instantiate empty location set so there are not duplicate locations
  locations = set()

  # Populate locations set
  for venue in venues:
    locations.add((venue.city, venue.state))

  # Loop through each location
  for location in locations:

    # Get all the venues unique to the location
    location_venues = Venue.query.filter_by(city=location[0]).order_by('id').all()

    # Generate a dictionary for each venue in the location, for display
    venue_dicts = []
    for venue in location_venues:
      upcoming_shows = 0
      for show in venue.shows:
        if show.start_time > datetime.datetime.now():
          upcoming_shows += 1
      venue_dict = {
        "id": venue.id,
        "name": venue.name,
        "num upcoming shows": upcoming_shows
        }
      venue_dicts.append(venue_dict)
    
    # Append the location data to the empty data list
    data.append({
      "city": location[0],
      "state": location[1],
      "venues": venue_dicts
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Searches venues, case insensitive
  
  search_term=request.form.get('search_term', '')
  query_results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term)))
  data = []

  for item in query_results:
    upcoming_shows = 0
    for show in item.shows:
      if show.start_time > datetime.datetime.now():
        upcoming_shows += 1
    item_dict = {
      "id": item.id,
      "name": item.name,
      "num upcoming shows": upcoming_shows
      }
    data.append(item_dict)

  response={
    "count": query_results.count(),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
    data = {
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": format_datetime(str(show.start_time))
    }
    if show.start_time < datetime.datetime.now():
      past_shows.append(data)
    elif show.start_time > datetime.datetime.now():
      upcoming_shows.append(data)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
    form = VenueForm()
    venue = Venue(name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website_link.data,
    facebook_link = form.facebook_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    image_link = form.image_link.data)

    # Add venue to database and commit
    db.session.add(venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:

    # Rollback session if error occurs
    db.session.rollback()

    # Flash error message
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  finally:

    # Close session
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Deletes a venue record

  # Get venue from database
  venue = Venue.query.get(venue_id)

  try:

    # Delete venue from database
    db.session.delete(venue_id)
    db.session.commit()

    # Flash success message
    flash('Venue ' + venue.name + 'was deleted.')
  
  except:

    # Rollback session if error occurs
    db.session.rollback()
    
    # Flash error message
    flash('An error occurred. Venue ' + venue.name + 'could not be deleted.')
  
  finally:

    # Close session
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():


  # Query database for artists
  artists = Artist.query.all()

  # Loop through artists and append data to list
  data = []
  for artist in artists:
    artist_data = {
      "id": artist.id,
      "name": artist.name,
    }
    data.append(artist_data)
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Searches for artist with given search term, case insensitive

  # Get search term from form
  search_term=request.form.get('search_term', '')

  # Get query results from database with case insensitive search
  query_results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term)))

  # Loop through results and append data dictionaries to empty list
  data = []
  for item in query_results:
    upcoming_shows = 0
    for show in item.shows:
      if show.start_time > datetime.datetime.now():
        upcoming_shows += 1
    item_dict = {
      "id": item.id,
      "name": item.name,
      "num upcoming shows": upcoming_shows
      }
    data.append(item_dict)

  response={
    "count": len(query_results),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  # Get artist from database
  artist = Artist.query.get(artist_id)

  # Loop through shows to get past and upcoming shows
  past_shows = []
  upcoming_shows = []
  for show in artist.shows:
      show_data = {
        "artist_id": show.artist_id,
        "artist_name": Artist.query.get(show.artist_id).name,
        "artist_image_link": Artist.query.get(show.artist_id).image_link,
        "start_time": format_datetime(str(show.start_time))
      }
      if show.start_time < datetime.datetime.now():
        past_shows.append(show_data)
      elif show.start_time > datetime.datetime.now():
        upcoming_shows.append(show_data)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = Artist.query.get(artist_id)

  artist_data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }

  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes

  try:

    # Instantiate form
    form = ArtistForm()

    # Get artist from database
    artist = Artist.query.get(artist_id)

    # Update values from form values
    artist.name == form.name.data
    artist.phone == form.phone.data
    artist.city == form.city.data
    artist.state == form.state.data
    artist.genres == form.genres.data
    artist.image_link == form.image_link.data
    artist.facebook_link == form.facebook_link.data

    # Commit to database and flash success message
    db.session.commit()
    flash('Artist ' + request.form['name'] + 'was updated.')
  
  except:

    # Rollback session if an error occurred
    db.session.rollback()
    flash('An error occurred, ' + request.form['name'] + 'could not be updated.')

  finally:

    # Close session
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue_data ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes


  try:
    
    # Instantiate form and query database for venue
    form = VenueForm
    venue = Venue.query.get(venue_id)

    # Update values with form values
    venue.name == form.name.data
    venue.genres == form.genres.data
    venue.address == form.address.data
    venue.city == form.city.data
    venue.state == form.state.data
    venue.phone == form.phone.data
    venue.website == form.website_link.data
    venue.facebook_link == form.facebook_link.data
    venue.seeking_talent == form.seeking_talent.data
    venue.seeking_description == form.seeking_description.data
    venue.image_link == form.image_link.data

    # Commit changes to database and flash success message
    db.session.commit()
    flash('Venue ' + request.form['name'] + 'was updated.')

  except:

    # Rollback database session if error occurs
    db.session.rollback()
    flash('An error occurred, ' + request.form['name'] + 'could not be updated.')

  finally:

    # Close session
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  

  try:
    form = ArtistForm()
    artist = Artist(name = form.name.data,
    genres = form.genres.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website_link.data,
    facebook_link = form.facebook_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data,
    image_link = form.image_link.data)

    # Add venue to database and commit
    db.session.add(artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:

    # Rollback session if error occurs
    db.session.rollback()

    # Flash error message
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  finally:

    # Close session
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  #       num_shows should be aggregated based on number of upcoming shows per venue.


  shows = Show.query.order_by(db.desc(Show.start_time))
  data = []
  for show in shows:
    show_data = {
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": format_datetime(str(show.start_time))
    }
    data.append(show_data)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form

  try:

    # Instantiate form and fill show variable with values from form
    form = ShowForm()
    show = Show(artist_id = form.artist_id.data,
    venue_id = form.venue_id.data,
    start_time = form.start_time.data)

    # Add show to database and commit
    db.session.add(show)
    db.session.commit()

    # Flash success message
    flash('Show was successfully listed')

  except:

    # Rollback session on error and flash message
    db.session.rollback()
    flash('An error occurred, show could not be listed.')

  finally:

    # Close session
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
