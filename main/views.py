from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Game, Comment, UserGame, Profile
from django.core.paginator import Paginator


def home(request):
    # топ 5 ігор за рейтингом для головної
    top_games = Game.objects.annotate(
        avg_rating=Avg('usergame__rating')
    ).filter(
        avg_rating__isnull=False
    ).order_by('-avg_rating')[:5]

    return render(request, 'home.html', {
        'top_games': top_games
    })


def register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # перевіряємо чи не зайнятий юзернейм
        if User.objects.filter(username=username).exists():
            error = 'Цей нікнейм вже зайнятий'
        else:
            User.objects.create_user(username=username, password=password)
            return redirect('login')

    return render(request, 'register.html', {'error': error})


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            error = 'Невірний нікнейм або пароль'

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('home')


def game_list(request):
    query = request.GET.get('q')
    game_type = request.GET.get('type')
    sort = request.GET.get('sort')

    games = Game.objects.all()

    if query:
        games = games.filter(title__icontains=query)

    if game_type:
        games = games.filter(type=game_type)

    # додаємо середній рейтинг до кожної гри
    games = games.annotate(avg_rating=Avg('usergame__rating'))

    if sort == 'rating_desc':
        games = games.order_by('-avg_rating')
    elif sort == 'rating_asc':
        games = games.order_by('avg_rating')
    elif sort == 'title':
        games = games.order_by('title')
    elif sort == 'date':
        games = games.order_by('-release_date')

    paginator = Paginator(games, 8)  # 8 карточок на сторінці
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'game_list.html', {
        'page_obj': page_obj,
        'query': query or '',
        'game_type': game_type or '',
        'sort': sort or '',
    })


def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    comments = Comment.objects.filter(game=game).order_by('-created_at')

    # середній рейтинг
    avg_rating = UserGame.objects.filter(game=game).aggregate(
        Avg('rating')
    )['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)

    # чи є гра в бібліотеці поточного юзера
    in_library = False
    user_game = None
    if request.user.is_authenticated:
        try:
            user_game = UserGame.objects.get(user=request.user, game=game)
            in_library = True
        except UserGame.DoesNotExist:
            pass

    # обробка форми нового коментаря
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
        'avg_rating': avg_rating,
        'in_library': in_library,
        'user_game': user_game,
        'rating_range': range(1, 11),
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

    # перевіряємо чи вже є в бібліотеці
    existing = None
    try:
        existing = UserGame.objects.get(user=request.user, game=game)
    except UserGame.DoesNotExist:
        pass

    return render(request, 'add_to_library.html', {
        'game': game,
        'existing': existing,
        'rating_range': range(1, 11),
    })


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_games = UserGame.objects.filter(user=profile_user).select_related('game')

    # середній рейтинг по іграх юзера
    avg_rating = user_games.filter(rating__isnull=False).aggregate(
        Avg('rating')
    )['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)

    # намагаємось отримати профіль (якщо не існує - нічого страшного)
    profile = None
    try:
        profile = profile_user.profile
    except Exception:
        pass

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'user_games': user_games,
        'total_games': user_games.count(),
        'avg_rating': avg_rating,
        'profile': profile,
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