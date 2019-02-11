"""Cache in background most popular packages

    ```
    import subprocess
    subprocess.Popen(['python3', '-m', 'dephell.cacher'])
    ```
"""
from itertools import islice
import asyncio

import requests
from packaging.requirements import Requirement

from dephell.models import Dependency, RootDependency
from dephell.repositories import WareHouseRepo


loop = asyncio.get_event_loop()
URL = 'https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json'


def get_deps():
    root = RootDependency()
    response = requests.get(URL)
    for info in response.json()['rows']:
        yield Dependency.from_requirement(
            source=root,
            req=Requirement(info['project']),
        )


def cache(deps):
    repo = WareHouseRepo()
    tasks = []
    for dep in islice(deps, 1000):
        for release in repo.get_releases(dep):
            task = asyncio.ensure_future(repo.get_dependencies(
                release.name,
                release.version,
            ))
            tasks.append(task)
    loop.run_until_complete(asyncio.gather(*tasks))


def main():
    cache(get_deps())


if __name__ == '__main__':
    main()