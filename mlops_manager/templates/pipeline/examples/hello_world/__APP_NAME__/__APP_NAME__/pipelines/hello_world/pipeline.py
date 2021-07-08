# TODO(axelmagn): delete in favor of standalone pipeline template
from datetime import datetime
from kfp import dsl
from kfp.v2.dsl import component
from typing import NamedTuple


TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")


@component()
def hello_world(text: str) -> str:
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
    o1 = f"output one from text: {text}"
    o2 = f"output two from text: {text}"
    print("output one: {}; output_two: {}".format(o1, o2))
    return (o1, o2)


@component()
def consumer(text1: str, text2: str, text3: str):
    print(f"text1: {text1}; text2: {text2}; text3: {text3}")


@dsl.pipeline(
    name="hello-pipeline",
    description="A simple intro pipeline",
)
def pipeline(text: str = "hi there"):
    hw_task = hello_world(text)
    two_outputs_task = two_outputs(text)
    _consumer_task = consumer(
        hw_task.output,
        two_outputs_task.outputs["output_one"],
        two_outputs_task.outputs["output_two"],
    )
