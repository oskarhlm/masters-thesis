from typing import Sequence

from .worker import workers


def check_valid_workers(workers_to_use: Sequence[str]):
    for worker_key in workers_to_use:
        if not workers.get(worker_key):
            raise KeyError(f'No worker `{worker_key}` in worker dict')
