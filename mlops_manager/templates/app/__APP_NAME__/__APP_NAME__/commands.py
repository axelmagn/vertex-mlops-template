from . import pipelines
from .cli import command, arg
from .config import Config
from kfp.v2 import compiler
from kfp.v2.google.client import AIPlatformClient
import logging
import os
import importlib.util
import yaml


@command([
    arg("echo", help="String to echo", type=str),
])
def example(args):
    # TODO(axelmagn): docstring
    print(f"You said '{args.echo}'")


@command([
    arg("pipeline_id", help="The pipeline to run", type=str),
])
def run_pipeline(args):
    # TODO(axelmagn): docstring, logging
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
    pipeline_run_response_path = os.path.join(
        build_dir, f"{args.pipeline_id}_run_response.yaml")
    response = api_client.create_run_from_job_spec(
        job_spec_path=pipeline_package_path,
        pipeline_root=pipeline_storage_root
    )

    with open(pipeline_run_response_path, 'w') as f:
        f.write(yaml.safe_dump(response))
