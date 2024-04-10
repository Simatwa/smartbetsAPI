#!/usr/bin/python3
import argparse
from . import __version__
from .configuration_handler import set_config
from appdirs import AppDirs

dirs = AppDirs("Smartwa", "smartbets_API")
program_info = "Simple football prediction API  "
epilog = "[*] This program is disseminated under GPL-3.0 license."
log_level_choices = ["debug", "info", "warning", "error", "critical"]


def parse_handler():
    parser = argparse.ArgumentParser(description=program_info, epilog=epilog)
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + "v" + __version__
    )
    parser.add_argument(
        "-u", "--username", help="Username for authenticating clients", default="API"
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Port to be used for hosting the API",
        default=8000,
        type=int,
    )
    parser.add_argument("-f", "--filename", help="Filename to be used in logging")
    parser.add_argument(
        "-l",
        "--level",
        help="Logging level",
        choices=log_level_choices,
        default="info",
        metavar="|".join(log_level_choices),
    )
    parser.add_argument(
        "--enable-proxy",
        dest="proxy",
        action="store_true",
        help="Access internet via rotating proxies",
    )
    parser.add_argument(
        "--no-net",
        action="store_true",
        help="Force the API to use cached data rather than from internet.",
    )
    parser.add_argument("--host", help="Host the API on net [LAN]", action="store_true")
    parser.add_argument(
        "--debug", help="Debug the API at web level - developers", action="store_true"
    )
    parser.add_argument(
        "--log",
        help=f"Log to a file located at {dirs.user_data_dir}",
        action="store_true",
    )
    parser.add_argument(
        "--colorize", help="Colorize the logs", action="store_true", dest="color"
    )
    parser.add_argument(
        "--gui", help="Use gui notifications [Termux]", action="store_true"
    )
    parser.add_argument("token", help="Passphrase for login authentication")
    return parser.parse_args()


args = parse_handler()
# Ensures configurations are set before importing other modules
set_config(args).main()

from .predictor import predictor
from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated

app = FastAPI(
    title="smartbetsAPI",
    summary="Worldwide soccer-matches predictor",
    version=__version__,
    description="""View official docs at [Simatwa/smartbets](https://github.com/Simatwa/smartbetsapi)""",
    license_info={
        "name": "GNUv3",
        "url": "https://github.com/Simatwa/smartbetsAPI/blob/main/LICENSE?raw=true",
    },
    contact={
        "name": "Smartwa",
        "url": "https://github.com/Simatwa",
        "email": "simatwacaleb@proton.me",
    },
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    # openapi_prefix="/v1",
)

v1_router = APIRouter(prefix="/v1", tags=["v1"])

v1_auth_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/token", description="Token set at server launch."
)


class Match(BaseModel):
    """Football match teams and net flag"""

    home: str
    away: str
    net: bool = False


class Prediction(BaseModel):
    """Match prediction"""

    g: float
    gg: float
    ov15: float
    ov25: float
    ov35: float
    choice: float
    result: str
    pick: str


def verify_token(token: Annotated[str, Depends(v1_auth_scheme)]):
    """Ensures token passed match the one set"""
    if token and token == args.token:
        return token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/")
def home():
    """Redirect to api playground"""
    return RedirectResponse("/v1/docs")


@v1_router.post("/token")
def fetch_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Fetch api token"""
    if form_data.username == args.username and form_data.password == args.token:
        return {
            "access_token": args.token,
            "token_type": "bearer",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )


@v1_router.post("/predict", dependencies=[Depends(verify_token)])
def predict(match: Match) -> Prediction:
    """Make prediction"""
    return predictor(api=True).predictorD({1: match.home, 2: match.away}, match.net)


app.include_router(v1_router)


def start_server():
    import uvicorn

    try:
        uvicorn.run(
            app,
            host="0.0.0.0" if args.host else "127.0.0.1",
            port=args.port,
            reload=args.debug,
            log_level=args.level,
        )
    except (KeyboardInterrupt, EOFError):
        pass
