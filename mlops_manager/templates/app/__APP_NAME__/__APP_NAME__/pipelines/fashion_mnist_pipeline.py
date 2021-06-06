# TODO(axelmagn): delete in favor of standalone pipeline template
from kfp import dsl

from kfp.v2.dsl import (
    Dataset,
    Input,
    Metrics,
    Model,
    Output,
    component,
)


# TODO(axelmagn): use built app image
@component(base_image="gcr.io/deeplearning-platform-release/tf2-cpu.2-5")
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


@component(base_image="gcr.io/deeplearning-platform-release/tf2-cpu.2-5")
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
@component(base_image="gcr.io/deeplearning-platform-release/tf2-cpu.2-5")
def train(
    train_dataset_clean: Input[Dataset],
    trained_model: Output[Model],
    metrics: Output[Metrics],
):
    # TODO(axelmagn): invoke vertex custom training
    from tensorflow import keras
    import numpy as np

    with open(train_dataset_clean.path, 'rb') as f:
        npzfile = np.load(f)
        train_images = npzfile['images']
        train_labels = npzfile['labels']

    # Define the model using Keras.
    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(10)
    ])

    model.compile(optimizer='adam',
                  loss=keras.losses.SparseCategoricalCrossentropy(
                      from_logits=True),
                  metrics=['accuracy'])

    # Run a training job with specified number of epochs
    train_history = model.fit(train_images, train_labels, epochs=10)
    for history_key in train_history.history:
        history_value = train_history.history[history_key]
        if isinstance(history_value, int) or isinstance(history_value, float):
            metrics.log_metric(f"train_{history_key}", float(history_value))

    model.save(trained_model.path)


# TODO(axelmagn): use built app image
@component(base_image="gcr.io/deeplearning-platform-release/tf2-cpu.2-5")
def evaluate(
    test_dataset_clean: Input[Dataset],
    trained_model: Input[Model],
    metrics: Output[Metrics],
):
    import numpy as np
    from tensorflow import keras

    with open(test_dataset_clean.path, 'rb') as f:
        npzfile = np.load(f)
        test_images = npzfile['images']
        test_labels = npzfile['labels']

    model = keras.models.load_model(trained_model.path)

    test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)

    metrics.log_metric("test_loss", test_loss)
    metrics.log_metric("test_acc", test_acc)


@dsl.pipeline(
    name="fashion-mnist-train",
    description="Train a simple classifier for fashion-mnist problem",
)
def fashion_mnist_pipeline():
    eg_task = example_gen()
    train_dataset_raw = eg_task.outputs['train_dataset_raw']
    test_dataset_raw = eg_task.outputs['test_dataset_raw']

    train_preprocess_task = preprocess(train_dataset_raw)
    train_dataset_clean = train_preprocess_task.outputs['clean_dataset']

    test_preprocess_task = preprocess(test_dataset_raw)
    test_dataset_clean = test_preprocess_task.outputs['clean_dataset']

    train_task = train(train_dataset_clean)
    trained_model = train_task.outputs['trained_model']

    eval_task = evaluate(test_dataset_clean, trained_model)
