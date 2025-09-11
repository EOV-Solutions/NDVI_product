from redis import Redis
from redis.exceptions import ConnectionError
from settings import config

from redis.sentinel import Sentinel

def is_backend_running() -> bool:
    try:
        conn = Redis(
            host='redis',
            port=6379,
            db=1,
            password='password'
        )
        conn.client_list()  
        print("Successfully connected to Redis instance at %s", config.REDIS_BACKEND)
    except ConnectionError as e:
        print("Failed to connect to Redis instance at %s", config.REDIS_BACKEND)
        print(repr(e))
        return False
    conn.close()
    return True