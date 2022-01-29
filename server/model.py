import time

# Events not used yet - can you await them?
# from threading import Event
from asyncio import Event
from random import randint

from pydantic import BaseModel


class MyTask:
    def __init__(self, no):
        self.event = Event()  # Note: This is an awaitable async event
        self.priority = randint(1, 5)
        self.no = no
        self.aborted = False
        self.completed = False
        self.create_time = time.time()

    def __lt__(self, other):
        return self.priority < other.priority

    def __repr__(self):
        return f"Task No {self.no}, Priority {self.priority}"

    def complete(self):
        self.event.set()
        self.completed = True

    @property
    def exist_time(self):
        return time.time() - self.create_time


class Message(BaseModel):
    message: str


class ExampleResponse(BaseModel):
    count: int
    global_count: int
    priority: int
    queue_size: int
    runtime_ms: int
