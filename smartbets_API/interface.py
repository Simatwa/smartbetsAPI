#!/usr/bin/python3
import argparse
from . import __version__
from .configuration_handler import set_config
from appdirs import AppDirs

dirs = AppDirs("Smartwa", "smartbets_API")
program_info = "Simple football prediction API  "
epilog = "[*] This program is disseminated under GPL-3.0 license."


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
        choices=[0, 10, 20, 30, 40, 50],
        type=int,
        default=20,
        metavar="0-50",
    )
    parser.add_argument(
        "--enable-proxy",
        dest='proxy',
        action='store_true',
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
    parser.add_argument("password", help="Passphrase for login authentication")
    return parser.parse_args()


args = parse_handler()
# Ensures configurations are set before importing other modules
set_config(args).main()
import logging
from flask import *
from .predictor import predictor
from .bet_common import logging, col
from random import sample
from hashlib import sha256

cookie_jar, dat = {}, []

for x in range(65, 126, 1):
    dat.append(chr(x))

app = Flask(__name__)


@app.errorhandler(500)
def internal_error(e):
    return str(e), 500


# Generates cookie value
def cookie_value():
    genVals = lambda amt: "".join(sample(dat, amt))
    id, value = (genVals(7), sha256(genVals(14).encode()).hexdigest())
    cookie_jar[id] = value
    logging.debug(f"Assigning cookie - id [{id}] : {request.remote_addr}")
    logging.debug(f"Total logins [{len(cookie_jar)}]")
    return id, value


# Interacts with the predictor
def hunter(h: str, a: str, net: bool) -> dict:
    logging.debug(f"BET : {request.remote_addr} : {h}-{a}")
    return jsonify(predictor(api=True).predictorD({1: h, 2: a}, verifyNet(net)))


# Converts net-arg parsed to bool (data-type)
def verifyNet(arg):
    arg = str(arg).lower()
    if arg in ("false", "0", "none"):
        return False
    else:
        return True


# Handles request error
def error(msg: str, comment=None):
    logging.debug(f"INVALID {request.remote_addr} : {msg}")
    return jsonify({"message": msg, "comment": comment})


def bad_request() -> tuple:
    info = "Kindly pass team names"
    help = "Params {home:home-team, away:away-team, net:(true/false)}"
    return error(info, help), 400


# Home route
@app.route("/")
def home():
    return error("Dormant path", "Paths available [/login,/predict]"), 404


# Route to the predictor
@app.route("/predict", methods=["GET", "POST"])
def responser():
    verified = False
    try:
        id = request.cookies.get("id")
        value = request.cookies.get("value")
        if all([id, value]) and cookie_jar[id] == value:
            verified = True
    except KeyError:
        return error("Kindly login!"), 401
    if verified:
        if request.method == "GET":
            h_team = request.args.get("home")
            a_team = request.args.get("away")
            net = False if args.no_net else request.args.get("net")
            if h_team and a_team:
                return hunter(h_team, a_team, str(net))
            else:
                logging.error(f"Incomplete request : {request.remote_addr}")
                return bad_request()
        else:
            try:
                h_team = request.form["home"]
                a_team = request.form["away"]
                if "net" in list(request.form.keys()):
                    net = False if args.no_net else str(request.form["net"])
            except Exception as e:
                logging.error(f"POST method - {e} - [{request.remote_addr}]")
                return bad_request()
            else:
                return hunter(h_team, a_team, net)
    else:
        return error("Kindly login!"), 401


# Initial login
@app.route("/login", methods=["POST", "GET"])
def login():
    try:
        if request.method in ("POST"):
            user = request.form["user"]
            paswd = request.form["paswd"]
        else:
            user = request.args.get("user")
            paswd = request.args.get("paswd")
    except:
        return (
            error(
                "Error in your request",
                "Params {User:username, paswd:paswword, net:(true/false)}",
            ),
            400,
        )
    if user == args.username and paswd == args.password:
        resp = make_response(jsonify({"message": "login succeeded"}))
        id, value = cookie_value()
        resp.set_cookie("id", id)
        resp.set_cookie("value", value)
        logging.debug(
            f"LOGIN Successful: {request.remote_addr} : {request.headers['User-Agent']}"
        )
        return resp
    else:
        logging.debug(
            f"LOGIN FAILED : {request.remote_addr} : {request.headers['User-Agent']}"
        )
        return error("Wrong credentials!"), 400


def start_server():
    try:
        if args.host:
            app.run(host="0.0.0.0", port=args.port, debug=args.debug, threaded=True)
        else: 
            app.run(port=args.port, debug=args.debug)
    except (KeyboardInterrupt, EOFError):
        from sys import exit

        print(col.Fore.RED + "[*] Goodbye !" + col.Fore.RESET)
        exit(logging.critical("KeyboardInterrupt"))
    except Exception as e:
        logging.error(str(e))


if __name__ == "__main__":
    start_server()
