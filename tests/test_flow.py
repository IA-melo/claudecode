import threading
import time

import pytest

from localgh import agent
from localgh.gate import Busy, gate
from localgh.outbox import Outbox


class FakeLLM:
    def __init__(self, out):
        self.out = out

    def chat(self, system, user):
        return self.out


class FakeGH:
    def __init__(self):
        self.calls = []

    def comment(self, n, body):
        self.calls.append(("comment", n, body))

    def add_labels(self, n, labels):
        self.calls.append(("labels", n, labels))


ISSUE = {"number": 1, "title": "crash", "body": "falla al iniciar"}


def test_triage_ok_filters_labels():
    llm = FakeLLM('{"labels":["bug","hack"],"comment":"Gracias"}')
    assert agent.triage(llm, ISSUE) == {"labels": ["bug"], "comment": "Gracias"}


@pytest.mark.parametrize("raw", ["", "no json", '{"labels":[]}'])
def test_triage_rejects_broken(raw):
    with pytest.raises(agent.BadOutput):
        agent.triage(FakeLLM(raw), ISSUE)


def test_offline_queues_then_sync(tmp_path):
    box, gh = Outbox(str(tmp_path / "o.db")), FakeGH()
    res = {"labels": ["bug"], "comment": "hola"}
    assert agent.deliver(gh, box, 1, res, online=False, apply=True) == "queued"
    assert gh.calls == []
    assert agent.flush(gh, box) == 1
    assert ("comment", 1, "hola") in gh.calls and box.pending() == []


def test_dry_run_writes_nothing(tmp_path):
    box, gh = Outbox(str(tmp_path / "o.db")), FakeGH()
    assert agent.deliver(gh, box, 1, {"labels": [], "comment": "x"}, online=True, apply=False) == "dry-run"
    assert gh.calls == [] and box.pending() == []


def test_gate_is_exclusive(tmp_path):
    lock = str(tmp_path / "l")
    started = threading.Event()

    def hold():
        with gate(lock):
            started.set()
            time.sleep(0.6)

    t = threading.Thread(target=hold)
    t.start()
    started.wait()
    with pytest.raises(Busy):
        with gate(lock, wait=0.2, poll=0.05):
            pass
    t.join()
