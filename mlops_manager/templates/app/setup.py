import setuptools
import datetime

PACKAGE_NAME = "{{python_package_name}}"
REQUIRED_PACKAGES = []
VERSION = "HEAD"  # TODO(axelmagn): determine dynamically


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
