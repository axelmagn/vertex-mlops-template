from ...config import Config

CONFIG = Config(config_init={
    "app_name": "app",
    "release": {
        "version": "vtest"
    },
    "pipelines": {
        "hello_world": {
            "build": {
                "python_path": "{{app_name}}.pipelines.hello_pipeline.hello_pipeline",
            },
            "run": {},
        },
    },
})


# more of an integration test than a unit test.  Makes sure that build_pipeline
# produces the expected file.
# TODO(axelmagn): separate with pytest mark
def test_compiler_builds_hello_pipeline():
    from .. import runner as pipeline_runner
    import os
    import tempfile
    from unittest.mock import Mock
    from kfp.v2.compiler import Compiler

    # use real compiler.  side effects are isolated to temp dir.
    compiler = Compiler()
    client = Mock()
    # use temporary output dir to isolate side effects
    output_dir = tempfile.mkdtemp()

    runner = pipeline_runner.PipelineRunner(
        config=CONFIG, client=client, compiler=compiler)

    output_path = runner.build_pipeline(
        pipeline_id="hello_world",
        output_dir=output_dir,
    )

    written_dir, written_filename = output_path.rsplit('/', 1)

    # check that file was written to output dir
    assert os.path.samefile(output_dir, written_dir)

    # check that we wrote the expected filename
    assert written_filename == "test-app-hello-world-test-job-spec.json"

    # check that the written file exists
    assert os.path.isfile(output_path)

    # check that the written file is nonempty
    assert os.path.getsize(output_path) > 0
