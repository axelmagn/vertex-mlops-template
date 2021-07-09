from ..harness import PipelineHarness
from ...config import Config
from kfp.v2.compiler import Compiler
from unittest.mock import Mock
import os
import tempfile

CONFIG = Config(config_init={
    "app_name": "app",
    "release": {
        "label": "test"
    },
    "cloud": {
        "storage_root": "gs://dummy_bucket/"
    },
    "pipelines": {
        "hello_world": {
            "build": {
                "path": "{{app_name}}.pipelines.test.hello_pipeline.pipeline",
            },
            "run": {},
        },
    },
})


# more of an integration test than a unit test.  Makes sure that build_pipeline
# produces the expected file.
# TODO(axelmagn): separate with pytest mark
def test_compiler_builds_hello_pipeline():

    # use real compiler.  side effects are isolated to temp dir.
    compiler = Compiler()
    client = Mock()
    # use temporary output dir to isolate side effects
    output_dir = tempfile.mkdtemp()

    harness = PipelineHarness(
        config=CONFIG, client=client, compiler=compiler)

    output_path = harness.build_pipeline(
        pipeline_id="hello_world",
        output_dir=output_dir,
    )

    written_dir, written_filename = output_path.rsplit('/', 1)

    # check that file was written to output dir
    assert os.path.samefile(output_dir, written_dir)

    # check that we wrote the expected filename
    assert written_filename == "hello-world.json"

    # check that the written file exists
    assert os.path.isfile(output_path)

    # check that the written file is nonempty
    assert os.path.getsize(output_path) > 0


def test_run_pipeline():
    compiler = Mock()
    client = Mock()
    client_response = "MOCK_RESPONSE"
    client.create_run_from_job_spec.return_value = client_response
    harness = PipelineHarness(config=CONFIG, client=client, compiler=compiler)
    run_response = harness.run_pipeline(
        pipeline_id="hello_world",
        job_spec_path="job_spec_path.json",
    )

    # check that client call behaves as expected
    client.create_run_from_job_spec.assert_called_with(
        job_spec_path="job_spec_path.json",
        pipeline_root="gs://dummy_bucket/pipelines",
        labels={
            "release": "test",
            "app_name": "app",
            "pipeline_id": "hello_world",
            "vertex_mlops_template": "yes",
        },
    )

    # check that run_pipeline returns the client's response
    assert run_response == client_response
