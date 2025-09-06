from redis import Redis
from redis.exceptions import ConnectionError
from settings import config


def is_backend_running() -> bool:
    try:
        conn = Redis(
            host=config.REDIS['host'],
            port=int(config.REDIS['port']),
            db=int(config.REDIS['db']),
            password=config.REDIS['pass']
        )
        conn.client_list()  # Must perform an operation to check connection.
        print("Successfully connected to Redis instance at %s", config.REDIS_BACKEND)
    except ConnectionError as e:
        print(config.REDIS['host'])
        print(config.REDIS['pass'])
        print("Failed to connect to Redis instance at %s", config.REDIS_BACKEND)
        print(repr(e))
        return False
    conn.close()
    return True