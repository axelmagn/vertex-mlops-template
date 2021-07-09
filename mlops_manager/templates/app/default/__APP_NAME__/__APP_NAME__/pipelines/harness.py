from ..config import Config, get_config
from ..constants import *
from ..util import dynamic_import_func, get_collection
from kfp.v2.compiler import Compiler
from kfp.v2.google.client.client import AIPlatformClient
from typing import Optional, Any, Dict
import importlib
import os
import re


# Pattern for valid names used as a uCAIP resource name.
_VALID_NAME_PATTERN = re.compile('^[a-z][-a-z0-9]{0,127}$')


class PipelineHarness(object):
    """Build and run pipelines."""

    def __init__(
        self,
        # TODO(axelmagn): decouple from config
        config: Optional[Config] = None,
        client: Optional[AIPlatformClient] = None,
        compiler: Optional[Compiler] = None,
    ):
        self.config = get_config() if config is None else config
        self._client = client
        self.compiler = Compiler() if compiler is None else compiler

    def _get_client(self):
        """Lazy load default client to avoid config errors in some environments"""
        if self._client is None:
            self._client = self._get_default_client()
        return self._client

    def _get_default_client(self):
        project_id = self.config['cloud']['project']
        region = self.config['cloud']['region']
        return AIPlatformClient(
            project_id,
            region
        )

    def _get_pipeline_job_spec_filename(
        self,
        pipeline_name: str,
    ):
        """Get the correct filename for a pipeline job."""
        # return f"{pipeline_name}-job-spec.json"
        return f"{pipeline_name}.json"

    def _get_pipeline_name(
        self,
        pipeline_id: str,
    ):
        """Get the canonical name for a pipeline from an app"""
        # app_name = self.config['app_name']
        # release_version = self.config['release']['label']
        # name = f"{app_name}-{pipeline_id}-{release_version}"
        return self._sanitize_name(pipeline_id)

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
                   [CONFIG_PIPELINES]
                   [pipeline_id]
                   [CONFIG_BUILD])
        import_path = pconfig[CONFIG_PATH]

        # load computed variables
        pipeline_func = dynamic_import_func(import_path)
        pipeline_name = self._get_pipeline_name(pipeline_id)
        self._validate_name(pipeline_name)
        output_filename = self._get_pipeline_job_spec_filename(pipeline_name)
        output_path = os.path.join(output_dir, output_filename)

        # compute compiler arguments
        kwargs = {}
        kwargs['pipeline_func'] = pipeline_func
        kwargs['package_path'] = output_path
        kwargs['pipeline_name'] = pipeline_name
        kwargs.update(get_collection(pconfig, CONFIG_KWARGS))

        # compile pipeline
        self.compiler.compile(**kwargs)

        return output_path

    def run_pipeline(
        self,
        pipeline_id: str,
        job_spec_path: str,
    ) -> Dict[str, Any]:
        # run section may be left unset if only default params are needed.
        pconfig = get_collection(
            self.config, [CONFIG_PIPELINES, pipeline_id, CONFIG_RUN])

        # computed parameters
        storage_root = self.config['cloud']['storage_root']
        pipeline_root = os.path.join(storage_root, 'pipelines')

        # compute run arguments
        kwargs = get_collection(pconfig, 'kwargs')
        kwargs['job_spec_path'] = job_spec_path
        kwargs['pipeline_root'] = pipeline_root

        # automatic labels
        labels = {}
        labels['release'] = self.config['release']['label']
        labels['app_name'] = self.config['app_name']
        labels['pipeline_id'] = pipeline_id
        # Please include the following line to allow GCP calculate usage that is
        # derived from the Vertex MLOPs Template.
        labels['vertex_mlops_template'] = "yes"
        print("LABELS:")
        print(get_collection(kwargs, 'labels'))
        labels.update(get_collection(kwargs, 'labels'))
        kwargs['labels'] = labels

        client = self._get_client()
        run_response = client.create_run_from_job_spec(**kwargs)
        return run_response

    def schedule_pipeline(
        self,
        pipeline_id: str,
        job_spec_path: str,
        schedule: Optional[str] = None
    ):
        # pipeline config
        pconfig = get_collection(
            self.config, [CONFIG_PIPELINES, pipeline_id, CONFIG_SCHEDULE])

        # computed parameters
        storage_root = self.config['cloud']['storage_root']
        pipeline_root = os.path.join(storage_root, 'pipelines')

        # compute run arguments
        kwargs = {}
        kwargs['job_spec_path'] = job_spec_path
        kwargs['pipeline_root'] = pipeline_root
        kwargs.update(get_collection(pconfig, CONFIG_KWARGS))
        if schedule is not None:
            kwargs['schedule'] = schedule

        # TODO(axelmagn): labels

        client = self._get_client()
        response = client.create_schedule_from_job_spec(**kwargs)
        return response

    def deploy(self):
        deploy_config = get_collection(
            self.config, [CONFIG_DEPLOY, CONFIG_PIPELINES])
        pipeline_manifest = get_collection(
            self.config, [CONFIG_RELEASE, CONFIG_PIPELINES])
        results = {}
        for pipeline_id, schedule in deploy_config.items():
            job_spec_path = pipeline_manifest[pipeline_id][CONFIG_JOB_SPEC]
            if schedule == CONFIG_RUN_ONCE:
                results[pipeline_id] = self.run_pipeline(
                    pipeline_id, job_spec_path)
            else:
                results[pipeline_id] = self.schedule_pipeline(
                    pipeline_id, job_spec_path, schedule)
