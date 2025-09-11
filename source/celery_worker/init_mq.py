from redis import Redis
from settings import config
from dotenv import load_dotenv

redis = Redis(
    host="redis", 
    port=6379, 
    password='password',
    db=1
)