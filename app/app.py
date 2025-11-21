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
        SELECT * FROM
        Show
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
        SELECT * FROM
        Genre
    ''').fetchall()
    return render_template('show_genre.html', genres=genres)

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

# Ratings
@APP.route('/rating/')
def show_rating():
    ratings = db.execute('''
        SELECT * FROM
        Rating
        ''').fetchall()
    return render_template('show_rating.html', ratings=ratings)

# Queries (Placeholders)
@APP.route('/queries/top-actors')
def top_actors():
    return "Top 5 Atores (TODO)"

@APP.route('/queries/avg-duration')
def avg_duration():
    return "Duração média por Género (TODO)"
