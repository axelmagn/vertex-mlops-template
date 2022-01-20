"""TODO(author): a brief docstring describing the task"""

import argparse
import json


def parse_args() -> argparse.Namespace:
    """Parse task arguments"""
    parser = argparse.ArgumentParser()
    # TODO(author): define any command line arguments for the task:
    # parser.add_argument(...)
    return parser.parse_args()


def run(args):
    # TODO(author): replace the lines below with task logic
    print("Task: {{ task_name }}")
    print("Args: %s" % json.dumps(args, sort_keys=True, indent=2))


if __name__ == "__main__":
    run(parse_args())
