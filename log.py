import logging
import json


def debug(obj):
    if logging.getLogger().level == logging.DEBUG:
        print(json.dumps(obj, indent=2, default=str))


def info(obj):
    if logging.getLogger().level <= logging.INFO:
        print(json.dumps(obj, indent=2, default=str))


def warn(obj):
    if logging.getLogger().level <= logging.WARNING:
        print(json.dumps(obj, indent=2, default=str))


def error(obj):
    print(json.dumps(obj, indent=2, default=str))
