from django.core.management.base import BaseCommand
from app.models import Genre,Media,Actor,Director,MediaType
import requests
from django.core.files.base import ContentFile

class Command(BaseCommand):   
    help = 'Добавляет данные из сторонних API'
    
    def handle(self, *args, **options):
        
        if not Genre.objects.exists():
            url = "https://moviesminidatabase.p.rapidapi.com/genres/"
            headers = {
	            "X-RapidAPI-Key": "a vot ne dam)",
	            "X-RapidAPI-Host": "moviesminidatabase.p.rapidapi.com"
            }
            genre_response = requests.get(url, headers=headers).json()['results']
            for genre in genre_response:
                Genre.objects.create(
                genre_name = genre['genre'],
            )
            self.stdout.write(self.style.SUCCESS('Жанры добавлены'))
        else:
            self.stdout.write(self.style.SUCCESS('Жанры уже есть'))
            
    
        if not Media.objects.filter(m_type = 1).exists() or len(Media.objects.filter(m_type = 1)) < 70:
            url = "https://movies-tv-shows-database.p.rapidapi.com/"
            querystring = {"page":"1"}
            headers = {
	            "Type": "get-trending-movies",
	            "X-RapidAPI-Key": "a vot ne dam)",
	            "X-RapidAPI-Host": "movies-tv-shows-database.p.rapidapi.com"
            }

            movieIMDB = list()
            for movie_range in range(1,8,1):
                querystring['page'] = str(movie_range)
                response = requests.get(url, headers=headers, params=querystring).json()['movie_results']
                for movie_imdb in response:
                    movieIMDB.append(movie_imdb['imdb_id'])

            headers['Type'] = "get-movie-details"
            querystring = {"movieid":"tt1375666"}

            for movie_imdb in movieIMDB:
                headers['Type'] = "get-movie-details"
                querystring['movieid'] = str(movie_imdb)
                response = requests.get(url, headers=headers, params=querystring).json()

                if response['title'] and response['description'] and response['genres'] and response['year'] and response['runtime'] and response['imdb_rating'] and response['countries']:
                    if not Media.objects.filter(title = response['title']).exists():
                        media = Media.objects.create(
                            title = response['title'],
                            body = response['description'],
                            genre = Genre.objects.get(genre_name = response['genres'][0]),
                            year = response['year'],
                            duration = response['runtime'],
                            m_type = MediaType.objects.get(id = 1),
                            rating = response['imdb_rating'],
                            country = response['countries'][0],
                            imdb = movie_imdb,
                            youtube_trailer_key = response['youtube_trailer_key'],
                        )
            
                        headers['Type'] = "get-movies-images-by-imdb"
                        img_response = requests.get(url,headers=headers,params=querystring).json()['poster']
                        img_content = requests.get(img_response).content
                        media.cover.save(f'cover_{media.pk}.jpg',ContentFile(img_content),save=True)
            self.stdout.write(self.style.SUCCESS('Фильмы добавлены'))
        else:
            self.stdout.write(self.style.SUCCESS('Фильмы уже есть'))
        
        
        if not Media.objects.filter(m_type = 2).exists() or len(Media.objects.filter(m_type = 2)) < 50:
            url = "https://movies-tv-shows-database.p.rapidapi.com/"
            querystring = {"page":"1"}
            headers = {
	            "Type": "get-trending-shows",
	            "X-RapidAPI-Key": "a vot ne dam)",
	            "X-RapidAPI-Host": "movies-tv-shows-database.p.rapidapi.com"
            }
            
            tv_showIMDB = list()
            for show in range(1,4,1):
                querystring['page'] = str(show)
                response = requests.get(url, headers=headers, params=querystring).json()['tv_results']
                for tv_show in response:
                    tv_showIMDB.append(tv_show['imdb_id'])
            
            querystring = {"seriesid":"tt2741602"}        
            
            for serial_imdb in tv_showIMDB:
                headers['Type'] = "get-show-details"
                querystring['seriesid'] = str(serial_imdb)
                response = requests.get(url, headers=headers, params=querystring).json()
                
                if response['title'] and response['description'] and response['genres'] and response['year_started'] and response['runtime'] and response['imdb_rating'] and response['countries']:
                    
                    if not Media.objects.filter(title = response['title']):
                        media = Media.objects.create(
                            title = response['title'],
                            body = response['description'],
                            genre = Genre.objects.get(genre_name = response['genres'][0]),
                            year = response['year_started'],
                            duration = response['runtime'],
                            m_type = MediaType.objects.get(id = 2),
                            rating = response['imdb_rating'],
                            country = response['countries'][0],
                            imdb = serial_imdb,
                        )
                        
                        headers['Type'] = "get-show-images-by-imdb"
                        img_response = requests.get(url, headers=headers, params=querystring).json()['poster']
                        img_content = requests.get(img_response).content
                        media.cover.save(f'cover_{media.pk}.jpg',ContentFile(img_content),save=True)
            self.stdout.write(self.style.SUCCESS('Сериалы добавлены'))
        else:
            self.stdout.write(self.style.SUCCESS('Сериалы уже есть'))
        
        
        
        if Actor.objects.all() or Director.objects.all():
            self.stdout.write(self.style.SUCCESS('Актеры и Режиссеры фильмов/сериалов существуют'))
        else:
            url = "https://movies-tv-shows-database.p.rapidapi.com/"
            headers = {
	            "Type": None,
	            "X-RapidAPI-Key": "a vot ne dam)3",
	            "X-RapidAPI-Host": "movies-tv-shows-database.p.rapidapi.com"
            }
            
            media = Media.objects.all()
            for data in media:
                if data.m_type.pk == 1:
                    querystring = {"movieid":str(data.imdb)}
                    headers['Type'] = "get-movie-details"
                    
                    response = requests.get(url, headers=headers, params=querystring).json()
                    actors = response['stars']
                    directors = response['directors']
                    
                    for actor in actors:
                        if not Actor.objects.filter(surname = actor.split()[-1]).exists():
                            if len(Actor.objects.filter(imdb = data.imdb)) == 15:
                                break
                            actor = actor.split(' ',-1)
                            if len(actor) == 2:
                                new_actor = Actor.objects.create(
                                    surname = actor[-1],
                                    name = actor[0],
                                    imdb = data.imdb,
                                )
                                new_actor.save()
                    
                    for director in directors:
                        if not Director.objects.filter(surname = director.split()[-1]).exists():
                            if len(Director.objects.filter(imdb = data.imdb)) == 2:
                                break
                            director = director.split(' ',-1)
                            if len(director) == 2:
                                new_director = Director.objects.create(
                                    surname = director[-1],
                                    name = director[0],
                                    imdb = data.imdb
                                )
                                new_director.save()
                else:
                    querystring = {"seriesid":"tt2741602"}
                    headers['Type'] = "get-show-details"
                    response = requests.get(url, headers=headers, params=querystring).json()
                    
                    actors = response['stars']
                    directors = response['directors']
                    
                    for actor in actors:
                        if not Actor.objects.filter(surname = actor.split()[-1]).exists():
                            if len(Actor.objects.filter(imdb = data.imdb)) == 15:
                                break
                            actor = actor.split(' ',-1)
                            if len(actor) == 2:
                                new_actor = Actor.objects.create(
                                    surname = actor[-1],
                                    name = actor[0],
                                    imdb = data.imdb,
                                )
                                new_actor.save()
                    
                    for director in directors:
                        if not Director.objects.filter(surname = director.split()[-1]).exists():
                            if len(Director.objects.filter(imdb = data.imdb)) == 2:
                                break
                            director = director.split(' ',-1)
                            if len(director) == 2:
                                new_director = Director.objects.create(
                                    surname = director[-1],
                                    name = director[0],
                                    imdb = data.imdb
                                )
                                new_director.save()
            self.stdout.write(self.style.SUCCESS('Актеры и Режиссеры фильмов/сериалов были добавлены'))