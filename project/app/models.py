from django.db import models
from django.contrib.auth.models import AbstractUser


# Расширенная модель пользователя
class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='static/images/avatars', default='static/images/avatars/du.jpg')
    
    def __str__(self):
        return self.username

# Жанры
class Genre(models.Model):
    genre_name = models.CharField(max_length=255, verbose_name='Жанр')

    def __str__(self):
        return self.genre_name

# Абстрактная модель для Actor,Director
class Human(models.Model):
    surname = models.CharField(max_length=100, verbose_name='Фамилия')
    name = models.CharField(max_length=100, verbose_name='Имя')

    def __str__(self):
        return f'{self.surname} {self.name}'

    class Meta:
        abstract = True

# Фильм/Сериал
class MediaType(models.Model):
    media_type = models.CharField(max_length=128,verbose_name='Тип контента')
    
    def __str__(self):
        return self.media_type

# Режиссеры
class Director(Human):
    imdb = models.CharField(max_length = 64)
    
    def __str__(self):
        return f'{self.surname} {self.name}'

# Актеры
class Actor(Human):
    imdb = models.CharField(max_length = 64)
    
    def __str__(self):
        return f'{self.surname} {self.name}'

# Фильмы / Сериалы
class Media(models.Model):
    title = models.CharField(max_length=128, verbose_name='Название')
    body = models.TextField(verbose_name='Описание')
    cover = models.ImageField(upload_to='static/images/covers', blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='media_genre')
    year = models.IntegerField(verbose_name='Год')
    duration = models.IntegerField(verbose_name='Продолжительность')
    created_at = models.DateTimeField(auto_now_add=True)

    youtube_trailer_key = models.CharField(max_length=256,blank=True)

    m_type = models.ForeignKey(MediaType,on_delete=models.CASCADE)
    
    rating = models.DecimalField(decimal_places=1, max_digits=3)
    country = models.CharField(max_length=128, verbose_name='Страна производства')

    imdb = models.CharField(max_length = 64)
    
    def __str__(self):
        return self.title
    

# Отзывы
class Review(models.Model):
    title = models.CharField(max_length=64)
    body = models.TextField()
    
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    media = models.ForeignKey(Media,on_delete=models.CASCADE)
    rating = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.user.username} - {self.title}'