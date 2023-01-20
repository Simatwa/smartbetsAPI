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
        "--no-net",
        action="store_true",
        dest="no_net",
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
from flask import *
from .predictor import predictor
from .bet_common import logging, col
from random import sample

cookie_jar, ip_address = {}, []
app = Flask(__name__)


@app.errorhandler(500)
def internal_error(e):
    return str(e), 500


# Generates cookie value
def cookie_value():
    dat = []
    addr = request.remote_addr
    for x in range(65, 126, 1):
        dat.append(chr(x))
    rp = "".join(sample(dat, 30))
    cookie_jar[addr] = rp
    ip_address.append(addr)
    logging.debug(f"Assigning cookie_value [{rp}] : {request.remote_addr}")
    logging.debug(f"Total logins [{len(cookie_jar)}]")
    return rp


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
def error(msg: str, comment=""):
    logging.debug(f"INVALID {request.remote_addr} : {msg}")
    return make_response(
        Response(
            f'<script>alert("{msg}")</script>{comment}',
            mimetype="javascript/application",
        )
    )


def bad_request() -> tuple:
    info = """
	Kindly pass team names {home:str,away:str,net:bool}
	//<input name="home" type="text"/> 
	//<input name="away" type="text"/>
	//<input name="net" type="text"/>
	"""
    return error(info), 400


# Route to the server
@app.route("/", methods=["GET", "POST"])
def responser():
    if (
        request.cookies.get("id")
        and request.remote_addr in ip_address
        and cookie_jar[request.remote_addr] == request.cookies.get("id")
    ):
        if request.method == "GET":
            h_team = request.args.get("home")
            a_team = request.args.get("away")
            net = False if args.no_net else request.args.get("net")
            if h_team and a_team:
                return hunter(h_team, a_team, str(net))
            else:
                logging.error(f"Get method unknown : {request.remote_addr}")
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
@app.route("/login", methods=["POST"])
def login():
    try:
        user = request.form["user"]
        paswd = request.form["paswd"]
    except:
        return (
            error(
                "Error in your request",
                '//<input name="user" type="text"/> '
                '//<innput name="paswd" type="password"/>',
            ),
            400,
        )
    if user == args.username and paswd == args.password:
        resp = make_response("<h1>Success<h1>")
        resp.set_cookie("id", cookie_value())
        logging.debug(
            f"LOGIN Successful: {request.remote_addr} : {request.headers['User-Agent']}"
        )
        return resp
    else:
        logging.debug(
            f"LOGIN FAILURE : {request.remote_addr} : {request.headers['User-Agent']}"
        )
        return error("Wrong credentials!"), 400


def start_server():
    try:
        if args.host:
            app.run(host="0.0.0.0", port=args.port, debug=args.debug)
        else:
            app.run(port=args.port, debug=args.debug)
    except (KeyboardInterrupt, EOFError):
        from sys import exit

        exit(logging.critical("KeyboardInterrupt"))
        print(col.Fore.RED + "[*] Goodbye !" + col.Fore.RESET)
    except Exception as e:
        logging.error(str(e))


if __name__ == "__main__":
    start_server()
