"""{{pipeline_name}} pipeline unit tests"""
import tempfile
import os

from {{app_name}}.pipelines import {{pipeline_name}}


def test_can_compile():
    with tempfile.TemporaryDirectory() as tmp_dir:
        package_path = os.path.join(tmp_dir, 'package.json')
        {{pipeline_name}}.compile(package_path)
        assert os.path.exists(package_path)
        assert os.path.getsize(package_path) > 0
