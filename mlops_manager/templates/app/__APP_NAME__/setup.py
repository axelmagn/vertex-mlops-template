import setuptools
import yaml
import os

PACKAGE_NAME = "{{app_name}}"

REQUIRED_PACKAGES = [
    "kfp~=1.6.2",
    "PyYAML~=5.4.1",
    "tensorflow~=2.5.0",
    # "numpy~=1.20.3",
]


def setup():
    project_root = os.path.dirname(os.path.realpath(__file__))
    app_config_path = os.path.join(project_root, 'config/app.yaml')
    with open(app_config_path, 'r') as f:
        config = yaml.safe_load(f)
    setuptools.setup(
        name=config['name'],
        version=['version'],
        install_requires=REQUIRED_PACKAGES,
        packages=setuptools.find_packages(),
        include_package_data=True,
    )


if __name__ == "__main__":
    setup()
