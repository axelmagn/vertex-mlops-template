"""{{app_name}} process entry point."""

import logging
import sys
import yaml
from yaml.error import YAMLError

from . import cli, config, commands as _


def main():
    """Run the module as a command line tool."""
    # parse arguments
    args = cli.PARSER.parse_args()

    # configure logging
    log_level_num = getattr(logging, args.log_level.upper(), None)
    logging.basicConfig(level=log_level_num)

    # handle command
    if args.command is None:
        cli.PARSER.print_help()
        return
    # load args globally
    cli.init_global_args(args)
    # load config globally
    config.init_global_config(
        config_file_paths=args.config_files,
        config_strings=args.config_strings,
    )
    # invoke command. Although args could be retrieved with cli.get_args, we
    # pass it explicitly as a convenience.
    out = args.func(args)

    # write the result to stdout or file
    out_str = None
    if isinstance(out, str):
        out_str = out + "\n"
    else:
        try:
            out_str = yaml.safe_dump(out)
        except YAMLError:
            logging.info("Command return value is not serializable as YAML.")
    if out_str is not None:
        if args.out_file is not None:
            with open(args.out_file, 'w') as out_file:
                out_file.write(out_str)
            logging.info("Wrote command result to: %s", args.out_file)
        else:
            sys.stdout.write(out_str)


if __name__ == "__main__":
    main()
