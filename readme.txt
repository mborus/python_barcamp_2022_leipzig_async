FastAPI Async with Sync Background Example Code
-----------------------------------------------

This example code has an async server with a sync background thread.

Incoming requests are sent into a priority queue, unless the queue is full.

The background worker finishes the tasks by priority

FastAPI notices the finished task and returns the result. Or times out/aborts if the work takes too long.

![overview](docs/overview.jpg?raw=true "Overview")
