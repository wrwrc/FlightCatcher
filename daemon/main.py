import asyncio
import sys
import logging
import signal
import time
from datetime import date
import config
import ptx
from models import MySqlConnection
from tasks import TaskManager

# class LoopController:
#     should_stop = False

#     def __init__(self):
#         self.callbacks = []
#         signal.signal(signal.SIGINT, self.onstop)
#         signal.signal(signal.SIGTERM, self.onstop)

#     def onstop(self, signum, frame):
#         self.should_stop = True

#         for fn in self.callbacks:
#             fn()

#     def subscribe(self, fn):
#         self.callbacks.append(fn)

async def main():
    prev_daily = None
    while True:
        with MySqlConnection(**config.DATABASE) as db:
            ptx_client = ptx.Client(config.APP_ID, config.APP_KEY)
            task = TaskManager(db, ptx_client)

            if not prev_daily or prev_daily < date.today():
                await task.updateairports()
                await task.updateairlines()
                prev_daily = date.today()

            await task.updateflights()

        await asyncio.sleep(60)

def sig_callback():
    raise SystemExit('terminates')

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        stream=sys.stderr
    )

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, sig_callback)
    loop.add_signal_handler(signal.SIGTERM, sig_callback)

    try:
        loop.run_until_complete(main())
    except SystemExit:
        pass
    except:
        logging.exception("Error")

    loop.close()