from .cli import command, arg
from .templating import TemplateTreeJob


@command([
    arg("template_path", help="Template Path", type=str),
    arg("target_path", help="Target Path", type=str),
    arg("--exists_policy", help="Policy for files that already exist",
        default="error", choices=TemplateTreeJob.VALID_EXISTS_POLICIES),
    arg("-n", "--name", help="Name to use in substitution"),

])
def apply_template(args):
    job = TemplateTreeJob(
        args.template_path,
        args.target_path,
        exists_policy=args.exists_policy,
        sub_name=args.name,
    )
    job.run()
