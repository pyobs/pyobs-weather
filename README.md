## Start redis and celery

    redis-server
    celery -A [project-name] worker --beat --scheduler django --loglevel=info 
