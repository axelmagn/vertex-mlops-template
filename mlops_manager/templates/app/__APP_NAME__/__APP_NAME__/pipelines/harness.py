from ..config import Config, get_config
from collections.abc import Callable
from kfp.v2.compiler import Compiler
from kfp.v2.google.client.client import AIPlatformClient
from typing import Optional, Any, Dict
import importlib
import os
import re


# Pattern for valid names used as a uCAIP resource name.
_VALID_NAME_PATTERN = re.compile('^[a-z][-a-z0-9]{0,127}$')

CONFIG_PIPELINES_SECTION = 'pipelines'
CONFIG_BUILD_SUBSECTION = 'build'
CONFIG_RUN_SUBSECTION = 'run'


class PipelineHarness(object):
    """Build and run pipelines."""

    def __init__(
        self,
        config: Optional[Config] = None,
        client: Optional[AIPlatformClient] = None,
        compiler: Optional[Compiler] = None,
    ):
        if config is None:
            config = get_config()
        self.config = config

        if client is None:
            client = AIPlatformClient(
                project_id=config['cloud']['project'],
                region=config['cloud']['region']
            )
        self.client = client

        if compiler is None:
            compiler = Compiler()
        self.compiler = compiler

    def _get_pipeline_func(
        self,
        import_path: str,
    ):
        """
        Import a pipeline function by its module string and function name.

        Args:
            import_path: import path for the pipeline function.
                         (example: my_package.pipelines.pipeline_func)

        Returns:
            The imported pipeline function.
        """
        # TODO(axelmagn): import_path validation
        module_name, func_name = import_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func

    def _get_pipeline_job_spec_filename(
        self,
        pipeline_name: str,
    ):
        """Get the correct filename for a pipeline job."""
        return f"{pipeline_name}-job-spec.json"

    def _get_pipeline_name(
        self,
        pipeline_id: str,
    ):
        """Get the canonical name for a pipeline from an app"""
        app_name = self.config['app_name']
        release_version = self.config['release']['version']
        name = f"{app_name}-{pipeline_id}-{release_version}"
        return self._sanitize_name(name)

    def _sanitize_name(self, name: str):
        """convert into a valid name for AI Platform"""
        # python IDs will allow underscores but disallow hyphens, so some
        # interpolation is necessary
        return name.replace("_", "-")

    def _validate_name(self, name: str):
        """ensure name is valid on AI Platform"""
        if not _VALID_NAME_PATTERN.match(name):
            raise ValueError(
                f"'{name}' must match '{_VALID_NAME_PATTERN.pattern}' to be"
                + "valid on AI Platform.")

    def build_pipeline(
        self,
        pipeline_id: str,
        output_dir: str,
    ) -> str:
        """Compile a configured pipeline by ID.

        Args:
            pipeline_id: An ID corresponding to a key in the `pipelines`
                         section of the config file.
            output_dir: local directory to write compiled job file to.

        Returns:
            Path of the compiled pipeline job file.
        """
        # pipeline config
        pconfig = (self.config
                   [CONFIG_PIPELINES_SECTION]
                   [pipeline_id]
                   [CONFIG_BUILD_SUBSECTION])
        import_path = pconfig['python_path']

        # load computed variables
        pipeline_func = self._get_pipeline_func(import_path)
        pipeline_name = self._get_pipeline_name(pipeline_id)
        self._validate_name(pipeline_name)
        output_filename = self._get_pipeline_job_spec_filename(pipeline_name)
        output_path = os.path.join(output_dir, output_filename)

        # compute compiler arguments
        compile_args = pconfig.get('compile_args', {})
        if compile_args is None:
            compile_args = {}
        compile_args['pipeline_func'] = pipeline_func
        compile_args['package_path'] = output_path
        compile_args['pipeline_name'] = pipeline_name

        # compile pipeline
        self.compiler.compile(**compile_args)

        return output_path

    def run_pipeline(
        self,
        pipeline_id: str,
        job_spec_path: str
    ) -> Dict[str, Any]:
        # pipeline config
        pconfig = (self.config
                   [CONFIG_PIPELINES_SECTION]
                   [pipeline_id])
        # run section may be left unset if only default params are needed.
        pconfig = pconfig.get(CONFIG_RUN_SUBSECTION, None)
        if pconfig is None:  # protects against unset or nonetype in config
            pconfig = {}

        # computed parameters
        storage_root = self.config['cloud']['storage_root']
        pipeline_root = os.path.join(storage_root, 'pipelines')

        # compute run arguments
        run_args = pconfig.get('run_args', None)
        if run_args is None:  # protects against nonetype in config
            run_args = {}
        run_args['job_spec_path'] = job_spec_path
        run_args['pipeline_root'] = pipeline_root

        # automatic labels
        labels = run_args.get('labels', {})
        labels['release_version'] = self.config['release']['version']
        labels['app_name'] = self.config['app_name']
        labels['pipeline_id'] = pipeline_id
        # Please include this line to allow GCP calculate usage that is derived
        # from the Vertex MLOPs Template.
        labels['vertex_mlops_template'] = "yes"  # TODO: replace with version
        run_args['labels'] = labels

        run_response = self.client.create_run_from_job_spec(**run_args)
        return run_response
