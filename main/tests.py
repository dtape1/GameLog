from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Game, UserGame, Comment, Profile, Note
import datetime


# ============================================================
# Тести для моделей
# ============================================================

class GameModelTest(TestCase):
    """
    Тестуємо модель Game.
    Передумова: є хоча б одна гра в БД.
    Постумова: всі поля зберігаються і читаються правильно.
    """

    def setUp(self):
        # створюємо тестову гру перед кожним тестом
        self.game = Game.objects.create(
            title='The Witcher 3',
            description='Крутий RPG від CD Projekt',
            release_date=datetime.date(2015, 5, 19),
            type='single'
        )

    def test_game_created(self):
        # перевіряємо що гра створилась
        self.assertEqual(Game.objects.count(), 1)

    def test_game_title(self):
        # перевіряємо що назва збережена правильно
        game = Game.objects.get(id=self.game.id)
        self.assertEqual(game.title, 'The Witcher 3')

    def test_game_str(self):
        # перевіряємо __str__ метод
        self.assertEqual(str(self.game), 'The Witcher 3')

    def test_game_type_default(self):
        # перевіряємо дефолтний тип гри
        game = Game.objects.create(
            title='Test Game',
            description='опис'
        )
        self.assertEqual(game.type, 'single')

    def test_game_type_choices(self):
        # перевіряємо що тип може бути online
        game = Game.objects.create(
            title='Online Game',
            description='опис',
            type='online'
        )
        self.assertEqual(game.type, 'online')

    def test_average_rating_no_ratings(self):
        # якщо ніхто не оцінив - повертає None
        result = self.game.average_rating()
        self.assertIsNone(result)

    def test_average_rating_with_ratings(self):
        """
        Передумова: є юзер і гра.
        Постумова: average_rating() повертає правильне середнє.
        """
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')

        UserGame.objects.create(user=user1, game=self.game, status='completed', rating=8)
        UserGame.objects.create(user=user2, game=self.game, status='completed', rating=6)

        # середнє = (8+6)/2 = 7.0
        avg = self.game.average_rating()
        self.assertEqual(avg, 7.0)

    def test_average_rating_ignores_null(self):
        # рейтинги без оцінки не впливають на середнє
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')

        UserGame.objects.create(user=user1, game=self.game, status='completed', rating=10)
        UserGame.objects.create(user=user2, game=self.game, status='want', rating=None)

        avg = self.game.average_rating()
        self.assertEqual(avg, 10.0)


class ProfileModelTest(TestCase):
    """
    Тестуємо модель Profile — зв'язок 1:1 з User.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')

    def test_profile_str(self):
        profile = Profile.objects.create(user=self.user, bio='Привіт')
        self.assertEqual(str(profile), 'testuser')

    def test_profile_bio(self):
        profile = Profile.objects.create(user=self.user, bio='Я геймер')
        self.assertEqual(profile.bio, 'Я геймер')

    def test_profile_one_to_one(self):
        # один юзер - один профіль
        Profile.objects.create(user=self.user)
        self.assertEqual(Profile.objects.filter(user=self.user).count(), 1)


class UserGameModelTest(TestCase):
    """
    Тестуємо модель UserGame — зв'язок User і Game.
    Передумова: є юзер і гра.
    Постумова: запис UserGame створюється з правильними полями.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='gamer', password='pass123')
        self.game = Game.objects.create(title='Dark Souls', description='Боляче')

    def test_usergame_created(self):
        ug = UserGame.objects.create(
            user=self.user,
            game=self.game,
            status='playing'
        )
        self.assertEqual(ug.status, 'playing')

    def test_usergame_str(self):
        ug = UserGame.objects.create(user=self.user, game=self.game, status='want')
        self.assertEqual(str(ug), 'gamer - Dark Souls')

    def test_usergame_rating_optional(self):
        # рейтинг необов'язковий
        ug = UserGame.objects.create(user=self.user, game=self.game, status='want')
        self.assertIsNone(ug.rating)

    def test_usergame_with_rating(self):
        ug = UserGame.objects.create(
            user=self.user, game=self.game, status='completed', rating=9
        )
        self.assertEqual(ug.rating, 9)

    def test_usergame_status_choices(self):
        # перевіряємо всі статуси
        statuses = ['want', 'playing', 'completed', 'dropped']
        for s in statuses:
            ug = UserGame.objects.create(user=self.user, game=self.game, status=s)
            self.assertEqual(ug.status, s)
            ug.delete()


class CommentModelTest(TestCase):
    """
    Тестуємо модель Comment.
    Передумова: є юзер і гра.
    Постумова: коментар створюється і лайки працюють.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='commenter', password='pass123')
        self.game = Game.objects.create(title='Minecraft', description='Кубики')
        self.comment = Comment.objects.create(
            user=self.user,
            game=self.game,
            text='Дуже крута гра!'
        )

    def test_comment_created(self):
        self.assertEqual(Comment.objects.count(), 1)

    def test_comment_str(self):
        self.assertEqual(str(self.comment), 'Comment by commenter')

    def test_comment_text(self):
        self.assertEqual(self.comment.text, 'Дуже крута гра!')

    def test_comment_likes_empty(self):
        # спочатку лайків немає
        self.assertEqual(self.comment.likes.count(), 0)

    def test_comment_like_add(self):
        # додаємо лайк
        other_user = User.objects.create_user(username='liker', password='pass123')
        self.comment.likes.add(other_user)
        self.assertEqual(self.comment.likes.count(), 1)

    def test_comment_like_remove(self):
        # прибираємо лайк
        other_user = User.objects.create_user(username='liker', password='pass123')
        self.comment.likes.add(other_user)
        self.comment.likes.remove(other_user)
        self.assertEqual(self.comment.likes.count(), 0)

    def test_comment_delete_cascade(self):
        """
        Постумова: якщо видалити гру — коментарі видаляються теж (CASCADE).
        """
        self.game.delete()
        self.assertEqual(Comment.objects.count(), 0)


class NoteModelTest(TestCase):
    """Тестуємо модель Note."""

    def setUp(self):
        self.user = User.objects.create_user(username='noter', password='pass123')
        self.game = Game.objects.create(title='GTA V', description='Відкритий світ')

    def test_note_created(self):
        note = Note.objects.create(user=self.user, game=self.game, content='Треба пройти місію 5')
        self.assertEqual(str(note), 'Note by noter')
        self.assertEqual(note.content, 'Треба пройти місію 5')


# ============================================================
# Тести для views (сторінок)
# ============================================================

class HomeViewTest(TestCase):
    """Тестуємо головну сторінку."""

    def test_home_returns_200(self):
        # головна сторінка має відкриватись без авторизації
        client = Client()
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_uses_correct_template(self):
        client = Client()
        response = client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')


class GameListViewTest(TestCase):
    """
    Тестуємо список ігор — фільтрацію, пошук, пагінацію.
    Передумова: в БД є кілька ігор.
    Постумова: сторінка відкривається і повертає правильний контекст.
    """

    def setUp(self):
        self.client = Client()
        Game.objects.create(title='Witcher', description='RPG', type='single')
        Game.objects.create(title='CS:GO', description='Шутер', type='online')
        Game.objects.create(title='Portal 2', description='Головоломка', type='coop')

    def test_game_list_returns_200(self):
        response = self.client.get(reverse('game_list'))
        self.assertEqual(response.status_code, 200)

    def test_game_list_template(self):
        response = self.client.get(reverse('game_list'))
        self.assertTemplateUsed(response, 'game_list.html')

    def test_game_list_search(self):
        # пошук по назві
        response = self.client.get(reverse('game_list'), {'q': 'Witcher'})
        self.assertEqual(response.status_code, 200)
        # в page_obj має бути тільки Witcher
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj[0].title, 'Witcher')

    def test_game_list_filter_by_type(self):
        # фільтрація по типу
        response = self.client.get(reverse('game_list'), {'type': 'online'})
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj[0].type, 'online')

    def test_game_list_search_no_results(self):
        # пошук який нічого не знаходить
        response = self.client.get(reverse('game_list'), {'q': 'нічого такого нема'})
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 0)

    def test_game_list_sort_by_title(self):
        response = self.client.get(reverse('game_list'), {'sort': 'title'})
        page_obj = response.context['page_obj']
        titles = [g.title for g in page_obj]
        self.assertEqual(titles, sorted(titles))


class GameDetailViewTest(TestCase):
    """
    Тестуємо детальну сторінку гри.
    Передумова: є гра в БД.
    Постумова: сторінка відкривається і містить правильні дані.
    """

    def setUp(self):
        self.client = Client()
        self.game = Game.objects.create(
            title='Hollow Knight',
            description='Метроідванія',
            type='single'
        )
        self.user = User.objects.create_user(username='player', password='pass123')

    def test_game_detail_returns_200(self):
        response = self.client.get(reverse('game_detail', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)

    def test_game_detail_template(self):
        response = self.client.get(reverse('game_detail', args=[self.game.id]))
        self.assertTemplateUsed(response, 'game_detail.html')

    def test_game_detail_context(self):
        # перевіряємо що в контексті є потрібні дані
        response = self.client.get(reverse('game_detail', args=[self.game.id]))
        self.assertIn('game', response.context)
        self.assertIn('comments', response.context)
        self.assertIn('avg_rating', response.context)

    def test_game_detail_wrong_id_returns_404(self):
        # неіснуючий id має повертати 404
        response = self.client.get(reverse('game_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_game_detail_add_comment(self):
        """
        Передумова: юзер авторизований.
        Постумова: коментар створюється в БД.
        """
        self.client.login(username='player', password='pass123')
        self.client.post(
            reverse('game_detail', args=[self.game.id]),
            {'text': 'Відмінна гра!'}
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().text, 'Відмінна гра!')

    def test_game_detail_comment_not_saved_if_empty(self):
        # порожній коментар не зберігається
        self.client.login(username='player', password='pass123')
        self.client.post(
            reverse('game_detail', args=[self.game.id]),
            {'text': ''}
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_game_detail_comment_requires_auth(self):
        # без авторизації POST не додає коментар
        self.client.post(
            reverse('game_detail', args=[self.game.id]),
            {'text': 'спроба без логіну'}
        )
        self.assertEqual(Comment.objects.count(), 0)


class RegisterViewTest(TestCase):
    """
    Тестуємо реєстрацію.
    Передумова: форма з username і password.
    Постумова: юзер створюється і відбувається редірект.
    """

    def setUp(self):
        self.client = Client()

    def test_register_page_returns_200(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        self.client.post(reverse('register'), {
            'username': 'newplayer',
            'password': 'secure123'
        })
        self.assertTrue(User.objects.filter(username='newplayer').exists())

    def test_register_redirects_after_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'newplayer2',
            'password': 'secure123'
        })
        # після успішної реєстрації - редірект на логін
        self.assertEqual(response.status_code, 302)

    def test_register_duplicate_username(self):
        # не можна зареєструватись з зайнятим нікнеймом
        User.objects.create_user(username='existing', password='pass123')
        response = self.client.post(reverse('register'), {
            'username': 'existing',
            'password': 'other123'
        })
        # помилка - лишається на сторінці реєстрації
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(User.objects.filter(username='existing').count(), 1)


class LoginViewTest(TestCase):
    """
    Тестуємо логін.
    Передумова: є зареєстрований юзер.
    Постумова: після логіну - редірект на головну.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='logintest', password='pass123')

    def test_login_page_returns_200(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'logintest',
            'password': 'pass123'
        })
        # після входу - редірект
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'logintest',
            'password': 'wrongpass'
        })
        # лишається на сторінці логіну з помилкою
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_login_wrong_username(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'pass123'
        })
        self.assertIn('error', response.context)


class LogoutViewTest(TestCase):
    """Тестуємо вихід з акаунту."""

    def test_logout_redirects(self):
        user = User.objects.create_user(username='logouttest', password='pass123')
        self.client.login(username='logouttest', password='pass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class AddToLibraryViewTest(TestCase):
    """
    Тестуємо додавання гри в бібліотеку.
    Передумова: юзер авторизований, гра існує.
    Постумова: запис UserGame створюється в БД.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='libraryuser', password='pass123')
        self.game = Game.objects.create(title='Sekiro', description='Складно')

    def test_add_to_library_requires_login(self):
        # без авторизації - редірект на логін
        response = self.client.get(reverse('add_to_library', args=[self.game.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_add_to_library_page_returns_200(self):
        self.client.login(username='libraryuser', password='pass123')
        response = self.client.get(reverse('add_to_library', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)

    def test_add_to_library_creates_usergame(self):
        self.client.login(username='libraryuser', password='pass123')
        self.client.post(reverse('add_to_library', args=[self.game.id]), {
            'status': 'playing',
            'rating': '8'
        })
        self.assertTrue(UserGame.objects.filter(user=self.user, game=self.game).exists())

    def test_add_to_library_status_saved(self):
        self.client.login(username='libraryuser', password='pass123')
        self.client.post(reverse('add_to_library', args=[self.game.id]), {
            'status': 'completed',
            'rating': '10'
        })
        ug = UserGame.objects.get(user=self.user, game=self.game)
        self.assertEqual(ug.status, 'completed')
        self.assertEqual(ug.rating, 10)

    def test_want_status_clears_rating(self):
        """
        Якщо статус 'want' — рейтинг не зберігається (None).
        Передумова: юзер вибирає 'Хочу пройти'.
        Постумова: rating = None в БД.
        """
        self.client.login(username='libraryuser', password='pass123')
        self.client.post(reverse('add_to_library', args=[self.game.id]), {
            'status': 'want',
            'rating': '7'
        })
        ug = UserGame.objects.get(user=self.user, game=self.game)
        self.assertIsNone(ug.rating)


class ProfileViewTest(TestCase):
    """
    Тестуємо сторінку профілю.
    Передумова: є юзер.
    Постумова: сторінка відкривається і містить дані юзера.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='profiletest', password='pass123')

    def test_profile_returns_200(self):
        response = self.client.get(reverse('profile', args=['profiletest']))
        self.assertEqual(response.status_code, 200)

    def test_profile_template(self):
        response = self.client.get(reverse('profile', args=['profiletest']))
        self.assertTemplateUsed(response, 'profile.html')

    def test_profile_wrong_user_returns_404(self):
        response = self.client.get(reverse('profile', args=['nobody_here']))
        self.assertEqual(response.status_code, 404)

    def test_profile_context_has_user_games(self):
        response = self.client.get(reverse('profile', args=['profiletest']))
        self.assertIn('user_games', response.context)


class EditCommentViewTest(TestCase):
    """
    Тестуємо редагування коментаря.
    Передумова: є коментар, юзер є його автором.
    Постумова: текст коментаря змінюється в БД.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='editor', password='pass123')
        self.game = Game.objects.create(title='Test Game', description='test')
        self.comment = Comment.objects.create(
            user=self.user, game=self.game, text='Старий текст'
        )

    def test_edit_comment_saves_new_text(self):
        self.client.login(username='editor', password='pass123')
        self.client.post(
            reverse('edit_comment', args=[self.comment.id]),
            {'text': 'Новий текст'}
        )
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Новий текст')

    def test_edit_comment_by_wrong_user_redirects(self):
        # інший юзер не може редагувати чужий коментар
        other = User.objects.create_user(username='other', password='pass123')
        self.client.login(username='other', password='pass123')
        response = self.client.post(
            reverse('edit_comment', args=[self.comment.id]),
            {'text': 'Зламати!'}
        )
        # редірект без зміни тексту
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Старий текст')


class DeleteCommentViewTest(TestCase):
    """
    Тестуємо видалення коментаря.
    Передумова: є коментар, юзер є його автором.
    Постумова: коментар видаляється з БД.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='deleter', password='pass123')
        self.game = Game.objects.create(title='Game', description='desc')
        self.comment = Comment.objects.create(
            user=self.user, game=self.game, text='Видали мене'
        )

    def test_delete_comment_removes_from_db(self):
        self.client.login(username='deleter', password='pass123')
        self.client.post(reverse('delete_comment', args=[self.comment.id]))
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_by_wrong_user_fails(self):
        other = User.objects.create_user(username='stranger', password='pass123')
        self.client.login(username='stranger', password='pass123')
        self.client.post(reverse('delete_comment', args=[self.comment.id]))
        # коментар не видалений
        self.assertEqual(Comment.objects.count(), 1)


class LikeCommentViewTest(TestCase):
    """
    Тестуємо лайки.
    Передумова: є коментар і авторизований юзер.
    Постумова: лайк додається/прибирається.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='liker', password='pass123')
        self.game = Game.objects.create(title='Liked Game', description='desc')
        self.comment = Comment.objects.create(
            user=self.user, game=self.game, text='Лайкни мене'
        )

    def test_like_adds(self):
        self.client.login(username='liker', password='pass123')
        self.client.post(reverse('like_comment', args=[self.comment.id]))
        self.assertEqual(self.comment.likes.count(), 1)

    def test_like_toggle_removes(self):
        # другий клік прибирає лайк
        self.client.login(username='liker', password='pass123')
        self.client.post(reverse('like_comment', args=[self.comment.id]))
        self.client.post(reverse('like_comment', args=[self.comment.id]))
        self.assertEqual(self.comment.likes.count(), 0)

    def test_like_requires_auth(self):
        # без авторизації - редірект
        response = self.client.post(reverse('like_comment', args=[self.comment.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.comment.likes.count(), 0)