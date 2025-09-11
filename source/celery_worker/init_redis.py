from redis import Redis
from redis.exceptions import ConnectionError
from settings import config

from redis.sentinel import Sentinel

REDIS_PASSWORD = 'EovdcRedis2025'

def is_backend_running() -> bool:
    try:
        sentinel = Sentinel(
            [('redis-sentinel.eovdc.svc.cluster.local', 26379)],
            socket_timeout=0.5,
            password=REDIS_PASSWORD,
            sentinel_kwargs={"password": REDIS_PASSWORD}
        )

        # Lấy master từ sentinel
        conn = sentinel.master_for(
            'mymaster',
            socket_timeout=0.5,
            password=REDIS_PASSWORD,
            db=1
        )

        # test lệnh client_list
        conn.client_list()
        print(f"✅ Successfully connected to Redis master via Sentinel at {config.REDIS_BACKEND}")
    except ConnectionError as e:
        print(f"❌ Failed to connect to Redis via Sentinel at {config.REDIS_BACKEND}")
        print(repr(e))
        return False
    except Exception as e:
        print("⚠️ Unexpected error:", repr(e))
        return False

    conn.close()
    return True