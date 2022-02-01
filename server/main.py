import asyncio
from queue import PriorityQueue
from threading import Thread
from typing import Optional

import uvicorn
from background import background_worker_thread, wake_up_worker_trigger
from fastapi import FastAPI, HTTPException, Request
from model import ExampleResponse, Message, MyTask

LOOP_TIME_WAIT_SEC = 0.2
LOOP_TIMEOUT = 5
PQ_MAXSIZE = 10

global_pq = PriorityQueue()  # do not use maxsize, it blocks!
global_task_count = 0

bg = Thread(target=background_worker_thread, args=(global_pq,))
bg.daemon = True
bg.start()

app = FastAPI()


@app.get(
    "/",
    response_model=ExampleResponse,
    responses={
        429: {"model": Message},
        408: {"model": Message},
    },
)
async def get_from_root(request: Request):
    result = await process_root_request(request)
    return result


@app.post(
    "/",
    response_model=ExampleResponse,
    responses={
        429: {"model": Message},
        408: {"model": Message},
    },
)
async def post_to_root(request: Request):
    result = await process_root_request(request, raw_body=await request.body())
    return result


async def process_root_request(request: Request, raw_body: Optional[bytes] = None):

    """processes both GET and POST request"""

    # Note: See https://github.com/tiangolo/fastapi/issues/558#issuecomment-533931308 on how to
    # access the body

    global global_task_count
    global_task_count += 1
    mytask = MyTask(no=global_task_count)
    mytask.raw_request = raw_body

    # check queue size
    if len(global_pq.queue) > PQ_MAXSIZE:
        raise HTTPException(status_code=429, detail="worker queue busy")

    print(f"put {mytask} into queue, size {len(global_pq.queue)}")
    global_pq.put((mytask.priority, mytask))
    wake_up_worker_trigger.set()  # note: this is a sync (threading event)

    try:
        await asyncio.wait_for(mytask.event.wait(), LOOP_TIMEOUT)
    except asyncio.exceptions.TimeoutError as err:
        raise HTTPException(status_code=408, detail="worker did not finish on time")

    return {
        "req_method": request.method,
        "count": mytask.no,
        "global_count": global_task_count,
        "priority": mytask.priority,
        "queue_size": len(global_pq.queue),
        "runtime_ms": int(mytask.exist_time * 1000),
        "response": mytask.raw_response,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
