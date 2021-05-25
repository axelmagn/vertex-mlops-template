import os
import pathlib

from jinja2 import FileSystemLoader

from .cli import command, arg
from .templating import TemplateTreeJob, get_templates_dir


@command([
    arg("template_path", help="Template Path", type=str),
    arg("target_path", help="Target Path", type=str),
    arg("--exists_policy", help="Policy for files that already exist",
        default="error", choices=TemplateTreeJob.VALID_EXISTS_POLICIES),
    arg("-n", "--name", help="Name to use in substitution"),

])
def apply_template(args, tail):
    job = TemplateTreeJob(
        args.template_path,
        args.target_path,
        exists_policy=args.exists_policy,
    )
    job.run()


@command([
    arg("--package_name", help="Package Name", type=str, required=True),
    arg("--force", help="overwrite files rather than throwing an error", action="store_true"),
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
            "PACKAGE_NAME": args.package_name
        }
        # TODO(axelmagn): template_context
    )
    job.run()
