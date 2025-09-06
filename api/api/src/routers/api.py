from fastapi import APIRouter

from ..config import ROUTE_PREFIX_V1

from . import  router_v1

router = APIRouter()

def include_api_routes():
    ''' Include to router all api rest routes with version prefix '''
    router.include_router(router_v1.router)

include_api_routes()