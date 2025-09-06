from redis import Redis
from src import config
from celery import Celery
from redis.sentinel import Sentinel

REDIS_PASSWORD = 'eovdc@2025$%'

sentinel = Sentinel(
    [('redis-sentinel.eovdc.svc.cluster.local', 26379)],
    socket_timeout=0.5,
    password=REDIS_PASSWORD,
    sentinel_kwargs={"password":REDIS_PASSWORD}
)

redis = sentinel.master_for(
    'mymaster',
    socket_timeout=0.5,
    password=REDIS_PASSWORD,   
    db=0
)


# redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, password=config.REDIS_PASSWORD, db= config.REDIS_DB)
redis.set('celery', 'ready')
celery_execute = Celery(broker=config.BROKER, backend=config.REDIS_BACKEND)