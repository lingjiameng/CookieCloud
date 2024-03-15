import gzip
from typing import Callable, Union, Optional, Dict, Any

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute
from pydantic import BaseModel
import urllib.request
import json

import uvicorn
from uvicorn import Config
import cookieserver

App = FastAPI()

App.include_router(cookieserver.router, prefix="/cookiecloud")

if __name__ == '__main__':
    Server = uvicorn.Server(
        Config(App, host="0.0.0.0", port=10375, reload=False, workers=2))
    Server.run()
