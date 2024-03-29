### YaMDb

## Описание
Проект YaMDb позволяет собирать отзывы и комментарии к произведениям. У пользователей есть возможность оставить свой отзыв, поставить произведению оценку, комментировать отзывы.
Произведения могут быть сгруппированы по категориями (например, "Книги", "Фильмы", "Музыка"). Проект не хранит сами произведения.

Внесение в базу данных произведений, создание категорий и жанров доступно только администратору.

## Запуск проекта

* Клонировать репозиторий, перейти к репозиторию в командной строке

```
git clone git@github.com:Aleksey-Lyap/api_yamdb.git
```
```
cd api_yamdb
```
* Создать и активировать виртуальное окружение
```
python3 -m venv venv
```
* Для Linux/MacOS: `source venv/bin/activate`
* Если у вас Windows `source venv/Scripts/activate`

* Установить зависимости из requirements.txt
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
* Выполнить миграции
```
python3 manage.py migrate
```
* Запустить проект
```
python3 manage.py runserver
```

## API

Для управления записями проект использует API. Поддерживается версионность API (актуальная версия: `v1`)

Документация API доступна по адресу ```/redoc/```

Примеры запросов:

* Получение списка всех произведений

**Запрос**: `GET /titles/`

**Ответ (200)**: 
```json
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "name": "string",
      "year": 0,
      "rating": 0,
      "description": "string",
      "genre": [
        {
          "name": "string",
          "slug": "string"
        }
      ],
      "category": {
        "name": "string",
        "slug": "string"
      }
    }
  ]
}
```
* Создание отзыва

**Запрос**: `POST /titles/{title_id}/reviews/`
```json
{
  "text": "string",
  "score": 1
}
```
**Ответ (200)**:
```json
{
  "id": 0,
  "text": "string",
  "author": "string",
  "score": 1,
  "pub_date": "2019-08-24T14:15:22Z"
}
```

## Права доступа
Проект поддерживает следующие роли пользователей:

1) `Аноним` — может просматривать описания произведений, читать отзывы и комментарии.
2) Аутентифицированный пользователь (`user`) — имеет те же права, что и Аноним, также может публиковать отзывы и ставить оценки произведениям, может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Роль присваивается по умолчанию каждому новому пользователю.
3) Модератор (`moderator`) — те же права, что и у Аутентифицированного пользователя, а также право удалять и редактировать любые отзывы и комментарии.
4) Администратор (`admin`) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.

## Регистрация и создание пользователей
Проект поддерживает создание пользователей администратором и самостоятельную регистрацию.

1) Создание новых пользователей администратором
* Через админ-зону сайта (`/admin/`)

либо

* Путем POST-запроса на эндпоинт `api/v1/users/`
* Пользователь направляет свои `email` и `username` на эндпоинт `/api/v1/auth/signup/`, в ответ ему должно прийти письмо с кодом подтверждения.
* Далее пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит `token` (`JWT-токен`), как и при самостоятельной регистрации.

2) Самостоятельная регистрация

* Пользователь отправляет POST-запрос с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.
* Сервис `YaMDB` отправляет письмо с кодом подтверждения (`confirmation_code`) на указанный адрес `email`.
    Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит `token` (`JWT-токен`).
* Полученный токен следует отправлять с каждым запросом
* После регистрации и получения токена пользователь может отправить PATCH-запрос на эндпоинт `/api/v1/users/me/` и заполнить поля в своём профайле (описание полей — в документации).
