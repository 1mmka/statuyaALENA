from django.contrib import admin
from app.models import *

# Register your models here.
admin.site.register(Media)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(CustomUser)
admin.site.register(Genre)
admin.site.register(MediaType)
admin.site.register(Review)