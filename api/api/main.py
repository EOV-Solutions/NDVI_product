from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from src.routers.api import router as router_api
from src import config
# from src.config import API_PREFIX, ALLOWED_HOSTS
from src.routers.handler.http_error import http_error_handler


def get_application() -> FastAPI:
    ## Start FastApi App 
    application = FastAPI(title=config.PROJECT_NAME, docs_url="/api/docs", redoc_url="/api/redoc")

    ## Mapping api routes
    # application.include_router(router_api, prefix=API_PREFIX)
    application.include_router(router_api)
    ## Add exception handlers
    application.add_exception_handler(HTTPException, http_error_handler)

    ## Allow cors
    application.add_middleware(
        CORSMiddleware,
        # allow_origins=ALLOWED_HOSTS or ["*"],
        allow_origins=["*"],

        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return application


app = get_application()