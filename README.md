# GameLog

GameLog — це веб-додаток для ведення щоденника геймера з можливістю додавання ігор, відстеження прогресу проходження, оцінювання, коментування та взаємодії між користувачами.

## Функціонал

- Реєстрація та авторизація користувачів
- Перегляд списку ігор (List Page)
- Пошук, фільтрація та сортування
- Детальна сторінка гри (Detail Page)
- Додавання ігор у бібліотеку
- Встановлення статусу (хочу пройти / проходжу / пройшов / кинув)
- Оцінювання ігор
- Коментарі та лайки
- Профіль користувача зі статистикою
- Адмін-панель

## Технології

- Python
- Django
- SQLite
- GitHub

## Документація

- Технічне завдання: `docs/technical_specification.md`

## UML діаграми
### Use Case
```mermaid
graph TD
    User([Користувач])
    Admin([Адміністратор])

    subgraph auth [Авторизація]
        Register[Реєстрація]
        Login[Вхід в систему]
        Logout[Вихід]
    end

    subgraph games [Робота з іграми]
        ViewList[Перегляд списку ігор]
        Search[Пошук за назвою]
        Filter[Фільтрація за типом]
        Sort[Сортування]
        ViewDetail[Перегляд деталей гри]
    end

    subgraph library [Бібліотека]
        AddToLib[Додати гру в бібліотеку]
        SetStatus[Встановити статус]
        SetRating[Виставити оцінку]
    end

    subgraph comments [Коментарі]
        WriteComment[Написати коментар]
        EditComment[Редагувати коментар]
        DeleteComment[Видалити коментар]
        LikeComment[Лайкнути коментар]
    end

    subgraph profile [Профіль]
        ViewProfile[Переглянути профіль]
        ViewStats[Статистика ігор]
    end

    subgraph admin [Адмін-панель]
        ManageGames[Керування іграми]
        ManageUsers[Керування користувачами]
        ModerateComments[Модерація коментарів]
    end

    User --> Register
    User --> Login
    User --> Logout
    User --> ViewList
    User --> Search
    User --> Filter
    User --> Sort
    User --> ViewDetail
    User --> AddToLib
    User --> SetStatus
    User --> SetRating
    User --> WriteComment
    User --> EditComment
    User --> DeleteComment
    User --> LikeComment
    User --> ViewProfile
    User --> ViewStats

    Admin --> ManageGames
    Admin --> ManageUsers
    Admin --> ModerateComments
    Admin --> Login
```

### Class Diagram
```mermaid
classDiagram
    class User {
        +int id
        +str username
        +str password
    }

    class Profile {
        +int id
        +ImageField avatar
        +str bio
        +__str__() str
    }

    class Game {
        +int id
        +str title
        +str description
        +DateField release_date
        +str type
        +ImageField image
        +__str__() str
        +average_rating() float
    }

    class UserGame {
        +int id
        +str status
        +int rating
        +__str__() str
    }

    class Comment {
        +int id
        +str text
        +DateTimeField created_at
        +__str__() str
    }

    class Note {
        +int id
        +str content
        +__str__() str
    }

    User "1" --> "1" Profile : має
    User "1" --> "0..*" UserGame : додає
    User "1" --> "0..*" Comment : пише
    User "1" --> "0..*" Note : створює
    User "0..*" --> "0..*" Comment : лайкає

    Game "1" --> "0..*" UserGame : входить в
    Game "1" --> "0..*" Comment : має
    Game "1" --> "0..*" Note : має
```

### Sequence Diagram
```mermaid
sequenceDiagram
    actor User as Користувач
    participant Browser as Браузер
    participant View as views.py
    participant DB as База даних

    User->>Browser: Відкриває сторінку гри /games/1/
    Browser->>View: GET /games/1/
    View->>DB: Game.objects.get(id=1)
    DB-->>View: об'єкт Game
    View->>DB: UserGame.objects.get(user, game)
    DB-->>View: in_library = False
    View-->>Browser: game_detail.html
    Browser-->>User: Показує кнопку Додати в бібліотеку

    User->>Browser: Натискає Додати в бібліотеку
    Browser->>View: GET /games/1/add/
    View-->>Browser: add_to_library.html
    Browser-->>User: Показує форму зі статусом і оцінкою

    User->>Browser: Вибирає статус completed оцінка 9
    Browser->>View: POST /games/1/add/ status=completed rating=9
    View->>DB: UserGame.objects.get_or_create(user, game)
    DB-->>View: створено новий запис
    View->>DB: user_game.status = completed
    View->>DB: user_game.rating = 9
    View->>DB: user_game.save()
    DB-->>View: збережено
    View-->>Browser: redirect /games/1/
    Browser-->>User: Показує в бібліотеці
```

## Команда

- Ільчук  
- Дорощенков  
- Пахольчук  