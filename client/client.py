import httpx
from threading import Thread

NUMBER_OF_THREADS = 20
HTTPX_TIMEOUT_SEC = 10.0

def single_request():
    try:
        r = httpx.get('http://localhost:9000', timeout=HTTPX_TIMEOUT_SEC)
        r.raise_for_status()
        print(f"{r.status_code=} {r.text}")
    except httpx.TimeoutException as exc:
        print(f"Timeout response \"{exc}\" while requesting {exc.request.url!r}.")
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")


if __name__ == '__main__':

    threads = []
    for _ in range(NUMBER_OF_THREADS):
        t = Thread(target=single_request)
        t.daemon = True
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

