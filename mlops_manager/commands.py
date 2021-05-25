import os
import pathlib

from jinja2 import FileSystemLoader

from .cli import command, arg
from .templating import TemplateTreeJob, get_templates_dir


@command([
    # TODO(axelmagn): handle required args interactively
    arg("--package_name", help="Package Name", type=str, required=True),
    arg("--gcp_project", required=True),
    arg("--gcp_region", required=True),
    arg("--gcp_storage_root", required=True),

    arg("--force", help="overwrite files rather than throwing an error",
        action="store_true"),
    arg("--target", help="target directory")
])
def init(args):
    # TODO(axelmagn): docstring
    template_root = os.path.join(get_templates_dir(), 'app')
    target_root = pathlib.Path().absolute()

    exists_policy = "error"
    if args.force:
        exists_policy = "overwrite"

    job = TemplateTreeJob(
        template_root=template_root,
        target_root=target_root,
        exists_policy=exists_policy,
        filename_substitutions={
            "__PACKAGE_NAME__": args.package_name
        },
        template_context={
            "python_package_name": args.package_name,
            "gcp_project": args.gcp_project,
            "gcp_region": args.gcp_region,
            "gcp_storage_root": args.gcp_storage_root,
        }
    )
    job.run()
