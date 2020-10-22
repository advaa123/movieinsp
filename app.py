from flask import Flask, render_template, request
import requests
from tmdbv3api import TMDb, Movie

app = Flask(__name__)

tmdb = TMDb()
tmdb.api_key = 'cd29a8d6e11e7a77604c8b0bb53a1577'
tmdb.language = 'en'
tmdb.debug = True

resp = requests.get(f'https://api.themoviedb.org/3/genre/movie/list?api_key={tmdb.api_key}&language=en-US')
genres = resp.json()['genres']


@app.route("/movie/<movie_id>")
def movie_details(movie_id):
    movie_credits = Movie().credits(movie_id)
    movie_details = Movie().details(movie_id)
    movie_recommendations = Movie().recommendations(movie_id)
    return render_template('movie.html', movie_details=movie_details, credits=movie_credits, recommendations=movie_recommendations, genres=genres)


@app.route("/", methods=['GET', 'POST'])
def get_movie(movie = None):
    movie = Movie()
    popular = movie.popular()
    recdict = {}
    for p in popular:
        recdict[p.title] = {'id': p.id, 'overview': p.overview, 'url': p.poster_path}


    if request.method == "POST":
        user_movie = request.form.get('movie')
        if not user_movie:
            return render_template('index.html', recdict=recdict, genres=genres, mf=Movie().details)

        if not request.form.getlist('genre') and not request.form.get('runtime'):
            return render_template('index.html', search=movie.search(user_movie), genres=genres, mf=Movie().details)

        else:
            user_runtime, checked_genres = None, None
            search = movie.search(user_movie)

            if request.form.getlist('genre'):
                checked_genres = list(map(int, request.form.getlist('genre')))
            
            if request.form.get('runtime'):
                try: 
                    user_runtime = int(request.form.get('runtime'))
                except (TypeError, ValueError):
                    user_runtime = None

            def genre_filter(r):
                for g in movie.details(r.id).genres:
                    if g['id'] in checked_genres:
                        return True
                return False

            def runtime_filter(r):
                if movie.details(r.id).runtime <= user_runtime:
                    return True
                return False

            if checked_genres:
                search = list(filter(genre_filter, search))

            if user_runtime:
                search = list(filter(runtime_filter, search))
            
            if search == []:
                search = movie.search(user_movie)
                return render_template('index.html', 
                    search=search,
                    genres=genres,
                    checked_genres=checked_genres,
                    mf=Movie().details,
                    success=True
                    )
            
            return render_template('index.html', 
                                search=search,
                                genres=genres,
                                checked_genres=checked_genres,
                                mf=Movie().details,
                                )
        

    return render_template('index.html', recdict=recdict, genres=genres, mf=Movie().details)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)