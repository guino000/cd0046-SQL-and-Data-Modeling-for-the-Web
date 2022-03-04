# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for, Flask
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_moment import Moment
from sqlalchemy import and_, func
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
from models import db, Venue, Show, Artist

app = Flask(__name__)
db.init_app(app)
app.config.from_object('config')
moment = Moment(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
# Done: implement any missing fields, as a database migration using Flask-Migrate

# Done: implement any missing fields, as a database migration using Flask-Migrate


# Done Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # DONE: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    cities = db.session.query(Venue.city, Venue.state) \
        .group_by(Venue.city, Venue.state) \
        .all()

    data = []
    for city in cities:
        citydata = dict(city)
        venues = db.session.query(
            Venue.id,
            Venue.name,
        ).filter(
            and_(
                Venue.city == city.city,
                Venue.state == city.state
            )
        ).all()
        citydata['venues'] = [{
            'id': v.id,
            'name': v.name,
            'num_upcoming_shows': Show.query.filter(Show.venue_id == v.id).count()
        } for v in venues]
        data.append(citydata)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    results = Venue.query.filter(func.lower(Venue.name).like(f'%{search_term.lower()}%')).all()
    response = {
        "count": len(results),
        "data": [{
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": Show.query.filter(Show.start_time > datetime.now(),
                                                    Show.venue_id == result.id).count()
        } for result in results]
    }
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_venues.html', results=response,
                           search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # Done: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id).as_dict()
    venue['genres'] = [genre for genre in venue['genres'].split(',')]
    venue['past_shows'] = dict(Show.query.filter(Show.start_time <= datetime.now()).all())
    venue['past_shows_count'] = Show.query.filter(Show.start_time <= datetime.now(), Show.venue_id == venue_id).count()
    venue['upcoming_shows'] = dict(Show.query.filter(Show.start_time > datetime.now()).all())
    venue['upcoming_shows_count'] = Show.query.filter(Show.start_time > datetime.now(),
                                                      Show.venue_id == venue_id).count()
    return render_template('pages/show_venue.html', venue=venue)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Done: insert form data as a new Venue record in the db, instead
    # Done: modify data to be the data object returned from db insertion

    try:
        venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            genres=request.form['genres'],
            facebook_link=request.form['facebook_link'],
            image_link=request.form['image_link'],
            website=request.form['website_link'],
            seeking_description=request.form['seeking_description']
        )
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        # Done: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except Exception as err:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed. ' + str(err))
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    # Done: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was deleted!')
    except Exception as err:
        flash('Error deleting Venue! ' + str(err))
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')
    # Done: BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Done: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    results = Artist.query.filter(func.lower(Artist.name).like(f'%{search_term.lower()}%')).all()
    response = {
        "count": len(results),
        "data": [{
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": Show.query.filter(Show.start_time > datetime.now(),
                                                    Show.artist_id == result.id).count()
        } for result in results]
    }
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # Done: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id).as_dict()
    artist['genres'] = [genre for genre in artist['genres'].split(',')]
    past_shows = Show.query.filter(Show.start_time <= datetime.now(), Show.artist_id == artist_id).all()
    upcoming_shows = Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == artist_id).all()
    artist['past_shows'] = [
        {
            "venue_id": show.venue_id,
            "venue_name": Venue.query(Venue.name).get(show.venue_id),
            "venue_image_link": Venue.query(Venue.image_link).get(show.venue_id),
            "start_time": show.start_time
        } for show in past_shows
    ]
    artist['upcoming_shows'] = [
        {
            "venue_id": show.venue_id,
            "venue_name": Venue.query(Venue.name).get(show.venue_id),
            "venue_image_link": Venue.query(Venue.image_link).get(show.venue_id),
            "start_time": show.start_time
        } for show in upcoming_shows
    ]
    artist['past_shows_count'] = len(past_shows)
    artist['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.process_data(artist.name)
    form.genres.process_data(artist.genres)
    form.city.process_data(artist.city)
    form.state.process_data(artist.state)
    form.phone.process_data(artist.phone)
    form.website_link.process_data(artist.website)
    form.facebook_link.process_data(artist.facebook_link)
    form.seeking_venue.process_data(artist.seeking_venue)
    form.seeking_description.process_data(artist.seeking_description)
    form.image_link.process_data(artist.image_link)
    # Done: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Done: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name')
        artist.genres = request.form.get('genres')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.website = request.form.get('website_link')
        artist.facebook_link = request.form.get('facebook_link')
        artist.seeking_venue = request.form.get('seeking_venue')
        artist.seeking_description = request.form.get('seeking_description')
        artist.image_link = request.form.get('image_link')
        db.session.commit()
        flash('Artist updated successfully!')
    except Exception as err:
        db.session.rollback()
        flash('Error updating artist! ' + str(err))
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.process_data(venue.name)
    for genre in venue.genres:
        for c in form.genres.iter_choices():
            if c[0] == genre:
                form.genres.process_data(c)
    form.address.process_data(venue.address)
    form.city.process_data(venue.city)
    form.state.process_data(venue.state)
    form.phone.process_data(venue.phone)
    form.website_link.process_data(venue.website)
    form.facebook_link.process_data(venue.facebook_link)
    form.seeking_talent.process_data(venue.seeking_talent)
    form.seeking_description.process_data(venue.seeking_description)
    form.image_link.process_data(venue.image_link)

    # Done: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.genres = request.form.get('genres')
        venue.facebook_link = request.form.get('facebook_link')
        venue.image_link = request.form.get('image_link')
        venue.website = request.form.get('website_link')
        venue.seeking_description = request.form.get('seeking_description')
        db.session.commit()
        flash('Venue updated successfully!')
    except Exception as err:
        db.session.rollback()
        flash('Error updating venue!' + str(err))
    finally:
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
    try:
        artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            genres=request.form['genres'],
            image_link=request.form['image_link'],
            phone=request.form['phone'],
            seeking_description=request.form['seeking_description'],
            seeking_venue='seeking_venue' in request.form,
            state=request.form['state'],
            website=request.form['website_link'],
            facebook_link=request.form['facebook_link']
        )

        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + artist.name + ' was listed successfully!')
    except Exception as err:
        flash('Error when adding new artist! ' + str(err))
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
