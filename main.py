import time

import schedule

from config import RUN_INTERVAL_HOURS
from crawler.run import run


def job():
    print("running crawler...")
    run()


schedule.every(RUN_INTERVAL_HOURS).hours.do(job)

if __name__ == "__main__":
    job()

    while True:
        schedule.run_pending()
        time.sleep(1)
