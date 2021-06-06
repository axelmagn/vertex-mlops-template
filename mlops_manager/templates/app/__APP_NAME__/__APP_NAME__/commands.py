from . import pipelines
from .cli import command, arg
from .config import get_config
from .pipelines.runner import PipelineRunner
from kfp.v2 import compiler
from kfp.v2.google.client import AIPlatformClient
import importlib.util
import logging
import os
import yaml


@command([
    arg("echo", help="String to echo", type=str),
])
def example(args):
    # TODO(axelmagn): docstring
    config = get_config()
    project_id = config['cloud']['project_id']
    print(f"You said '{args.echo}'")


@command([
    arg("pipeline",
        help=("Pipeline ID corresponding to key in pipelines"
              + "section of config file."),
        type=str),
    arg("-o", "--output-dir", help="output directory", type=str, required=True),
])
def build_pipeline(args):
    config = get_config()
    os.makedirs(args.output_dir, exist_ok=True)
    pipeline_job_path = PipelineRunner().build_pipeline(
        pipeline_id=args.pipeline,
        output_dir=args.output_dir,
    )
    logging.info(f"Wrote compiled pipeline: {pipeline_job_path}")


@command([
    arg("pipeline_id", help="The pipeline to run", type=str),
])
def run_pipeline(args):
    config = get_config()
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
        project_id=config['cloud']['project_id'],
        region=config['cloud']['region'],
    )

    pipeline_storage_root = os.path.join(
        config['cloud']['storage_root'], 'pipelines', args.pipeline_id)
    pipeline_run_response_path = os.path.join(
        build_dir, f"{args.pipeline_id}_run_response.yaml")
    response = api_client.create_run_from_job_spec(
        job_spec_path=pipeline_package_path,
        pipeline_root=pipeline_storage_root
    )

    with open(pipeline_run_response_path, 'w') as f:
        f.write(yaml.safe_dump(response))
