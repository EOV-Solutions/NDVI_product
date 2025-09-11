from redis import Redis
from settings import config
from dotenv import load_dotenv

# redis = Redis(
#     host="redis", 
#     port=6379, 
#     password='password',
#     db=1
# )

from redis.sentinel import Sentinel

REDIS_PASSWORD = 'EovdcRedis2025'

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