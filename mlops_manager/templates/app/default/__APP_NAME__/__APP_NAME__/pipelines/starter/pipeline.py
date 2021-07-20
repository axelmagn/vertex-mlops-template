"""A simple starter pipeline."""

# KFP Lightweight Components are required to be self-contained, including imports.
# https://www.kubeflow.org/docs/components/pipelines/sdk/python-function-components/
# pylint: disable=import-outside-toplevel

from kfp.v2 import dsl


@dsl.component()
def example_component(text: str) -> str:
    """A simple component that prints and returns its input."""
    print(text)
    return text


@dsl.pipeline(name="starter-pipeline", description="a very simple pipeline")
def pipeline(text: str = "hi there"):
    """A simple pipeline with one component."""
    # KFP magic handles parameter interpolation between components, raising
    # warnings during linting.
    # pylint: disable=no-value-for-parameter
    # pylint: disable=no-member
    _ = example_component(text)
