import setuptools
import os

PACKAGE_NAME = "{{app_name}}"
# TODO(axelmagn): less brittle pathing
REQUIRED_PACKAGES = []
if os.path.exists('requirements.txt'):
    with open('requirements.txt') as f:
        REQUIRED_PACKAGES = f.read().strip().split('\n')
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
