import logging

from . import cli, commands


def main():
    # parse arguments
    args, unknown = cli._PARSER.parse_known_args()

    # configure logging
    log_level_num = getattr(logging, args.log_level.upper(), None)
    logging.basicConfig(level=log_level_num)

    # handle command
    if args.command is None:
        cli._PARSER.print_help()
    elif args.func.strict:
        args = cli._PARSER.parse_args()
        args.func(args)
    else:
        args.func(args, unknown)


if __name__ == "__main__":
    main()
