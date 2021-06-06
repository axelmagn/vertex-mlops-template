from kfp.v2 import compiler
from collections.abc import Callable
from typing import Optional, Mapping, Any
from ..config import Config, get_config
import importlib
import os
import re


class PipelineRunner(object):
    def __init__(self, config: Optional[Config] = None):
        if config is None:
            config = get_config()
        self.config = config

    def _get_pipeline_func(
        self,
        import_path: str,
    ) -> Callable[..., None]:
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

    def _get_pipeline_job_name(
        self,
        pipeline_name: str,
        version_id: str,
    ):
        """Get the correct filename for a pipeline job."""
        return f"{pipeline_name}-job-{version_id}.json"

    def _get_pipeline_name(self, app_name: str, pipeline_id: str):
        """Get the canonical name for a pipeline from an app"""
        return f"{app_name}-{pipeline_id}"

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
            version_id: version tag for the job file

        Returns:
            Path of the compiled pipeline job file.
        """
        # load variables from config
        app_name = self.config['app_name']
        release_version = self.config['release']['version']
        pconfig = self.config['pipelines'][pipeline_id]  # pipeline config
        import_path = pconfig['python_path']
        params = pconfig.get('parameters', None)
        type_check = pconfig.get('type_check', None)

        # load computed variables
        pipeline_func = self._get_pipeline_func(import_path)
        pipeline_name = self._get_pipeline_name(app_name, pipeline_id)
        output_filename = self._get_pipeline_job_name(pipeline_name,
                                                      release_version)
        output_path = os.path.join(output_dir, output_filename)

        # compile pipeline
        compiler.Compiler().compile(
            pipeline_func=pipeline_func,
            package_path=output_path,
            pipeline_name=pipeline_id,
            pipeline_parameters=params,
            type_check=type_check,
        )
        return output_path
