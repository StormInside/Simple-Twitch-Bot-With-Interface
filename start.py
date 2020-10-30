import eel
import json
import sys
import asyncio

from threading import Thread
from source_code import bot_comands
from datetime import datetime

eel.init("interface")


with open('bot_config.json', 'r', encoding="utf-8") as f:
    data = json.load(f)


@eel.expose
def get_value(name):
    try:

        return data[name]
    except Exception as ex:
        return f"Error initializing -- {ex}"


@eel.expose
def get_bool_value(name):
    try:

        return bool(data[name])
    except Exception as ex:
        return f"Error initializing -- {ex}"


@eel.expose
def set_value(name, value):
    try:
        if (name == "MUSIC_COMMANDS"
        or name == "FOLLOW_COMMANDS"
        or name == "MESSAGE_SOUND_BLACKLIST"
        or name == "INITIAL_CHANELS"
        ):

            data[name] = value.split(",")
        else:
            data[name] = value
    except Exception as ex:
        return f"Error initializing -- {ex}"


@eel.expose
def set_bool_value(name, value):
    try:

        data[name] = value
    except Exception as ex:
        return f"Error initializing -- {ex}"

@eel.expose
def save():
    try:
        with open('bot_config.json', 'w', encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as ex:
        return f"Error initializing -- {ex}"


@eel.expose
def eel_stop_bot():
    global loop
    # eel.sleep(2)
    loop.stop()

@eel.expose
def get_temp_file():
    with open('temp.txt', 'r', encoding="utf-8") as f:
        data = f.read()
    return data


def start_interface():
    eel.start("main.html", size=(640, 900))
    

def start_bot():
    global loop
    bot_comands.start_bot(loop)

loop = asyncio.new_event_loop()

interface = Thread(target = start_interface)
bot = Thread(target = start_bot)

interface.start()
bot.start()


# eel.start("main.html", size=(640, 768))