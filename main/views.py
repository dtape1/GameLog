from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Game, Comment, UserGame
from django.core.paginator import Paginator


def home(request):
    # беремо ігри з середнім рейтингом
    top_games = Game.objects.annotate(
        avg_rating=Avg('usergame__rating')
    ).filter(
        avg_rating__isnull=False
    ).order_by('-avg_rating')[:5]

    return render(request, 'home.html', {
        'top_games': top_games
    })


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def game_list(request):
    query = request.GET.get('q')
    game_type = request.GET.get('type')

    games = Game.objects.all()

    if query:
        games = games.filter(title__icontains=query)

    if game_type:
        games = games.filter(type=game_type)

    paginator = Paginator(games, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'game_list.html', {
        'page_obj': page_obj
    })


def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    comments = Comment.objects.filter(game=game)

    # середній рейтинг
    avg_rating = UserGame.objects.filter(game=game).aggregate(
        Avg('rating')
    )['rating__avg']

    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('text')
        if text:
            Comment.objects.create(
                user=request.user,
                game=game,
                text=text
            )
            return redirect('game_detail', game_id=game.id)

    return render(request, 'game_detail.html', {
        'game': game,
        'comments': comments,
        'avg_rating': avg_rating
    })


def add_to_library(request, game_id):
    if not request.user.is_authenticated:
        return redirect('login')

    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        rating = request.POST.get('rating')

        if status == 'want':
            rating = None

        user_game, created = UserGame.objects.get_or_create(
            user=request.user,
            game=game
        )

        user_game.status = status
        user_game.rating = rating if rating else None
        user_game.save()

        return redirect('game_detail', game_id=game.id)

    return render(request, 'add_to_library.html', {'game': game})


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    user_games = UserGame.objects.filter(user=user)

    return render(request, 'profile.html', {
        'profile_user': user,
        'user_games': user_games
    })


def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return redirect('game_detail', game_id=comment.game.id)

    if request.method == 'POST':
        comment.text = request.POST.get('text')
        comment.save()
        return redirect('game_detail', game_id=comment.game.id)

    return render(request, 'edit_comment.html', {'comment': comment})


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user == request.user:
        game_id = comment.game.id
        comment.delete()
        return redirect('game_detail', game_id=game_id)

    return redirect('home')

def like_comment(request, comment_id):
    if not request.user.is_authenticated:
        return redirect('login')

    comment = get_object_or_404(Comment, id=comment_id)

    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    return redirect('game_detail', game_id=comment.game.id)