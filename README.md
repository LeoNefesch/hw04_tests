# hw04_tests

[![CI](https://github.com/yandex-praktikum/hw04_tests/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw04_tests/actions/workflows/python-app.yml)


### О чём проект?
Перед Вами учебный django-проект, построенный с применением архитектуры MVT. Представляет из себя блог для публикации записей. Код проекта покрыт тестами.

**Стэк технологий:**
- Python 3.9
- django 2.2
- pytest-django
- Pillow
- django-debug-toolbar
- requests

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:LeoNefesch/hw04_tests.git
```

```
cd hw04_tests
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source v venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать пользователя с правами администратора (логин и пароль запомните, эти данные ещё понадобятся):

```
python manage.py createsuperuser
```

Запустить тестовый сервер:

```
python3 manage.py runserver
```

В браузере по адресу `http://127.0.0.1:8000/admin/` авторизоваться по логину и паролю суперпользователя.


