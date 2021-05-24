from .cli import command, arg


@command([
    arg("echo", help="String to echo", type=str),
])
def example(args):
    # TODO(axelmagn): docstring
    print(f"You said '{args.echo}'")
