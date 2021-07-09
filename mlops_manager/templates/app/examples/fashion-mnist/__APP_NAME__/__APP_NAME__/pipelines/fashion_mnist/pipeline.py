# TODO(axelmagn): delete in favor of standalone pipeline template
from ...config import get_config
from kfp import dsl
from kfp.v2.dsl import (Dataset, Input, Metrics, Model, Output, component)


# TODO(axelmagn): use built app image
@component(base_image=get_config()['release']['images']['default'])
def example_gen(
    train_dataset_raw: Output[Dataset],
    test_dataset_raw: Output[Dataset],
    metrics: Output[Metrics],
):
    import numpy as np
    from tensorflow import keras

    fashion_mnist = keras.datasets.fashion_mnist
    data = keras.datasets.fashion_mnist.load_data()
    (train_images, train_labels), (test_images, test_labels) = data

    # validate data shape.
    # data validation could be done as a separate component, but for this simple
    # example it gives this component something nontrivial to do
    n_train_records = train_images.shape[0]
    assert n_train_records == train_labels.shape[0]
    metrics.log_metric("n_train_records", float(n_train_records))
    n_test_records = test_images.shape[0]
    assert n_test_records == test_labels.shape[0]
    metrics.log_metric("n_test_records", float(n_test_records))

    # write datasets as npz files
    with open(train_dataset_raw.path, 'wb') as f:
        np.savez(f, images=train_images, labels=train_labels)
    with open(test_dataset_raw.path, 'wb') as f:
        np.savez(f, images=test_images, labels=test_labels)

# TODO(axelmagn): use built app image


@component(base_image=get_config()['release']['images']['default'])
def preprocess(
    raw_dataset: Input[Dataset],
    clean_dataset: Output[Dataset],
):
    import numpy as np

    with open(raw_dataset.path, 'rb') as f:
        npzfile = np.load(f)
        images = npzfile['images']
        labels = npzfile['labels']

    # normalize images
    images = images / 255.0

    with open(clean_dataset.path, 'wb') as f:
        np.savez(f, images=images, labels=labels)


# TODO(axelmagn): use built app image
@component(base_image=get_config()['release']['images']['default'])
def train(
    config_str: str,
    train_dataset_clean: Input[Dataset],
    trained_model: Output[Model],
):
    from {{app_name}}.config import init_global_config

    from google.cloud import aiplatform as aip
    import logging
    import yaml

    # load config and extract used values
    config = init_global_config(config_strings=[config_str])
    app_name = config['app_name']
    project = config['cloud']['project']
    region = config['cloud']['region']
    service_account = config['cloud'].get('service_account', None)
    tensorboard_id = config['cloud'].get('tensorboard_id', None)
    # TODO: build other images
    train_image_uri = config['release']['images']['default']
    predict_image_uri = config['release']['images']['predict']

    staging_bucket = f"{app_name}-{region}-staging"
    aip.init(project=project, location=region, staging_bucket=staging_bucket)

    dataset_uri = train_dataset_clean.uri
    output_uri = trained_model.uri

    logging.info(f"dataset_uri: {dataset_uri}")
    logging.info(f"output_uri: {output_uri}")

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
    from tensorflow import keras
    import numpy as np
    import os

    with open(test_dataset_clean.path, 'rb') as f:
        npzfile = np.load(f)
        test_images = npzfile['images']
        test_labels = npzfile['labels']

    model = keras.models.load_model(os.path.join(trained_model.path, 'model'))

    test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)

    metrics.log_metric("test_loss", test_loss)
    metrics.log_metric("test_acc", test_acc)


@ dsl.pipeline()
def pipeline():
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

    eval_task = evaluate(test_dataset_clean, trained_model)
