from .parser import command, arg


@command([arg("--package_name", help="Package Name", type=str)])
def init(args):
    print("INIT")
    print(args)
