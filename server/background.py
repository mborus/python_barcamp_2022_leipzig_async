import datetime
import time
from queue import Empty, PriorityQueue
from threading import Event

from model import MyTask

LOOP_TIME_SEC = 2.0
LOOP_TIME_WORK_SEC = 0.5

wake_up_worker_trigger = Event()


def background_worker_thread(worker_priority_queue: PriorityQueue):

    global wake_up_worker_trigger

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

            # when the queue is totally empty, pause for a fixed amount of time
            # or until a wakeup trigger is set.

            # There's a potentiol race condition for the trigger
            # but it's not a blocker: the timeout guarantees a run every
            # x seconds and also any following request will immediately unlock
            # the wait

            wake_up_worker_trigger.clear()
            # start_time = time.time()
            wake_up_worker_trigger.wait(timeout=LOOP_TIME_SEC)

            # waited_time = 1000 * (time.time() - start_time)
            # if waited_time < LOOP_TIME_SEC * 1000:
            #     print(f"waited {waited_time}")
