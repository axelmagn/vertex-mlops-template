from kfp.v2 import dsl
from typing import NamedTuple


@dsl.component()
def example_component(text: str) -> str:
    print(text)
    return text


@dsl.pipeline(name="starter-pipeline", description="a very simple pipeline")
def pipeline(text: str = "hi there"):
    task = example_component(text)
