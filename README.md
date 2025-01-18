# API Yamdb

## Описание
Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. Список категорий может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»). 
Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). 
Добавлять произведения, категории и жанры может только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.
Пользователи могут оставлять комментарии к отзывам.
Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

**Ключевые особенности:**

*   **Верификация** Верификация по email
*   **Категории и жанры:** Произведения классифицируются по категориям и жанрам, что облегчает навигацию и поиск.
*   **Отзывы и оценки:** Пользователи могут делиться своими мнениями и оценивать произведения.
*   **Рейтинг:** Автоматический расчет среднего рейтинга произведений.
*   **Комментарии:** Возможность комментировать отзывы других пользователей.
*   **Роли:** Разграничение доступа для администраторов и обычных пользователей.
*   **Аутентификация:** Доступ к оставлению отзывов и комментариев доступен только для аутентифицированных пользователей.

## Эндпоинты API

### Аутентификация

*   `POST /api/v1/auth/signup/`
    *   **Описание:** Регистрация нового пользователя.
    *   **Параметры тела запроса (JSON):** `username`, `email`.
    *   **Ответ:**
        *   `201 Created`: Пользователь успешно зарегистрирован. В теле ответа будет `confirmation_code` для подтверждения почты.
        *   `400 Bad Request`: Ошибка при валидации данных.
*   `POST /api/v1/auth/token/`
    *   **Описание:** Получение JWT-токена.
    *   **Параметры тела запроса (JSON):** `username`, `confirmation_code`.
    *   **Ответ:**
        *   `200 OK`: Успешная аутентификация, возвращается JWT-токен.
        *   `401 Unauthorized`: Неверные учетные данные.

### Пользователи

*   `GET /api/v1/users/`
    *   **Описание:** Получить список всех пользователей (доступ Администратора).
    *   **Ответ:** `200 OK`, массив JSON с данными пользователей.
*   `POST /api/v1/users/`
   *  **Описание:** Создать нового пользователя (доступ Администратора).
   *  **Параметры тела запроса (JSON):**  `username`(обязательное поле), `email`(обязательное поле), `first_name`, `last_name`, `bio`, `role`.
   *  **Ответ:** `201 Created`, данные нового пользователя.
*   `GET /api/v1/users/{username}/`
    *   **Описание:** Получить данные пользователя по имени (доступ Администратора).
    *   **Ответ:** `200 OK`, данные пользователя в JSON.
*  `PATCH /api/v1/users/{username}/`
      * **Описание:** Обновить данные пользователя (доступ Администратора).
      * **Параметры тела запроса (JSON):** `username`, `email`, `first_name`, `last_name`, `role`.
        Параметры username и email не являются обязательным, но не могут быть пустыми.
      * **Ответ:** `200 OK`, обновленные данные пользователя.
*  `DELETE /api/v1/users/{username}/`
      *   **Описание:** Удалить пользователя (доступ Администратора).
      *  **Ответ:** `204 No Content`
*   `GET /api/v1/users/me/`
     * **Описание:** Получить данные пользователя выполняющего запрос.
    *   **Ответ:** `200 OK`, данные текущего пользователя в JSON.
*   `PATCH /api/v1/users/me/`
     *  **Описание:** Обновить данные текущего пользователя.
      * **Параметры тела запроса (JSON):** `username`, `email`, `first_name`, `last_name`, `role`.
     * **Ответ:** `200 OK`, обновленные данные пользователя.

## Как запустить проект
Клонировать репозиторий и перейти в него в командной строке:

`git clone https://github.com/Beaver-IK/api_yamdb.git`
`cd api_yamdb`

Cоздать и активировать виртуальное окружение:

`python3 -m venv env`
`source env/bin/activate`

Установить зависимости из файла requirements.txt:

`python3 -m pip install --upgrade pip`
`pip install -r requirements.txt`

Выполнить миграции:

`python3 manage.py migrate`

Запустить проект:

`python3 manage.py runserver`

Создать суперпользователя:

`python3 manage.py createsuperuser`