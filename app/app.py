import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    return render_template('index.html')

# Catálogo Completo
@APP.route('/show/')
def show_all():
    shows = db.execute('''
        SELECT s.show_id, s.title, s.description, s.show_type, s.release_date, s.date_added, s.duration_value, s.duration_unit, s.rating_id, g.name as genre_name, g.genre_id as genre_id FROM
        Show as s
        LEFT JOIN Show_Genre AS sg on s.show_id=sg.show_id
        LEFT JOIN Genre AS g on sg.genre_id=g.genre_id
        GROUP BY s.show_id
        ''').fetchall()
    return render_template('show_all.html', shows=shows)

# Atores e Diretores
@APP.route('/persons/')
def show_persons():
    persons = db.execute('''
        SELECT p.name, p.person_id, COUNT(c.show_id) as participacoes FROM
        Person AS p
        LEFT JOIN Credit AS c ON p.person_id=c.person_id
        GROUP BY p.person_id
        ''').fetchall()
    return render_template('show_persons.html', persons=persons)

# Géneros
@APP.route('/genre/')
def show_genre():
    genres = db.execute('''
        SELECT g.genre_id, g.name, COUNT(sg.show_id) as counter FROM
        Genre as g
        LEFT JOIN show_genre as sg on g.genre_id=sg.genre_id
        GROUP BY g.genre_id
    ''').fetchall()
    return render_template('show_genre.html', genres=genres)

@APP.route('/genre/<int:code>/')
def genre(code):
    genre = db.execute('''
        SELECT * FROM
        Genre
        WHERE genre_id = ?
    ''', [code]).fetchone()
    shows = db.execute('''
        SELECT s.show_id, s.title, s.show_type, s.description, s.release_date, s.date_added, s.duration_value, s.duration_unit, s.rating_id, g.name as genre_name FROM
        Show as s
        JOIN Show_Genre AS sg on s.show_id=sg.show_id
        LEFT JOIN Genre AS g on sg.genre_id=g.genre_id
        WHERE sg.genre_id=?
        GROUP BY s.show_id
    ''', [code]).fetchall()
    return render_template('genre.html', genre=genre, shows=shows)

# Países
@APP.route('/country/')
def show_country():
    countries = db.execute('''
        SELECT c.country_id, c.name, COUNT(sc.show_id) as counter FROM
        Country AS c
        LEFT JOIN show_country as sc ON c.country_id=sc.country_id
        GROUP BY c.country_id
    ''').fetchall()
    return render_template('show_country.html', countries=countries)

@APP.route('/country/<int:code>/')
def country(code):
    country = db.execute('''
        SELECT * FROM
        Country
        WHERE country_id = ?
    ''', [code]).fetchone()
    shows = db.execute('''
        SELECT s.show_id, s.title, s.description, s.show_type, s.release_date, s.date_added, s.duration_value, s.duration_unit, s.rating_id, g.name as genre_name FROM
        Show as s
        JOIN Show_Country AS sc ON s.show_id = sc.show_id
        LEFT JOIN Show_Genre AS sg on s.show_id=sg.show_id
        LEFT JOIN Genre AS g on sg.genre_id=g.genre_id
        WHERE sc.country_id=?
        GROUP BY s.show_id
    ''', [code]).fetchall()
    return render_template('country.html', country=country, shows=shows)


# Ratings
@APP.route('/rating/')
def show_rating():
    ratings = db.execute('''
        SELECT r.rating_id, r.code, COUNT(s.show_id) as counter FROM
        Rating as R
        LEFT JOIN Show as s ON r.rating_id = s.rating_id
        GROUP BY r.rating_id
        ''').fetchall()
    return render_template('show_rating.html', ratings=ratings)

@APP.route('/rating/<int:code>/')
def rating(code):
    rating = db.execute('''
        SELECT * FROM
        Rating
        WHERE rating_id = ?
    ''', [code]).fetchone()
    shows = db.execute('''
        SELECT s.show_id, s.title, s.description, s.show_type, s.release_date, s.date_added, s.duration_value, s.duration_unit, g.name as genre_name FROM
        Show as s
        JOIN Rating AS r ON r.rating_id = s.rating_id
        LEFT JOIN Show_Genre AS sg on s.show_id=sg.show_id
        LEFT JOIN Genre AS g on sg.genre_id=g.genre_id
        WHERE r.rating_id=?
        GROUP BY s.show_id
    ''', [code]).fetchall()
    return render_template('rating.html', rating=rating, shows=shows)

# Queries (Placeholders)
@APP.route('/queries/top-actors')
def top_actors():
    return "Top 5 Atores (TODO)"

@APP.route('/queries/avg-duration')
def avg_duration():
    return "Duração média por Género (TODO)"
