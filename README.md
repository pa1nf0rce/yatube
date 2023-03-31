# hw05_final

### Описание проекта
>>
Проект социальной сети Yatube. 
Позволяет публиковать собственные заметки и размещать к ним фото или любую другую картинку. Также можно смотреть и комментировать заметки других пользователей,
подписываться на понравившихся авторов. 
### Технологии
 - Python 3.7
 - Django 2.2.16
 - Pillow 8.3.1
 - Unittest


### Как запустить проект:

Клонировать репозиторий:

```
git clone https://github.com/pa1nf0rce/hw05_final.git
```

Перейти в папку hw05_final/
```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Перейти в папку hw05_final/yatube/
```
cd yatube/
```

Создать и запустить миграции
```
python manage.py makemigrations
python manage.py migrate
```

Запустить локальный сервер
```
python manage.py runserver
```
Тепкрь проект будет доступен по адресу http://127.0.0.1:8000/ в браузере



### Что могут делать пользователи:

**Зарегистрированные пользователи могут:
1. Просматривать, публиковать, удалять и редактировать свои публикации;
2. Просматривать, информацию о сообществах;
3. Просматривать, публиковать комментарии от своего имени к публикациям других пользователей (включая самого себя), удалять и редактировать свои комментарии;
4. Подписываться на других пользователей и просматривать свои подписки.

**Анонимные пользователи могут:
1. Просматривать, публикации;
2. Просматривать, информацию о сообществах;
3. Просматривать, комментарии;

### Набор доступных адресов:
* ```posts/``` - отображение постов и публикаций.
* ```posts/{id}``` - Получение, изменение, удаление поста с соответствующим id.
* ```posts/{post_id}/comments/``` - Получение комментариев к посту с соответствующим post_id и публикация новых комментариев.
* ```posts/{post_id}/comments/{id}``` - Получение, изменение, удаление комментария с соответствующим id к посту с соответствующим post_id.
* ```posts/groups/``` - Получение описания зарегестрированных сообществ.
* ```posts/groups/{id}/``` - Получение описания сообщества с соответствующим id.
* ```posts/follow/``` - Получение информации о подписках текущего пользователя, создание новой подписки на пользователя.

## :office_worker: Автор: 
[Авраменко Роман](https://github.com/pa1nf0rce)


