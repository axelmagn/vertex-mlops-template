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
        help=("Pipeline ID corresponding to key in pipelines "
              + "section of config file."),
        type=str),
    arg("-o", "--out-dir",
        help="output directory (default: local.build_root from config)",
        type=str, default=None),
    arg("--out-manifest",
        help="output manifest destination.  No manifest written if absent.",
        type=str, default=None),
])
def build_pipeline(args):
    pipeline_id = args.pipeline

    # load configured variables
    config = get_config()
    output_dir = args.out_dir
    if output_dir is None:
        output_dir = config['local']['build_root']

    # prepare output directory
    if os.path.exists(output_dir) and not os.path.isdir(output_dir):
        logging.fatal("Path supplied for output directory already exists and "
                      + "is not a directory.")
    os.makedirs(output_dir, exist_ok=True)

    pipeline_job_path = PipelineRunner().build_pipeline(
        pipeline_id=pipeline_id,
        output_dir=output_dir,
    )
    logging.info(f"Wrote compiled pipeline: {pipeline_job_path}")

    # TODO(axelmagn): replace with manifests module
    out_manifest_path = args.out_manifest
    if out_manifest_path:
        manifest = {
            pipeline_id: {
                "job_spec": pipeline_job_path
            },
        }
        with open(out_manifest_path, 'w') as f:
            yaml.safe_dump(manifest, f)
        logging.info(f"Wrote pipeline build manifest: {out_manifest_path}")


@command([
    arg("pipeline",
        help=("Pipeline ID corresponding to key in pipelines "
              + "section of config file."),
        type=str),
    arg("--build-manifest", help="build manifest file containing job spec path",
        type=str, default=None),
    arg("--job-spec", help="job spec file path", type=str, default=None),
    arg("--out-manifest", help="output manifest destination", default=None),
])
def run_pipeline(args):
    pipeline_id = args.pipeline

    # load configured variables
    config = get_config()

    # derive job_spec_path from args
    if args.job_spec:
        job_spec_path = args.job_spec
    elif args.build_manifest:
        # TODO(axelmagn): replace with manifests module
        with open(args.build_manifest, 'r') as f:
            manifest = yaml.safe_load(f)
        if pipeline_id not in manifest:
            logging.fatal(f"manifest does not contain '{pipeline_id}'")
        elif 'job_spec' not in manifest[pipeline_id]:
            logging.fatal(f"manifest section for '{pipeline_id}' does not "
                          + f"contain 'job_spec'")

        job_spec_path = manifest[pipeline_id]['job_spec']
    else:
        logging.fatal("Cannot derive job spec path."
                      + " Neither '--job-spec' nor '--out-manifest' is set.")

    response = PipelineRunner().run_pipeline(
        pipeline_id,
        job_spec_path,
    )

    # TODO(axelmagn): replace with manifests module
    out_manifest_path = args.out_manifest
    if out_manifest_path:
        manifest = {
            pipeline_id: {
                "run_response": response
            }
        }
        with open(out_manifest_path, 'w') as f:
            yaml.safe_dump(manifest, f)
        logging.info(f"Wrote pipeline run manifest: {out_manifest_path}")


@ command([
    arg("pipeline_id", help="The pipeline to run", type=str),
])
def run_pipeline_old(args):
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
