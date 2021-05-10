# DWI Data Processing

Life is short, use Python3 and Container Runtimes ...

## Docker Containers

**Start Services**

Add `--build` to rebuild images

```
docker-compose up
```

The postgresql database will run at localhost:5432.

**Stop Services**

Add `-v` to clean up volumes

```
docker-compose down
```

## Development

**Attach Python Container**

```
docker exec -it app bash
```

**Environment Variables**

We use a environment file `.env` at root folder to configure our app. The python package `environ` is used for parsing these variables.

**Project Configurations**

The configurations file is `settings.py` at package folder.

**Sqlalchemy Interface**

```
>>> from app.database.utils import session_scope
>>> with session_scope('default') as session:
>>>     # Do your ORM stuff with session here!
```

## Command line tools

The interface is `manage.py` at project folder. 

Make sure you attach the python container before executing them.

* Migrate the schema to default database:

    ```
    >>> python manage.py init --db=default
    OK
    ```
