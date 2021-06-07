from . import pipelines
from .cli import command, arg
from .config import get_config
from .pipelines.harness import PipelineHarness
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


def dump_config():
    config = get_config()


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

    pipeline_job_path = PipelineHarness().build_pipeline(
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

    response = PipelineHarness().run_pipeline(
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


# TRAINER TASK COMMANDS

@command([
    arg("--width", type=int, default=128, help="width of hidden layers"),
    arg("--depth", type=int, default=1, help="number of hidden layers"),
    arg("--epochs", type=int, default=10, help="training epochs"),

])
def train_fashion_mnist_dense(args):
    """Example training command for the fashion_mnist dataset"""
    from .trainers import fashion_mnist_dense

    # load environment params
    training_data_uri = os.environ.get('AIP_TRAINING_DATA_URI')
    model_dir_uri = os.environ.get('AIP_MODEL_DIR')
    tensorboard_log_dir_uri = os.environ.get('AIP_TENSORBOARD_LOG_DIR', None)
    fashion_mnist_dense.train(
        training_data_uri=training_data_uri,
        model_dir_uri=model_dir_uri,
        feedforward_width=args.width,
        feedforward_depth=args.depth,
        epochs=args.epochs,
        tensorboard_log_dir_uri=tensorboard_log_dir_uri,
    )
