from setuptools import find_packages, setup

REQUIRED_PACKAGES = ['tensorflow_datasets~=4.2.0']

setup(
    name='{{app_name}}',
    version='1.0',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    description='',  # TODO(author): description
)
