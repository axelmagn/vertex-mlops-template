import setuptools
import os

PACKAGE_NAME = "{{app_name}}"
# TODO(axelmagn): unify with requirements.txt
REQUIRED_PACKAGES = [
    "kfp",
    "PyYAML",
    "tensorflow"
    # "kfp~=1.6.2",
    # "PyYAML~=5.4.1",
    # "tensorflow~=2.5.0",
    # "numpy~=1.20.3",
]
VERSION = os.environ.get("PYTHON_PACKAGE_VERSION", "0.0.1")


def setup():
    setuptools.setup(
        name=PACKAGE_NAME,
        version=VERSION,
        install_requires=REQUIRED_PACKAGES,
        packages=setuptools.find_packages(),
        # TODO(axelmagn): package data
    )


if __name__ == "__main__":
    setup()
