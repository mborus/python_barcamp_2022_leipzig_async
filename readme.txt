FastAPI Async with Sync Background Example Code
-----------------------------------------------

This example code has an async server with a sync background thread.

Incoming requests are sent into a priority queue, unless the queue is "full"
If "full", abort with HTTP status code 429, but do not add items!

The background worker finishes the tasks by priority.

Finish might mean that it requests work from external parties.
(For this scenario, the amount of unfinished work that is not timed out
adds to the "full" count of the work queue.

FastAPI notices the finished task and returns the result. Or times out/aborts if the work takes too long.

Both GET and POST requests are accepted. POST bodys will return reversed as a simlulation of work
(until I get a better simulator)
