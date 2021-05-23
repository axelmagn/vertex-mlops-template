"""
Project manager CLI.

Extend this with your own commands.

Usage:
    manage.py 
"""

from manager import parser
from manager.commands import *


def main():
    args = parser.PARSER.parse_args()
    if args.command is None:
        parser.PARSER.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
