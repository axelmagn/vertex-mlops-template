"""
Application CLI Commands.

This file defines command functions which are invokable as commands from the
command line.  Additional application-specific commands are encouraged, and may
be added with the {{app_name}}.cli.command decorator.
"""

import logging
import os

from argparse import REMAINDER
from tensorflow.io import gfile
import yaml

from .cli import command, arg
from .config import get_config
from .pipelines.harness import PipelineHarness
from .util import dynamic_import_func, get_collection


@command([
    arg("pipeline",
        help=("pipeline ID from config"),
        type=str),
    arg("-o", "--out-dir", type=str, default=None,
        help="output directory (default: build.local_root variable from config)"),
])
def build_pipeline(args):
    """Build a pipeline job spec using configured settings."""
    pipeline_id = args.pipeline

    # load configured variables
    config = get_config()
    output_dir = args.out_dir
    if output_dir is None:
        output_dir = config['build']['local_root']

    # prepare output directory
    if os.path.exists(output_dir) and not os.path.isdir(output_dir):
        logging.fatal(
            "Path supplied for output directory already exists and is not a directory.")
    os.makedirs(output_dir, exist_ok=True)

    pipeline_job_path = PipelineHarness().build_pipeline(
        pipeline_id=pipeline_id,
        output_dir=output_dir,
    )
    logging.info("Wrote compiled pipeline: %s", pipeline_job_path)

    manifest = {
        pipeline_id: {
            "job_spec": pipeline_job_path
        },
    }

    return manifest


@command([
    arg("-o", "--out-dir", type=str, default=None,
        help="output directory (default: local.build_root from config)"),
])
def build_pipelines(args):
    """Build all pipeline job specs using configured settings."""
    # load configured variables
    config = get_config()
    output_dir = args.out_dir
    if output_dir is None:
        output_dir = config['build']['local_root']

    # prepare output directory
    if os.path.exists(output_dir) and not os.path.isdir(output_dir):
        logging.fatal("path supplied for output is not a directory")
    os.makedirs(output_dir, exist_ok=True)

    manifest = {}
    for pipeline_id in get_collection(config, 'pipelines'):
        logging.info("building pipeline: %s", pipeline_id)
        pipeline_job_path = PipelineHarness().build_pipeline(
            pipeline_id=pipeline_id,
            output_dir=output_dir,
        )
        manifest[pipeline_id] = {"job_spec": pipeline_job_path}

    return manifest


@command()
def deploy_pipelines(args):  # pylint: disable=unused-argument
    """Deploy all configured pipelines"""
    return PipelineHarness().deploy()


@command([
    arg("pipeline", type=str,
        help="pipeline ID from config"),
    arg("--manifest", type=str, default=None,
        help="pipeline build manifest file containing job spec path"),
    arg("--job-spec",  type=str, default=None, help="job spec file path"),
    arg("--out-manifest", type=str, default=None,
        help="output manifest destination"),
])
def run_pipeline(args):
    """Run a pipeline from either a job spec or a pipeline build manifest."""
    pipeline_id = args.pipeline

    # derive job_spec_path from args
    if args.job_spec:
        job_spec_path = args.job_spec
    elif args.build_manifest:
        # TODO(axelmagn): replace with manifests module
        with open(args.build_manifest, 'r') as file:
            manifest = yaml.safe_load(file)
        if pipeline_id not in manifest:
            logging.fatal("manifest does not contain '%s'", pipeline_id)
        elif 'job_spec' not in manifest[pipeline_id]:
            logging.fatal(
                "manifest section for '%s' does not contain 'job_spec'",
                pipeline_id
            )

        job_spec_path = manifest[pipeline_id]['job_spec']
    else:
        logging.fatal(
            "Cannot derive job spec path. Neither '--job-spec' nor '--manifest' is set."
        )

    response = PipelineHarness().run_pipeline(
        pipeline_id,
        job_spec_path,
    )
    manifest = {
        pipeline_id: {
            "run_response": response
        }
    }
    return manifest


@command([
    arg("import_path", type=str,
        help="python import string specifying task function to run"),
    arg("task_args", nargs=REMAINDER, help="task arguments"),
])
def task(args):
    """Run a task function."""
    func = dynamic_import_func(args.import_path)
    task_args = func.parser.parse_args(args.task_args)
    func(task_args)


@command()
def dump_config(_args):
    """Dump the current config to stdout or file"""
    config = get_config()
    return config.dumps()


@command([
    arg("--label", type=str, default=None, help="release label"),
    arg("--build", type=str, default=None, help="build label"),
    arg("--image", type=str, default=[], action="append", dest="images",
        help="release image key/value pair of the form KEY=IMAGE_VALUE (repeatable)"),
    arg("--pipelines-manifest", type=str, default=None,
        help="path to pipeline manifest generated by `build_pipelines` invocation"),
])
def release_config(args):
    """Build a release configuration section additively."""

    config = get_config()

    images = {}
    for image in args.images:
        key, value = image.split('=', 1)
        images[key] = value

    release = get_collection(config, 'release')

    if args.label is not None:
        release["label"] = args.label
    if args.build is not None:
        release["build"] = args.build
    release["images"] = get_collection(release, "images")
    release["images"].update(images)
    if args.pipelines_manifest is not None:
        with gfile.GFile(args.pipelines_manifest) as file:
            release["pipelines"] = get_collection(release, "pipelines")
            manifest = yaml.safe_load(file)
            release["pipelines"].update(manifest)

    config.set('release', release)

    return config.dumps()
