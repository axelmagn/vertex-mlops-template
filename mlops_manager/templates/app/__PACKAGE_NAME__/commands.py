from .cli import command, arg
from . import pipelines

import logging
import importlib

from kfp.v2 import compiler
from kfp.v2.google.client import AIPlatformClient

@command([
    arg("echo", help="String to echo", type=str),
])
def example(args):
    # TODO(axelmagn): docstring
    print(f"You said '{args.echo}'")

@command([
    arg("pipeline_id", help="The pipeline to run", type=str),
    arg("--pipeline_package_path", help="Output path for pipeline package", type=str),
    arg("--pipeline_root", help="GCS path that will act as the root of the pipeline run", required=True), # TODO(axelmagn): use config
    arg("--gcp_project_id", required=True), # TODO(axelmagn): use config
    arg("--gcp_region", required=True), # TODO(axelmagn): use config
])
def run_pipeline(args):
    # TODO(axelmagn): handle bad name
    pipeline_func = getattr(pipelines, args.pipeline_id)
    if args.pipeline_package_path:
        pipeline_package_path=args.pipeline_package_path
    else:
        pipeline_package_path=f"{args.pipeline_id}_pipeline_job.json"

    compiler.Compiler().compile(
        pipeline_func=pipeline_func,
        package_path=pipeline_package_path,
    )

    api_client=AIPlatformClient(
        project_id=args.gcp_project_id,
        region=args.gcp_region
    )

    response = api_client.create_run_from_job_spec(
        job_spec_path=pipeline_package_path,
        pipeline_root=args.pipeline_root
    )
    logging.info(f"Created Pipeline Job: {response}")


