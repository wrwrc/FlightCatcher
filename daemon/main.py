import sys
import logging
import signal
import time
from datetime import date
import config
from ptx import Client
from models import MySqlConnection
from tasks import TaskManager

class LoopController:
    should_stop = False

    def __init__(self):
        self.callbacks = []
        signal.signal(signal.SIGINT, self.onstop)
        signal.signal(signal.SIGTERM, self.onstop)

    def onstop(self, signum, frame):
        self.should_stop = True

        for fn in self.callbacks:
            fn()

    def subscribe(self, fn):
        self.callbacks.append(fn)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stderr
)

loop = LoopController()
prev_daily = None

while True:
    start = time.process_time()

    try:
        client = Client(config.APP_ID, config.APP_KEY)

        with MySqlConnection(**config.DATABASE) as db:
            task = TaskManager(db, client)
            loop.subscribe(task.interrupt)

            if not prev_daily or prev_daily < date.today():
                task.updateairports()
                task.updateairlines()

                prev_daily = date.today()

            task.updateflights()

    except Exception:
        logging.exception("Error")

    if loop.should_stop:
        break

    end = time.process_time()

    wait_time = 120 - round(end - start)
    if wait_time > 0:
        time.sleep(wait_time)