from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Game(models.Model):
    GAME_TYPE_CHOICES = [
        ('single', 'Singleplayer'),
        ('online', 'Online'),
        ('coop', 'Co-op'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=10, choices=GAME_TYPE_CHOICES, default='single')

    def __str__(self):
        return self.title


class UserGame(models.Model):
    STATUS_CHOICES = [
        ('want', 'Хочу пройти'),
        ('playing', 'Проходжу'),
        ('completed', 'Пройшов'),
        ('dropped', 'Кинув'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"Note by {self.user.username}"