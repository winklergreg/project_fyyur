#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import itertools
import json
from tokenize import group
import dateutil.parser
import babel
import psycopg2
import collections
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify, make_response
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import os

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.create_all()
collections.Callable = collections.abc.Callable
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = Venue.query.all()
  
  keys = lambda k: (k['city'], k['state'])
  sorted_keys = sorted(data, key=keys)
  grouped_data = itertools.groupby(sorted_keys, key=keys)
  venues = [{
    'city': key[0],
    'state': key[1],
    'venues': list(gd)
  } for key, gd in grouped_data]

  return render_template('pages/venues.html', areas=venues);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response = {
    'count': len(venues),
    'data': list([{
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': venue.upcoming_shows_count
    } for venue in venues])
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter_by(id=venue_id).first()
  if venue is None:
    abort(404)

  data = venue.format()
  return render_template('pages/show_venue.html', venue=data)

#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  data = request.form
  genres = data.to_dict(flat=False).get('genres')

  try:
    form = VenueForm(data)
    if form.validate():
      venue = Venue(
        name=data['name'],
        city=data['city'],
        state=data['state'],
        address=data['address'],
        phone=data['phone'],
        genres=', '.join(genres),
        facebook_link=data['facebook_link'],
        image_link=data['image_link'],
        website_link=data['website_link'],
        seeking_talent=True if 'seeking_talent' in data else False,
        seeking_description=data['seeking_description']
      )
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + data['name'] + ' was successfully listed!', 'success')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.', 'danger')
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash(f'Venue ID {venue_id} deleted.')
  except:
    db.session.rollback()
    flash(f'Failed to delete Venue ID {venue_id}.')
  finally:
    db.session.close()
    return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.order_by(Artist.name.asc()).all()
  data = [{
    'id': artist.id,
    'name': artist.name
  } for artist in artists]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  
  response = {
    'count': len(artists),
    'data': list([{
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': artist.upcoming_shows_count
    } for artist in artists])
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.filter_by(id=artist_id).first()
  if artist is None:
    abort(404)

  data = artist.format()
  
  return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash(f'Artist ID {artist_id} deleted.')
  except:
    db.session.rollback()
    flash(f'Failed to delete Artist ID {artist_id}.')
  finally:
    db.session.close()
    return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  if artist is None:
    abort(404)

  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres.split(', '),
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website_link': artist.website_link,
    'facebook_link': artist.facebook_link,
    'seeking_venues': artist.seeking_venues,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link
  }
  form = ArtistForm(formdata=None, data=data)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist_edit = Artist.query.filter_by(id=artist_id).first()

  if artist_edit is None:
    abort(404)
  
  form = ArtistForm(request.form, obj=artist_edit)
  if form.validate():
    form.genres.data = ', '.join(form.genres.data)
    form.populate_obj(artist_edit)
    artist_edit.update_artist()
    
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    return render_template('forms/edit_artist.html', form=form, artist=artist_edit)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  if venue is None:
    abort(404)

  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres.split(', '),
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website_link': venue.website_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link
  }
  form = VenueForm(formdata=None, data=data)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue_edit = Venue.query.filter_by(id=venue_id).first()

  if venue_edit is None:
    abort(404)
  
  form = VenueForm(request.form, obj=venue_edit)
  if form.validate():
    form.genres.data = ', '.join(form.genres.data)
    form.populate_obj(venue_edit)
    venue_edit.update_venue()
    
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    return render_template('forms/edit_venue.html', form=form, venue=venue_edit)

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  data = request.form
  genres = data.to_dict(flat=False).get('genres')
  
  try:
    form = ArtistForm(data)
    if form.validate():
      artist = Artist(
        name=data['name'],
        city=data['city'],
        state=data['state'],
        phone=data['phone'],
        genres=', '.join(genres),
        image_link=data['image_link'],
        facebook_link=data['facebook_link'],
        website_link=data['website_link'],
        seeking_venues=True if 'seeking_venues' in data else False,
        seeking_description=data['seeking_description']
      )
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + data['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data['name'] + ' could not be added.')
  finally:
    db.session.close()
    return render_template('pages/home.html')
  
#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.order_by(Show.start_time.desc()).all()
  data = [show.format() for show in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  data = request.form
  show = Show(
    artist_id=data['artist_id'],
    venue_id=data['venue_id'],
    start_time=data['start_time']
  )
  error_msg = ''
  try:
    artist_exists = Artist.query.filter_by(id=show.artist_id).first() is not None
    venue_exists = Venue.query.filter_by(id=show.venue_id).first() is not None

    if not artist_exists:
      error_msg = f'Artist ID {show.artist_id} does not exist'
    if not venue_exists:
      error_msg = f'Venue ID {show.venue_id} does not exist'

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    db.session.rollback()
    if error_msg is not None:
      flash(error_msg)
  finally:
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
'''
if __name__ == '__main__':
    app.run()
'''
# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)

