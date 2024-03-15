import os

from fastapi import FastAPI
from uvicorn import Config, Server

import cookieserver

App = FastAPI()

App.include_router(cookieserver.router, prefix=cookieserver.ROOT)

if __name__ == '__main__':
    COOKIE_CLOUD_PORT = int(os.getenv('COOKIE_CLOUD_PORT', 10375))
    Server = Server(
        Config(App, host="0.0.0.0", port=COOKIE_CLOUD_PORT, reload=False))
    Server.run()
