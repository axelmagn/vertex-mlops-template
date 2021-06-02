from . import pipelines, config
from .cli import command, arg
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
    project_id = config.CONFIG['cloud']['project_id']
    print(f"You said '{args.echo}'")


@command([
    arg("pipeline_id", help="The pipeline to run", type=str),
])
def run_pipeline(args):
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
        project_id=config.CONFIG['cloud']['project_id'],
        region=config.CONFIG['cloud']['region'],
    )

    pipeline_storage_root = os.path.join(
        config.CONFIG['cloud']['storage_root'], 'pipelines', args.pipeline_id)
    pipeline_run_response_path = os.path.join(
        build_dir, f"{args.pipeline_id}_run_response.yaml")
    response = api_client.create_run_from_job_spec(
        job_spec_path=pipeline_package_path,
        pipeline_root=pipeline_storage_root
    )

    with open(pipeline_run_response_path, 'w') as f:
        f.write(yaml.safe_dump(response))
