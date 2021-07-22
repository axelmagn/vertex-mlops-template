"""
Example pipeline that trains and deploys a model to classify apparel using the
fashion-mnist dataset.
"""

# KFP Lightweight Components are required to be self-contained, including imports.
# https://www.kubeflow.org/docs/components/pipelines/sdk/python-function-components/
# pylint: disable=import-outside-toplevel

from kfp import dsl
from kfp.v2.dsl import (Dataset, Input, Metrics, Model, Output, component)

from ...config import get_config


@component(base_image=get_config()['release']['images']['default'])
def example_gen(
    train_dataset_raw: Output[Dataset],
    test_dataset_raw: Output[Dataset],
    metrics: Output[Metrics],
):
    """
    Generate examples from the TFDS dataset.

    For non-trivial examples, this step could be replaced with an ETL step that
    prepares upstream data sources for training.  More advanced workflows would
    run data preparation tasks as separate pipelines, so that they may be
    prepared consistently between experimentation and productionization phases.
    """
    import numpy as np
    from tensorflow import keras

    data = keras.datasets.fashion_mnist.load_data()
    (train_images, train_labels), (test_images, test_labels) = data

    # validate data shape.
    # data validation could be done as a separate component, but for this
    # simple example it gives this component something nontrivial to do
    n_train_records = train_images.shape[0]
    assert n_train_records == train_labels.shape[0]
    metrics.log_metric("n_train_records", float(n_train_records))
    n_test_records = test_images.shape[0]
    assert n_test_records == test_labels.shape[0]
    metrics.log_metric("n_test_records", float(n_test_records))

    # write datasets as npz files
    with open(train_dataset_raw.path, 'wb') as file:
        np.savez(file, images=train_images, labels=train_labels)
    with open(test_dataset_raw.path, 'wb') as file:
        np.savez(file, images=test_images, labels=test_labels)


@component(base_image=get_config()['release']['images']['default'])
def preprocess(
    raw_dataset: Input[Dataset],
    clean_dataset: Output[Dataset],
):
    """
    Preprocess examples in preparation for training.

    In this example, each image is normalized on a range of [0.0,1.0].

    For larger datasets, consider delegating transformation steps to a big data
    engine such as Dataflow via Beam jobs.
    """
    import numpy as np

    with open(raw_dataset.path, 'rb') as file:
        npzfile = np.load(file)
        images = npzfile['images']
        labels = npzfile['labels']

    # normalize images
    images = images / 255.0

    with open(clean_dataset.path, 'wb') as file:
        np.savez(file, images=images, labels=labels)


@component(base_image=get_config()['release']['images']['default'])
def train(
    config_str: str,
    train_dataset_clean: Input[Dataset],
    trained_model: Output[Model],
):
    """
    Train a simple model using the Vertex Training service.

    This step demonstrates how the app release image may be reused to delegate
    tasks to specialized services. In general, be careful not to execute
    heavyweight tasks directly within a Pipelines Component. Pipelines perform
    best as an orchestration layer that delegates heavy tasks to other services.
    By decoupling orchestration from execution, it will be easier to scale
    training tasks according to their needs.
    """
    # This function uses a lot of local variables to unpack config values.
    # While we could certainly inline some of them, extracting them this way
    # helps catch any KeyErrors cleanly, and ensure that we have all values
    # available before we start.
    # pylint: disable=too-many-locals

    # note how by using the release image as our base image, we can import and
    # use code from other modules in our code base.  This principle can be
    # applied beyond config.
    from {{app_name}}.config import init_global_config

    from google.cloud import aiplatform as aip
    import logging

    # load config and extract used values
    config = init_global_config(config_strings=[config_str])
    app_name = config['app_name']
    project = config['cloud']['project']
    region = config['cloud']['region']
    service_account = config['cloud'].get('service_account', None)
    tensorboard_id = config['cloud'].get('tensorboard_id', None)
    # TODO(axelmagn): configure for GPU training
    train_image_uri = config['release']['images']['cpu']
    predict_image_uri = config['release']['images']['predict']

    staging_bucket = f"{app_name}-{region}-staging"
    aip.init(project=project, location=region, staging_bucket=staging_bucket)

    dataset_uri = train_dataset_clean.uri
    output_uri = trained_model.uri

    logging.info("dataset_uri: %s", dataset_uri)
    logging.info("output_uri: %s", output_uri)

    train_job = aip.CustomContainerTrainingJob(
        display_name="train-fashion-mnist",
        container_uri=train_image_uri,
        command=[
            "python",
            "-m", app_name,
            "--config-string", config_str,
            "task",
            "{{app_name}}.trainers.fashion_mnist.task.train",
        ],
        staging_bucket=staging_bucket,
        model_serving_container_image_uri=predict_image_uri
    )

    trained_model = train_job.run(
        replica_count=1,
        base_output_dir=output_uri,
        environment_variables={
            "AIP_TRAINING_DATA_URI": dataset_uri,
        },
        sync=True,
        service_account=service_account,
        tensorboard=tensorboard_id
    )


@component(base_image=get_config()['release']['images']['default'])
def evaluate(
    test_dataset_clean: Input[Dataset],
    trained_model: Input[Model],
    metrics: Output[Metrics],
):
    """Evaluate the trained model."""
    from tensorflow import keras
    import numpy as np
    import os

    with open(test_dataset_clean.path, 'rb') as file:
        npzfile = np.load(file)
        test_images = npzfile['images']
        test_labels = npzfile['labels']

    model = keras.models.load_model(os.path.join(trained_model.path, 'model'))

    test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)

    metrics.log_metric("test_loss", test_loss)
    metrics.log_metric("test_acc", test_acc)


@ dsl.pipeline()
def pipeline():
    """Fashion MNIST Training Pipeline"""

    # KFP magic handles parameter interpolation between components, raising
    # warnings during linting.
    # pylint: disable=no-value-for-parameter
    # pylint: disable=no-member
    config = get_config()

    eg_task = example_gen()
    train_dataset_raw = eg_task.outputs['train_dataset_raw']
    test_dataset_raw = eg_task.outputs['test_dataset_raw']

    train_preprocess_task = preprocess(train_dataset_raw)
    train_dataset_clean = train_preprocess_task.outputs['clean_dataset']

    test_preprocess_task = preprocess(test_dataset_raw)
    test_dataset_clean = test_preprocess_task.outputs['clean_dataset']

    train_task = train(
        config_str=config.dumps(),
        train_dataset_clean=train_dataset_clean,
    )
    trained_model = train_task.outputs['trained_model']

    _ = evaluate(test_dataset_clean, trained_model)
