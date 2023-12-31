
## Описание
Проект разработан в мастерской Яндекс.Практикума. Цель проекта поднять навыки работы с DRF.

### О проекте
Проект, представляет собой шаблонизатор документов - это инструмент, который позволяет автоматизировать процесс
создания документов на основе заданных шаблонов. Этот тип приложения может быть полезен во 
многих областях, включая бизнес, юриспруденцию, образование и другие.



## Основная логика
В основе логики шаблонизатора лежит создание готовых word документов на основе шаблона. Шаблон создается по определенным правилам и хранится на сервере в виде docx файлов. В шаблонах предусмотрены возможности дополнительных обработок вводимых пользователем данных (склонения по падежам, доп форматирование и др), более подробно об этом можно глянуть в инструкции([ссылка](https://github.com/document-template-engine/demo-repository/files/13055545/_._._.docx)). На данном этабе шаблон и его поля создаются администратором. Система регистрации и авторизации построена на основе djoser, с некоторыми модификациями

Невторизированный пользователь имеет возможность:
  - просмотреть список всех доступных шаблонов базы /api/templates/
  - скачать шаблон документа /api/templates/{id}/download_draft/
  - сформировать превью документа на основе шаблона и предоставляемых данных полей и скачать его (без сохранения на сервере)  /api/templates/{id}/download_preview/

Авторизованный пользователь имеет возможность:
  - формировать документы на основании выбранного шаблона и предоставленных данных и сохранять документы на сервере
  - скачивать сохраненные документы в формате docx /api/documents/{id}/download_dpcument/
  - добавлять шаблоны или документы в избранное
  - доступ к документам и данным отдельных документов имеет только администратор или автор документа

Администратор имеет возможность:
  - загрузить информацию о новом шаблоне (наименование, описание полей) POST /api/templates/
  - обновить docx файл шаблона PUT(PATCH) /api/templates/{id}/upload_template/

### Технологии
- **Python - 3.9**
- **Django - 3.2**
- **DRF - 3.12.4**
- **PostgreSQL - 13.10**
- **Docker - 4.19**

### Авторы
- [Nikki Nikonor](https://github.com/Paymir121)
- [Тимченко Александр](https://github.com/ASTimch)
- [Скуридин Андрей](https://github.com/andrzej-skuridin)
- [Николай Петров](https://github.com/NikolayPetrow23)


## Для запуска проекта вам понадобится:

### Клонирование репозитория:
Просите разрешение у владельца репозитория( можно со слезами на глазах)
Клонируете репозиторий:

```bash
    git clone  git@github.com:document-template-engine/backend.git
```

### Cоздать  виртуальное окружение:
```
    python -m venv venv
```
# активировать виртуальное окружение, Если у вас Linux/macOS
```
    source venv/bin/activate
```
# Активировать виртуальное окружение, Если у вас windows
```
    source venv/scripts/activate
```

### Установить зависимости из файла requirements.txt:
```
    cd backend
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```


### Выполнить миграции:
```
    python manage.py makemigrations
    python manage.py migrate
```

### Запустить проект:
```
    python manage.py runserver
```

### Создать суперпользователя:
```
    python manage.py createsuperuser
```

### Добавить темлейтов в базу:
```
    python manage.py init_field_types
    python manage.py init_templates

```

## Запуск докер контейнеров на локальной машине:

### Билдим проект и запускаем:
```
    docker compose up --build
```

### Выполнить миграции:
```
    docker compose exec backend python manage.py migrate
```

### Выполнить создание суперпользователя:
```
    docker compose exec backend python manage.py createsuperuser
```

### Выполнить Собрать статику Django:
```
    sudo docker compose  exec backend python manage.py collectstatic
    sudo docker compose  exec backend cp -r /app/collected_static/. /app/static/
```

## Запуск докер контейнеров на удаленной машине:

### Выполнить обновление apt:
```
    sudo apt update
```

### Билдим проект и запускаем:
```
    sudo docker compose -f docker-compose.production.yml up --build
```

### Выполнить миграции:
```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

### Выполнить миграции:
```
    docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

### Выполнить Собрать статику Django:
```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /app/static/
```

### Выполнить миграции:
```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py init_field_types
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py init_templates
```

### Настройки nginx:
```
    sudo nano /etc/nginx/sites-enabled/default
```

## Примеры запросов и ответов к API

### Регистрация
#### Endpoint
```
    POST  api/v1/users/
```
#### Пример запроса
```
{
    "email": "user@mail.ru",
    "password": "testuser123"
}
```
#### Пример ответа
```
{
    "id": 1, 
    "email": "user@mail.ru"
}
```

### Аутентификация
#### Endpoint
```
    POST  api/v1/auth/token/login/
```

#### Пример запроса 
```
{
    "email": "user@mail.ru",
    "password": "testuser123"
}
```

#### Пример ответа
```
{
    "auth_token": "7d577706781e1cf230b79813688a85193682b1ff"
}
```

### Узнать свои данные
#### Endpoint.
```
    GET  api/v1/users/me/
```

#### Пример ответа
```
{
    "id": 1,
    "email": "user@mail.ru"
}
```

### Просмотр списка пользователей
#### Endpoint
```
    GET  api/v1/users/
```

#### Пример ответа.
```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "email": "user@mail.ru"
        },
        {
            "id": 2,
            "email": "user_2@mail.ru"
        }
    ]
}
```
