from django.contrib import admin
from .models import Profile, Game, UserGame, Comment, Note


class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'type')


admin.site.register(Profile)
admin.site.register(Game, GameAdmin)
admin.site.register(UserGame)
admin.site.register(Comment)
admin.site.register(Note)