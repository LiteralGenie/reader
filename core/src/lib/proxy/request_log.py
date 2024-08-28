import time

from yarl import URL


class RequestLog:
    def __init__(self, purge_after_seconds=300, check_delay=0.1):
        self.purge_after_seconds = purge_after_seconds
        self.check_delay = check_delay

        self.history: dict[str, list[float]] = dict()

    def add(self, url: str):
        key = self.get_key(url)

        self.history.setdefault(key, [])
        self.history[key].append(time.time())

    def purge(self):
        cutoff = time.time() - self.purge_after_seconds

        for log_key, log in self.history.items():
            idx_stop = 0
            for idx_stop, t in enumerate(log):
                if t > cutoff:
                    break

            if idx_stop > 0:
                self.history[log_key] = log[:idx_stop]

    def wait_limit(self, url: str, per_second_limit: int):
        key = self.get_key(url)

        recent = self._get_recent(key, 1)
        if len(recent) >= per_second_limit:
            until = recent[-per_second_limit] + 1
            delay = time.time() - until
            time.sleep(delay)

        return

    def _get_recent(self, key: str, threshold: float):
        cutoff = time.time() - threshold

        reqs = []
        for t in reversed(self.history.get(key, [])):
            if t < cutoff:
                break
            reqs.append(t)

        return reqs

    def get_key(self, url_str: str) -> str:
        return str(URL(url_str).origin())
