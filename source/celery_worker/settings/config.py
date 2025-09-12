import configparser
import datetime
import pytz 
import os 
from dotenv import load_dotenv

# Load .env
load_dotenv(".env")
# cfg = configparser.ConfigParser(interpolation=None)
# cfg.read('./env.ini')


#=========================================================================
#                           TIMING CONFIG
#=========================================================================
u = datetime.datetime.utcnow()
u = u.replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh"))

#=========================================================================
#                          PROJECT INFORMATION 
#=========================================================================
# PROJECT = cfg['project']
# BE_HOST = PROJECT['be_host']
# BE_PORT = PROJECT['be_port']

#=========================================================================
#                          REDIS INFORMATION 
#=========================================================================


REDIS_BACKEND = "redis://:{password}@{hostname}:{port}/{db}".format(
    hostname=os.getenv("REDIS_HOST","redis"),
    password=os.getenv("REDIS_PASS", "password"),
    port=os.getenv("REDIS_PORT",  6379),
    db=os.getenv("REDIS_DB", 1)
)

#=========================================================================
#                          BROKER INFORMATION 
#=========================================================================
BROKER = "amqp://{user}:{pw}@{hostname}:{port}/{vhost}".format(
    user=os.getenv("RABBITMQ_USER", "guest"),
    pw=os.getenv("RABBITMQ_PASS", "guest"),
    hostname=os.getenv("RABBITMQ_HOST","rabbitmq"),
    port=os.getenv("RABBITMQ_PORT","5672"),
    vhost=os.getenv("RABBITMQ_VHOST", "")
)