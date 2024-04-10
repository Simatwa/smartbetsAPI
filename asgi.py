#!usr/bin/python3
from sys import argv
from os import environ

argv.append(environ.get("USERNAME", "api"))

argv += ["-u", environ.get("PASSWORD", "developer")]

from smartbets_API.interface import app

if __name__ == "__main__":
    from smartbets_API.interface import start_server

    start_server()
