import subprocess  # nosec B404
import sys

import yaml
from watchfiles import watch

from uselevers.main import app


def write() -> None:
    openapi = app.openapi()

    with open("openapi.yml", "w") as f:
        yaml.dump(openapi, f)


def main() -> None:
    match sys.argv[1:]:
        case ["watch"]:
            for change in watch("api"):
                print(change)
                subprocess.run([*sys.orig_argv[:-1]])  # nosec B603
        case _:
            write()


if __name__ == "__main__":
    main()
