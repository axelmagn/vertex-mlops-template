from . import pipelines
from .cli import command, arg
from config import Config
from kfp.v2 import compiler
from kfp.v2.google.client import AIPlatformClient
import logging
import os


@command([
    arg("echo", help="String to echo", type=str),
])
def example(args):
    # TODO(axelmagn): docstring
    print(f"You said '{args.echo}'")


@command([
    arg("pipeline_id", help="The pipeline to run", type=str),
    arg("--pipeline_package_path", help="Output path for pipeline package", type=str),
])
def run_pipeline(args):
    config = Config(config_root=args.config_dir,
                    config_environment=args.config_env)

    pipeline_func = getattr(pipelines, args.pipeline_id)
    build_dir = os.path.join(args.build_dir, "pipelines", args.pipeline_id)
    os.makedirs(build_dir, exist_ok=True)
    pipeline_package_path = os.path.join(
        build_dir, f"{args.pipeline_id}_pipeline_job.json")

    compiler.Compiler().compile(
        pipeline_func=pipeline_func,
        package_path=pipeline_package_path,
    )

    api_client = AIPlatformClient(
        project_id=config.cloud['project_id'],
        region=config.cloud['region'],
    )

    pipeline_storage_root = os.path.join(
        config.cloud['storage_root'], 'pipelines', args.pipeline_id)
    response = api_client.create_run_from_job_spec(
        job_spec_path=pipeline_package_path,
        pipeline_root=pipeline_storage_root
    )
    logging.trace(f"Created Pipeline Job: {response}")
