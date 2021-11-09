"""A simple pipeline for use in testing."""

# KFP Lightweight Components are required to be self-contained, including imports.
# https://www.kubeflow.org/docs/components/pipelines/sdk/python-function-components/
# pylint: disable=import-outside-toplevel

from datetime import datetime
from typing import NamedTuple

from kfp import dsl
from kfp.v2.dsl import component


TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")


@component()
def hello_world(text: str) -> str:
    """Print and return input."""
    print(text)
    return text


@component()
def two_outputs(
    text: str,
) -> NamedTuple(
    "Outputs",
    [
        ("output_one", str),  # Return parameters
        ("output_two", str),
    ],
):
    """Print input an interpolate into two outputs."""
    out1 = f"output one from text: {text}"
    out2 = f"output two from text: {text}"
    print("output one: {}; output_two: {}".format(out1, out2))
    return (out1, out2)


@component()
def consumer(text1: str, text2: str, text3: str):
    """Interpolate and print inputs."""
    print(f"text1: {text1}; text2: {text2}; text3: {text3}")


@dsl.pipeline(
    name="hello-pipeline",
    description="A simple intro pipeline",
)
def pipeline(text: str = "hi there"):
    """Pipeline definition exercising dummy components."""
    # KFP magic handles parameter interpolation between components, raising
    # warnings during linting.
    # pylint: disable=no-value-for-parameter
    # pylint: disable=no-member
    hw_task = hello_world(text)
    two_outputs_task = two_outputs(text)
    _consumer_task = consumer(
        hw_task.output,
        two_outputs_task.outputs["output_one"],
        two_outputs_task.outputs["output_two"],
    )
