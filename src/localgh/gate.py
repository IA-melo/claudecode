"""Semaforo entre procesos: solo una inferencia a la vez en el modelo local."""
import fcntl
import time
from contextlib import contextmanager


class Busy(Exception):
    pass


@contextmanager
def gate(path: str, wait: float = 60.0, poll: float = 0.5):
    fh = open(path, "w")
    deadline = time.monotonic() + wait
    try:
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise Busy(f"canal ocupado tras {wait}s")
                time.sleep(poll)
        yield
    finally:
        fh.close()
