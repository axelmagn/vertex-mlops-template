import setuptools
import datetime

PACKAGE_NAME = "{{app_name}}"
# TODO(axelmagn): unify with requirements.txt
REQUIRED_PACKAGES = [
    "kfp~=1.6.2",
    "PyYAML~=5.4.1",
]
VERSION = "0.0.1"  # TODO(axelmagn): determine dynamically


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
