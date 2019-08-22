## Start redis and celery

    redis-server
    celery -A pyobs_weather worker --beat --scheduler django --loglevel=info 
