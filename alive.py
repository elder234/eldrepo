from logging import (
    basicConfig,
    getLogger,
    INFO,
)
from os import environ
from requests import get
from time import sleep

basicConfig(
    format="{asctime} - [{levelname[0]}] {name} [{module}:{lineno}] - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=INFO,
)

LOGGER = getLogger("Alive")

def sendRequest(url: str) -> None:
    request = get(
        url=url,
        headers=dict({
            "User-Agent": "Not a RoBot"
        }),
        timeout=10
    )

    if not request.ok:
        raise Exception(f"[{request.status_code}] {request.text}")

try:
    BASE_URL_PORT = environ.get("PORT", "")
    HEROKU_APP_NAME = environ.get("HEROKU_APP_NAME", "")
    RENDER_APP_NAME = environ.get("RENDER_APP_NAME", "")
    if len(HEROKU_APP_NAME) != 0:
        if "://" in HEROKU_APP_NAME:
            BASE_URL = HEROKU_APP_NAME
        else:
            BASE_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com"
    
    elif len(RENDER_APP_NAME) != 0:
        if "://" in RENDER_APP_NAME:
            BASE_URL = RENDER_APP_NAME
        else:
            BASE_URL = f"https://{RENDER_APP_NAME}.onrender.com"
    
    else:
        raise Exception("Auto Alive is not set up correctly! Don't forget to add HEROKU_APP_NAME or RENDER_APP_NAME to prevent the Apps got shutdown!")
        
    if (
        BASE_URL 
        and len(BASE_URL_PORT) != 0
    ):
        while True:
            sendRequest(BASE_URL)
            sleep(300)

except Exception as error:
    LOGGER.error(error)
