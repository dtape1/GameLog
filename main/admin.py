from django.contrib import admin
from .models import Profile, Game, UserGame, Comment, Note

admin.site.register(Profile)
admin.site.register(Game)
admin.site.register(UserGame)
admin.site.register(Comment)
admin.site.register(Note)