from app import db
from datetime import datetime

class Venue(db.Model):
    __tablename__ = 'Venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    @property
    def past_shows(self):
      past_shows = list(
        filter(lambda s: s.start_time < datetime.now(), self.shows)
      )
      return [{
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.isoformat()
      } for show in past_shows]

    @property
    def upcoming_shows(self):
      upcoming_shows = list(
        filter(lambda s: s.start_time >= datetime.now(), self.shows)
      )
      return [{
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.isoformat()
      } for show in upcoming_shows]

    @property
    def past_shows_count(self):
      try:
        return len(self.past_shows)
      except:
        return 0

    @property
    def upcoming_shows_count(self):
      try:
        return len(self.upcoming_shows)
      except:
        return 0

    def update_venue(self):
      db.session.add(self)
      db.session.commit()
      db.session.close()

    def format(self):
      return {
        'id': self.id,
        'name': self.name,
        'address': self.address,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres.split(', '),
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website': self.website_link,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
        'past_shows_count': self.past_shows_count,
        'past_shows': self.past_shows,
        'upcoming_shows_count': self.upcoming_shows_count,
        'upcoming_shows': self.upcoming_shows
      }

    def __repr__(self):
      return f"<Venue id={self.id}, name={self.name}"

    def __getitem__(self, key):
      return getattr(self, key)

class Artist(db.Model):
    __tablename__ = 'Artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    @property
    def past_shows(self):
      past_shows = list(
        filter(lambda s: s.start_time < datetime.now(), self.shows)
      )
      return [{
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.isoformat()
      } for show in past_shows]

    @property
    def upcoming_shows(self):
      upcoming_shows = list(
        filter(lambda s: s.start_time >= datetime.now(), self.shows)
      )

      return [{
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.isoformat()
      } for show in upcoming_shows]

    @property
    def past_shows_count(self):
      try:
        return len(self.past_shows)
      except:
        return 0

    @property
    def upcoming_shows_count(self):
      try:
        return len(self.upcoming_shows)
      except:
        return 0

    def update_artist(self):
      db.session.add(self)
      db.session.commit()
      db.session.close()

    def format(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres.split(', '),
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website': self.website_link,
        'seeking_venues': self.seeking_venues,
        'seeking_description': self.seeking_description,
        'past_shows_count': self.past_shows_count,
        'past_shows': self.past_shows,
        'upcoming_shows_count': self.upcoming_shows_count,
        'upcoming_shows': self.upcoming_shows
      }

    def __getitem__(self, key):
      return getattr(self, key)

class Show(db.Model):
  __tablename__ = 'Shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venues.id'), nullable=False)
  venue = db.relationship('Venue', backref='shows', lazy=True)
  artist = db.relationship('Artist', backref='shows', lazy=True)
  start_time = db.Column(db.DateTime)

  def format(self):
    return {
      'venue_id': self.venue_id,
      'venue_name': self.venue.name,
      'artist_id': self.artist_id,
      'artist_name': self.artist.name,
      'artist_image_link': self.artist.image_link,
      'start_time': self.start_time.isoformat()
    }