import time
import datetime
from queue import Empty, PriorityQueue

from model import MyTask

LOOP_TIME_SEC = 0.5
LOOP_TIME_WORK_SEC = 0.5


def background_worker_thread(worker_priority_queue: PriorityQueue):
    while True:

        try:
            task: MyTask
            priority, task = worker_priority_queue.get(block=None)
            print(f'background {datetime.datetime.now().strftime("%H:%M:%S")} {task}')
            if not task.aborted:
                # TODO - Do the actual work here
                time.sleep(LOOP_TIME_WORK_SEC)
            task.complete()
        except Empty:
            time.sleep(LOOP_TIME_SEC)
            pass
