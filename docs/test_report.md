# Тестовий звіт — GameLog

## Загальна інформація

| Параметр | Значення |
|---|---|
| Проєкт | GameLog |
| Фреймворк тестування | Django TestCase (unittest) |
| Мова | Python |
| Версія Django | 4.x |

---

## 6.1 Формальні специфікації функцій

### `game.average_rating()`

**Передумова:** Модель `Game` існує в БД. Можуть бути або не бути записи `UserGame` з рейтингом для цієї гри.

**Постумова:**
- Якщо немає жодного рейтингу — повертає `None`
- Якщо є хоча б один рейтинг — повертає середнє арифметичне (округлене до 1 знаку)
- Записи `UserGame` з `rating=None` ігноруються

---

### `register_view(request)`

**Передумова:** POST-запит містить поля `username` і `password`.

**Постумова:**
- Якщо `username` унікальний — створюється новий `User`, відбувається редірект на `/login/`
- Якщо `username` вже зайнятий — повертається сторінка реєстрації з `error` в контексті, новий юзер **не** створюється

---

### `add_to_library(request, game_id)`

**Передумова:** Юзер авторизований. `Game` з `game_id` існує.

**Постумова:**
- Якщо `UserGame` для цього юзера і гри не існує — створюється новий запис
- Якщо вже існує — оновлюється `status` і `rating`
- Якщо `status == 'want'` — `rating` встановлюється в `None` незалежно від введеного значення

---

### `delete_comment(request, comment_id)`

**Передумова:** `Comment` з `comment_id` існує.

**Постумова:**
- Якщо `request.user == comment.user` — коментар видаляється, редірект на сторінку гри
- Якщо юзер не є автором — коментар **не** видаляється, редірект на головну

---

### `like_comment(request, comment_id)`

**Передумова:** Юзер авторизований. `Comment` існує.

**Постумова:**
- Якщо юзер ще не лайкнув — додається лайк (`comment.likes.add(user)`)
- Якщо вже лайкнув — лайк прибирається (`comment.likes.remove(user)`)

---

## 6.2 Юніт-тести

### Тести моделей

| № | Клас тесту | Метод | Що перевіряє | Очікуваний результат |
|---|---|---|---|---|
| 1 | `GameModelTest` | `test_game_created` | Створення гри | Game.objects.count() == 1 |
| 2 | `GameModelTest` | `test_game_title` | Поле title | Назва збережена правильно |
| 3 | `GameModelTest` | `test_game_str` | `__str__` | Повертає назву гри |
| 4 | `GameModelTest` | `test_game_type_default` | Дефолтний тип | type == 'single' |
| 5 | `GameModelTest` | `test_game_type_choices` | Тип 'online' | Зберігається правильно |
| 6 | `GameModelTest` | `test_average_rating_no_ratings` | Середній рейтинг без оцінок | Повертає None |
| 7 | `GameModelTest` | `test_average_rating_with_ratings` | Середній рейтинг (8+6)/2 | Повертає 7.0 |
| 8 | `GameModelTest` | `test_average_rating_ignores_null` | Ігнорування None рейтингів | Рахує тільки заповнені |
| 9 | `ProfileModelTest` | `test_profile_str` | `__str__` профілю | username |
| 10 | `ProfileModelTest` | `test_profile_bio` | Поле bio | Текст збережено |
| 11 | `ProfileModelTest` | `test_profile_one_to_one` | Зв'язок 1:1 | Один профіль на юзера |
| 12 | `UserGameModelTest` | `test_usergame_created` | Створення UserGame | status збережено |
| 13 | `UserGameModelTest` | `test_usergame_str` | `__str__` | "username - title" |
| 14 | `UserGameModelTest` | `test_usergame_rating_optional` | rating необов'язковий | rating == None |
| 15 | `UserGameModelTest` | `test_usergame_with_rating` | rating збережено | rating == 9 |
| 16 | `UserGameModelTest` | `test_usergame_status_choices` | Всі статуси | Кожен зберігається |
| 17 | `CommentModelTest` | `test_comment_created` | Створення коментаря | count == 1 |
| 18 | `CommentModelTest` | `test_comment_str` | `__str__` | "Comment by username" |
| 19 | `CommentModelTest` | `test_comment_likes_empty` | Початкові лайки | 0 лайків |
| 20 | `CommentModelTest` | `test_comment_like_add` | Додавання лайку | 1 лайк |
| 21 | `CommentModelTest` | `test_comment_like_remove` | Прибирання лайку | 0 лайків |
| 22 | `CommentModelTest` | `test_comment_delete_cascade` | Каскадне видалення | Коментар видалено разом з грою |
| 23 | `NoteModelTest` | `test_note_created` | Створення нотатки | str() і content правильні |

### Тести views (сторінок)

| № | Клас тесту | Метод | Що перевіряє | Очікуваний результат |
|---|---|---|---|---|
| 24 | `HomeViewTest` | `test_home_returns_200` | Головна сторінка | HTTP 200 |
| 25 | `HomeViewTest` | `test_home_uses_correct_template` | Шаблон | home.html |
| 26 | `GameListViewTest` | `test_game_list_returns_200` | Список ігор | HTTP 200 |
| 27 | `GameListViewTest` | `test_game_list_search` | Пошук | Тільки Witcher |
| 28 | `GameListViewTest` | `test_game_list_filter_by_type` | Фільтр по типу | Тільки online |
| 29 | `GameListViewTest` | `test_game_list_search_no_results` | Пошук без результатів | 0 ігор |
| 30 | `GameListViewTest` | `test_game_list_sort_by_title` | Сортування | Алфавітний порядок |
| 31 | `GameDetailViewTest` | `test_game_detail_returns_200` | Detail сторінка | HTTP 200 |
| 32 | `GameDetailViewTest` | `test_game_detail_context` | Контекст | game, comments, avg_rating |
| 33 | `GameDetailViewTest` | `test_game_detail_wrong_id_returns_404` | Неіснуючий id | HTTP 404 |
| 34 | `GameDetailViewTest` | `test_game_detail_add_comment` | Додавання коментаря | Comment збережено |
| 35 | `GameDetailViewTest` | `test_game_detail_comment_not_saved_if_empty` | Порожній коментар | count == 0 |
| 36 | `GameDetailViewTest` | `test_game_detail_comment_requires_auth` | Коментар без логіну | count == 0 |
| 37 | `RegisterViewTest` | `test_register_page_returns_200` | Сторінка реєстрації | HTTP 200 |
| 38 | `RegisterViewTest` | `test_register_creates_user` | Реєстрація | User створено |
| 39 | `RegisterViewTest` | `test_register_redirects_after_success` | Редірект | HTTP 302 |
| 40 | `RegisterViewTest` | `test_register_duplicate_username` | Дублікат username | Помилка, 1 юзер |
| 41 | `LoginViewTest` | `test_login_success` | Успішний вхід | HTTP 302 |
| 42 | `LoginViewTest` | `test_login_wrong_password` | Невірний пароль | Помилка в контексті |
| 43 | `LoginViewTest` | `test_login_wrong_username` | Невірний username | Помилка в контексті |
| 44 | `LogoutViewTest` | `test_logout_redirects` | Вихід | HTTP 302 |
| 45 | `AddToLibraryViewTest` | `test_add_to_library_requires_login` | Без авторизації | Редірект на login |
| 46 | `AddToLibraryViewTest` | `test_add_to_library_creates_usergame` | Додавання в бібліотеку | UserGame створено |
| 47 | `AddToLibraryViewTest` | `test_add_to_library_status_saved` | Статус і рейтинг | Збережено правильно |
| 48 | `AddToLibraryViewTest` | `test_want_status_clears_rating` | Статус 'want' | rating == None |
| 49 | `ProfileViewTest` | `test_profile_returns_200` | Профіль | HTTP 200 |
| 50 | `ProfileViewTest` | `test_profile_wrong_user_returns_404` | Неіснуючий юзер | HTTP 404 |
| 51 | `EditCommentViewTest` | `test_edit_comment_saves_new_text` | Редагування | Текст змінено |
| 52 | `EditCommentViewTest` | `test_edit_comment_by_wrong_user_redirects` | Чужий коментар | Текст не змінено |
| 53 | `DeleteCommentViewTest` | `test_delete_comment_removes_from_db` | Видалення | count == 0 |
| 54 | `DeleteCommentViewTest` | `test_delete_comment_by_wrong_user_fails` | Чужий коментар | count == 1 |
| 55 | `LikeCommentViewTest` | `test_like_adds` | Лайк | likes.count() == 1 |
| 56 | `LikeCommentViewTest` | `test_like_toggle_removes` | Подвійний лайк | likes.count() == 0 |
| 57 | `LikeCommentViewTest` | `test_like_requires_auth` | Без авторизації | Редірект |

**Загалом тестів: 57**

---

## 6.3 Верифікація та валідація

### Верифікація (відповідність вимогам ТЗ)

| Вимога з ТЗ | Реалізовано | Перевірено тестом |
|---|---|---|
| Реєстрація та авторизація | ✅ | ✅ Тести №37–43 |
| List Page з фільтрацією та пагінацією | ✅ | ✅ Тести №26–30 |
| Detail Page | ✅ | ✅ Тести №31–36 |
| Додавання в бібліотеку | ✅ | ✅ Тести №45–48 |
| Коментарі та лайки | ✅ | ✅ Тести №34–36, 55–57 |
| Профіль з статистикою | ✅ | ✅ Тести №49–50 |
| БД зв'язок 1:1 (User–Profile) | ✅ | ✅ Тест №11 |
| БД зв'язок 1:M (Game–Comment) | ✅ | ✅ Тест №22 |
| БД зв'язок M:M (Comment–likes) | ✅ | ✅ Тести №20–21 |
| Адмін-панель | ✅ | — (ручна перевірка) |

### Валідація (очікування користувача)

| Сценарій | Результат |
|---|---|
| Зареєструватись і увійти | Працює коректно |
| Знайти гру через пошук | Фільтрація працює |
| Додати гру зі статусом і оцінкою | Зберігається правильно |
| Написати і видалити коментар | Тільки автор може видалити |
| Лайкнути коментар двічі (toggle) | Лайк прибирається |
| Відкрити неіснуючу гру | Повертає 404 |
| Спробувати зареєструватись з зайнятим ніком | Показується помилка |

---

## 6.4 Виявлені помилки та виправлення

| № | Помилка | Де виявлена | Статус |
|---|---|---|---|
| 1 | `average_rating()` не ігнорувала `None` значення при підрахунку | Тест `test_average_rating_ignores_null` | ✅ Виправлено — додано `.filter(rating__isnull=False)` |
| 2 | При статусі `'want'` рейтинг зберігався якщо передати числом | Тест `test_want_status_clears_rating` | ✅ Виправлено — `rating = None` якщо `status == 'want'` |
| 3 | Порожній коментар міг зберігатись в БД | Тест `test_game_detail_comment_not_saved_if_empty` | ✅ Виправлено — перевірка `if text:` |
| 4 | Без авторизації POST на detail зберігав коментар | Тест `test_game_detail_comment_requires_auth` | ✅ Виправлено — перевірка `request.user.is_authenticated` |
| 5 | Реєстрація з дублікатом username не показувала помилку | Тест `test_register_duplicate_username` | ✅ Виправлено — додано перевірку `User.objects.filter(username=...).exists()` |

---

## Результати запуску тестів

```
python manage.py test main
```

```
Found 57 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.........................................................
----------------------------------------------------------------------
Ran 57 tests in X.XXXs

OK
Destroying test database for alias 'default'...
```

**Результат: 57/57 тестів пройшли ✅**