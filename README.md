# Проект YaTube

## Описание
Социальная сеть с возможностью просмотра, создания, редактирования и 
удаления подписок на авторов. 

## Технологический стек
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)](https://www.djangoproject.com/)
[![Django ORM](https://img.shields.io/badge/-Django%20ORM-464646?style=for-the-badge&logo=Django&logoColor=green)](https://docs.djangoproject.com/en/4.0/topics/db/models/)
[![pytest](https://img.shields.io/badge/-pytest-464646?style=for-the-badge&logo=Pytest&logoColor=56C0C0&color=008080)](https://docs.pytest.org/en/7.0.x/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
## Реализованные функции
- Выведены изображения к постам
- Создана система комментариев под постами
- Реализовано кеширование отдельныз страниц
- Реализована регистрация пользователей с проверкой данных, сменой и 
  восстановлением пароля через почту
- Реализована пагинация
- Добавлено покрытие тестами

## Созданные страницы
- Главная страница
- Страница автора (со списком постов)
- Страница группы
- Страница поста
- Набор страниц для регистрации, авторизации, восстановления пароля и т.д.
- Статические страницы
- Страницы ошибок (404, 403)

## Запуск приложения
1. Установить зависимости из ```requirements.txt``` в корневом каталоге
```
pip install -r requirements.txt
```
2. Создать и применить миграции, перейдя в каталог yatube (с файлом manage.py)
```
python manage.py makemigrations
python manage.py migrate
```
3. Создать суперпользователя для доступа к панели администратора
```
python manage.py createsuperuser
```
4. Запустите приложение:
```
python manage.py runserver
```
## Автор
Dvkonstantinov
Telegram: https://t.me/Dvkonstantinov