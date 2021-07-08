from .cli import command, arg, template_command
from .templating import TemplateTreeJob, get_templates_dir
import os
import yaml


@command([
    # TODO(axelmagn): handle required args interactively
    arg("--name", type=str, required=True),
    arg("--gcp-project", required=True),
    arg("--gcp-region", required=True),
    arg("--gcp-storage-root", required=True),
    arg("--variant", default="default"),
    arg("--on-exists",
        default="error",
        choices=TemplateTreeJob.VALID_EXISTS_POLICIES,
        help="policy for handling files which already exist.  "
        + "(choices: %(choices)s) (default: %(default)s)",),
    arg("--target_root", help="target directory", default=".")
])
def start_app(args):
    # TODO(axelmagn): docstring
    template_root = os.path.join(get_templates_dir(), 'app', 'default')

    filename_substitutions = {
        "__APP_NAME__": args.name
    },

    template_context = {
        "app_name": args.name,
        "gcp_project_id": args.gcp_project,
        "gcp_region": args.gcp_region,
        "gcp_storage_root": args.gcp_storage_root,
    }

    exists_policy = "error"
    if args.force:
        exists_policy = "overwrite"

    job = TemplateTreeJob(
        template_root=template_root,
        target_root=args.target_root,
        exists_policy=exists_policy,
        filename_substitutions={
            "__APP_NAME__": args.name
        },
        template_context={
            "app_name": args.name,
            "gcp_project_id": args.gcp_project,
            "gcp_region": args.gcp_region,
            "gcp_storage_root": args.gcp_storage_root,
        }
    )
    job.run()


@template_command(
    [
        arg("--on-exists",
            default="error",
            choices=TemplateTreeJob.VALID_EXISTS_POLICIES,
            help="policy for handling files which already exist.  "
            + "(choices: %(choices)s) (default: %(default)s)",),
        arg("--target_root", help="target directory", default="."),
    ],
)
def start_template(args):
    template_root = os.path.join(get_templates_dir(), args.template)
    variant_root = os.path.join(template_root, args.variant)

    variables_path = os.path.join(template_root, 'variables.yaml')
    with open(variables_path, 'r') as f:
        variables = yaml.safe_load(f)

    filename_substitutions = variables.get('filename_substitutions', None)
    if filename_substitutions is None:
        filename_substitutions = {}
    for key in filename_substitutions:
        arg_name = filename_substitutions[key]
        filename_substitutions[key] = getattr(args, arg_name)

    template_context = variables.get('template_context', None)
    if template_context is None:
        template_context = {}
    for key in template_context:
        arg_name = template_context[key]
        template_context[key] = getattr(args, arg_name)

    template_job = TemplateTreeJob(
        template_root=variant_root,
        target_root=args.target_root,
        exists_policy=args.on_exists,
        filename_substitutions=filename_substitutions,
        template_context=template_context,
    )
    template_job.run()

    examples = getattr(args, 'example', [])
    for example in examples:
        example_root = os.path.join(template_root, 'examples', example)
        example_job = TemplateTreeJob(
            template_root=example_root,
            target_root=args.target_root,
            exists_policy=args.on_exists,
            filename_substitutions=filename_substitutions,
            template_context=template_context,
        )
        example_job.run()
