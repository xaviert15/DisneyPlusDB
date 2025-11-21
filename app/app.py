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
    return render_template('show_all.html')

# Atores e Diretores
@APP.route('/persons/')
def show_persons():
    return render_template('show_persons.html')

# Géneros
@APP.route('/genre/')
def show_genre():
    return render_template('show_genre.html')

# Países
@APP.route('/country/')
def show_country():
    return render_template('show_country.html')

# Ratings
@APP.route('/rating/')
def show_rating():
    return render_template('show_rating.html')

# Queries (Placeholders)
@APP.route('/queries/top-actors')
def top_actors():
    return "Top 5 Atores (TODO)"

@APP.route('/queries/avg-duration')
def avg_duration():
    return "Duração média por Género (TODO)"
