import asyncio
from queue import PriorityQueue
from threading import Thread

import uvicorn
from fastapi import FastAPI, HTTPException

from model import MyTask, Message, ExampleResponse
from background import background_worker_thread

LOOP_TIME_WAIT_SEC = 0.2
LOOP_TIMEOUT = 5
PQ_MAXSIZE = 10

global_pq = PriorityQueue()  # do not use maxsize, it blocks!
global_task_count = 0

bg = Thread(target=background_worker_thread, args=(global_pq,))
bg.daemon = True
bg.start()

app = FastAPI()


@app.get("/", response_model=ExampleResponse, responses={429: {"model": Message}, 408: {"model": Message}, })
async def root():

    global global_task_count
    global_task_count += 1
    mytask = MyTask(no=global_task_count)

    # check queue size
    if len(global_pq.queue) > PQ_MAXSIZE:
        raise HTTPException(status_code=429, detail="worker queue busy")

    print(f"put {mytask} into queue, size {len(global_pq.queue)}")
    global_pq.put((mytask.priority, mytask))

    # while True:
    #
    #     await asyncio.sleep(LOOP_TIME_WAIT_SEC)
    #
    #     if mytask.completed:
    #         break
    #
    #     if mytask.exist_time > LOOP_TIMEOUT:
    #         mytask.aborted = True  # Race condition with background worker!
    #         raise HTTPException(status_code=408, detail="worker did not finish on time")
    try:
        await asyncio.wait_for(mytask.event.wait(), LOOP_TIMEOUT)
    except asyncio.exceptions.TimeoutError as err:
        raise HTTPException(status_code=408, detail="worker did not finish on time")

    return {
        "count": mytask.no,
        "global_count": global_task_count,
        "priority": mytask.priority,
        "queue_size": len(global_pq.queue),
        "runtime_ms": int(mytask.exist_time * 1000),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
