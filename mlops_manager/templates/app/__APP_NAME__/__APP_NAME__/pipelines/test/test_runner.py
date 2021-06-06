from .. import runner
from ...config import Config
import os
import tempfile

CONFIG = Config(config_init={
    "app_name": "test_app",
    "release": {
        "version": "test"
    },
    "pipelines": {
        "hello-world": {
            "python_path": "{{app_name}}.pipelines.hello_pipeline.hello_pipeline",
        },
    },
})


def test_can_build_hello_pipeline():
    output_dir = tempfile.mkdtemp()
    output_path = runner.PipelineRunner(config=CONFIG).build_pipeline(
        pipeline_id="hello-world",
        output_dir=output_dir,
    )

    written_dir, written_filename = output_path.rsplit('/', 1)

    # check that file was written to output dir
    assert os.path.samefile(output_dir, written_dir)

    # check that we wrote the expected filename
    assert written_filename == "test_app-hello-world-job-test.json"

    # check that the written file exists
    assert os.path.isfile(output_path)

    # check that the written file is nonempty
    assert os.path.getsize(output_path) > 0
