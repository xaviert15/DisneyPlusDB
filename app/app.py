import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask, request
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
    search = request.args.get('search')
    order = request.args.get('order')
    direction = request.args.get('direction', 'asc')
    possible_order = ['show_id', 'duration_value', 'release_date', 'date_added']
    if order not in possible_order:
        order = 'show_id'
    if direction not in ['asc', 'desc']:
        direction = 'asc'
    if search:
        shows = db.execute(f'''
            SELECT s.show_id, s.title, s.description, s.show_type, s.release_date, s.date_added, s.duration_value, s.duration_unit, s.rating_id, g.name as genre_name, g.genre_id as genre_id FROM
            Show as s
            LEFT JOIN Show_Genre AS sg on s.show_id=sg.show_id
            LEFT JOIN Genre AS g on sg.genre_id=g.genre_id
            WHERE s.title LIKE ? OR s.description LIKE ?
            GROUP BY s.show_id
            ORDER BY s.{order} {direction}
            ''', [f'%{search}%', f'%{search}%']).fetchall()
    else:
        shows = db.execute(f'''
            SELECT s.show_id, s.title, s.description, s.show_type, s.release_date, s.date_added, s.duration_value, s.duration_unit, s.rating_id, g.name as genre_name, g.genre_id as genre_id FROM
            Show as s
            LEFT JOIN Show_Genre AS sg on s.show_id=sg.show_id
            LEFT JOIN Genre AS g on sg.genre_id=g.genre_id
            GROUP BY s.show_id
            ORDER BY s.{order} {direction}
            ''').fetchall()
    return render_template('show_all.html', shows=shows, order=order, direction=direction)

# Filmes
@APP.route('/movies/')
def show_movies():
    movies = db.execute('''
        SELECT s.show_id, s.title, s.description, s.release_date, s.date_added, s.duration_value, s.duration_unit, s.rating_id, g.name as genre_name, g.genre_id as genre_id FROM
        Show as s
        LEFT JOIN Show_Genre AS sg on s.show_id=sg.show_id
        LEFT JOIN Genre AS g on sg.genre_id=g.genre_id
        WHERE s.show_type="Movie"
        GROUP BY s.show_id
        ''').fetchall()
    return render_template('show_movies.html', movies=movies)

# TV Shows
@APP.route('/tvshows/')
def show_tvshows():
    tvshows = db.execute('''
        SELECT s.show_id, s.title, s.description, s.release_date, s.date_added, s.duration_value, s.duration_unit, s.rating_id, g.name as genre_name, g.genre_id as genre_id FROM
        Show as s
        LEFT JOIN Show_Genre AS sg on s.show_id=sg.show_id
        LEFT JOIN Genre AS g on sg.genre_id=g.genre_id
        WHERE s.show_type="TV Show"
        GROUP BY s.show_id
        ''').fetchall()
    return render_template('show_tvshows.html', tvshows=tvshows)

# Atores e Diretores
@APP.route('/person/')
def show_persons():
    persons = db.execute('''
        SELECT p.name, p.person_id, COUNT(c.show_id) as participacoes FROM
        Person AS p
        LEFT JOIN Credit AS c ON p.person_id=c.person_id
        GROUP BY p.person_id
        ''').fetchall()
    return render_template('show_persons.html', persons=persons)

@APP.route('/person/<int:code>/')
def person(code):
    person = db.execute('''
        SELECT * FROM
        Person
        WHERE person_id = ?
    ''', [code]).fetchone()
    shows = db.execute('''
        SELECT s.show_id, s.title, s.description, s.show_type, s.release_date, s.date_added, s.duration_value, s.duration_unit, s.rating_id, g.name as genre_name, g.genre_id, GROUP_CONCAT(DISTINCT c.role) as role_name FROM
        Show as s
        LEFT JOIN credit AS c ON s.show_id=c.show_id
        LEFT JOIN person AS p ON c.person_id=p.person_id
        LEFT JOIN Show_Genre AS sg on s.show_id=sg.show_id
        LEFT JOIN Genre AS g on sg.genre_id=g.genre_id
        WHERE c.person_id=?
        GROUP BY s.show_id
    ''', [code]).fetchall()
    return render_template('person.html', person=person, shows=shows)

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

# Ano de Realização
@APP.route('/year/<int:code>/')
def year(code):
    year_str = str(code)
    shows = db.execute('''
        SELECT s.show_id, s.title, s.description, s.show_type, 
               s.release_date, s.date_added, s.duration_value, 
               s.duration_unit, s.rating_id, g.name as genre_name 
        FROM Show as s
        LEFT JOIN Show_Genre AS sg on s.show_id = sg.show_id
        LEFT JOIN Genre AS g on sg.genre_id = g.genre_id
        WHERE strftime('%Y', s.release_date) = ?
        GROUP BY s.show_id
    ''', [year_str]).fetchall()
    return render_template('year.html', year=code, shows=shows)

# Show (Movie + TV Show)
@APP.route('/show/<int:id>/')
def show(id):
    # 1. Informação Principal do Filme + Rating
    show = db.execute('''
        SELECT s.*, r.code as rating_code
        FROM Show s
        LEFT JOIN Rating r ON s.rating_id = r.rating_id
        WHERE s.show_id = ?
    ''', [id]).fetchone()

    if not show:
        return "Filme não encontrado", 404

    # 2. Buscar Géneros
    genres = db.execute('''
        SELECT g.genre_id, g.name 
        FROM Genre g
        JOIN Show_Genre sg ON g.genre_id = sg.genre_id
        WHERE sg.show_id = ?
    ''', [id]).fetchall()

    # 3. Buscar Países
    countries = db.execute('''
        SELECT c.country_id, c.name 
        FROM Country c
        JOIN Show_Country sc ON c.country_id = sc.country_id
        WHERE sc.show_id = ?
    ''', [id]).fetchall()

    # 4. Buscar Elenco e Diretores (Tudo junto e separamos no Python)
    credits = db.execute('''
        SELECT p.person_id, p.name, c.role
        FROM Person p
        JOIN Credit c ON p.person_id = c.person_id
        WHERE c.show_id = ?
        ORDER BY p.name
    ''', [id]).fetchall()
    actors = [p for p in credits if p['role'] == 'Actor']
    directors = [p for p in credits if p['role'] == 'Director']
    return render_template('show.html', 
                           show=show, 
                           genres=genres, 
                           countries=countries, 
                           actors=actors, 
                           directors=directors)

# Queries (Placeholders)
@APP.route('/queries/top-actors/')
def top_actors():
    topActors = db.execute('''
    select p.name, count(show_id) NumberOfShows, p.person_id personID from person p join credit c on p.person_id = c.person_id where c.role = 'Actor' group by c.person_id order by NumberOfShows desc limit 5
    ''').fetchall()
    return render_template('top_Actors.html', topActors=topActors)

@APP.route('/queries/topDurationMovies/')
def top_DurationMovies():
    topDurationMovies = db.execute('''
        WITH RankedMovies AS (
            SELECT g.name AS genrename, s.title AS movietitle, s.duration_value, s.duration_unit, g.genre_id AS genreID, s.show_id AS showID,
                RANK() OVER (PARTITION BY g.genre_id ORDER BY s.duration_value DESC) AS rank
            FROM Show s
            JOIN Show_Genre sg ON s.show_id = sg.show_id
            JOIN Genre g ON sg.genre_id = g.genre_id
            WHERE s.show_type = 'Movie'
        )
        SELECT * FROM RankedMovies 
        WHERE rank <= 3
        ORDER BY genrename ASC, rank ASC
    ''').fetchall()
    return render_template('top_durationMovies.html', topDurationMovies=topDurationMovies)

@APP.route('/queries/topExporters/')
def top_exporters():
    exporters = db.execute('''
        SELECT c.name AS country_name, c.country_id, SUM(CASE WHEN s.show_type = 'Movie' THEN 1 ELSE 0 END) AS total_movies, SUM(CASE WHEN s.show_type = 'TV Show' THEN 1 ELSE 0 END) AS total_tv, COUNT(s.show_id) AS total_content
        FROM Country c
        JOIN Show_Country sc ON c.country_id = sc.country_id
        JOIN Show s ON sc.show_id = s.show_id
        GROUP BY c.country_id
        ORDER BY total_content DESC
        LIMIT 20
    ''').fetchall()
    exporters_total = db.execute('''
        SELECT SUM(CASE WHEN s.show_type = 'Movie' THEN 1 ELSE 0 END) AS total_movies, SUM(CASE WHEN s.show_type = 'TV Show' THEN 1 ELSE 0 END) AS total_tv, COUNT(s.show_id) AS total_content
        FROM Country c
        JOIN Show_Country sc ON c.country_id = sc.country_id
        JOIN Show s ON sc.show_id = s.show_id
        ORDER BY total_content DESC
    ''').fetchone()
    return render_template('top_exporters.html', exporters=exporters, exporters_total=exporters_total)

@APP.route('/queries/avgGenreDuration/')
def avg_durationMovies():
    avgShowGenreDuration = db.execute('''
        select name, show_type, genre_id, round(avg(duration_value), 2) avg, duration_unit from show natural join show_genre natural join genre group by genre_id, show_type order by show_type, avg desc
    ''').fetchall()
    avgMovieDuration, avgTVDuration = db.execute('''
        select show_type, round(avg(duration_value), 2) avg, duration_unit from show natural join show_genre natural join genre group by show_type order by show_type
    ''').fetchmany(2)
    return render_template('avg_durationShows.html', avgShowGenreDuration=avgShowGenreDuration, avgTVDuration=avgTVDuration, avgMovieDuration=avgMovieDuration)

@APP.route('/queries/actorsdirectors/')
def actors_directors():
    actorsdirectors = db.execute('''
    SELECT 
            p.person_id, p.name, SUM(CASE WHEN c.role = 'Actor' THEN 1 ELSE 0 END) as count_actor, SUM(CASE WHEN c.role = 'Director' THEN 1 ELSE 0 END) as count_director, COUNT(DISTINCT c.show_id) as total_shows
        FROM Person p
        JOIN Credit c ON p.person_id = c.person_id
        GROUP BY p.person_id
        HAVING count_actor > 0 AND count_director > 0
        ORDER BY total_shows DESC
    ''').fetchall()
    return render_template('actors_directors.html', actorsdirectors=actorsdirectors)

@APP.route('/queries/monthlyreleases/')
def monthly_releases():
    monthlyreleases = db.execute('''
        SELECT strftime('%m', date_added) as month, COUNT(show_id) as count
        FROM Show
        WHERE date_added IS NOT NULL
        GROUP BY month
        ORDER BY month ASC
    ''').fetchall()
    return render_template('monthly_releases.html', monthlyreleases=monthlyreleases)

@APP.route('/queries/cumulativegrowth/')
def cumulative_growth():
    growth = db.execute('''
        SELECT strftime('%Y-%m', date_added) as month, COUNT(*) as monthly_added, SUM(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', date_added)) as cumulative_total
        FROM Show
        WHERE date_added IS NOT NULL
        GROUP BY month
        ORDER BY month
    ''').fetchall()
    return render_template('cumulative_growth.html', growth=growth)

@APP.route('/queries/weekdayreleases/')
def weekday_releases():
    weekdayreleases = db.execute('''
        SELECT 
            CASE CAST(strftime('%w', date_added) AS INTEGER)
                WHEN 0 THEN 'Domingo'
                WHEN 1 THEN 'Segunda-feira'
                WHEN 2 THEN 'Terça-feira'
                WHEN 3 THEN 'Quarta-feira'
                WHEN 4 THEN 'Quinta-feira'
                WHEN 5 THEN 'Sexta-feira'
                WHEN 6 THEN 'Sábado'
            END as day_name,
            COUNT(*) as total_added,
            CAST(strftime('%w', date_added) AS INTEGER) as day_index
        FROM Show
        WHERE date_added IS NOT NULL
        GROUP BY day_index
        ORDER BY day_index ASC
    ''').fetchall()
    return render_template('weekday_releases.html', weekdayreleases=weekdayreleases)