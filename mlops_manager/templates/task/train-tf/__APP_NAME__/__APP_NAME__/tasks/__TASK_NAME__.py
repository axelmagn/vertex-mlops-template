"""TODO(author): a brief docstring describing the task"""

import argparse
import os

import tensorflow as tf


def run(_args):
    # validate and parse environment variables
    if 'AIP_MODEL_DIR' not in os.environ:
        raise KeyError(
            'The `AIP_MODEL_DIR` environment variable has not been ' +
            'set. See https://cloud.google.com/ai-platform-unified/docs/tutorials/image-recognition-custom/training'
        )
    output_directory = os.environ['AIP_MODEL_DIR']

    dataset = load_data()
    dataset = preprocess(dataset)
    model = build_model()
    model = train_model(model, dataset)
    model.save(output_directory)


def parse_args() -> argparse.Namespace:
    """Parse task arguments"""
    parser = argparse.ArgumentParser()

    # Define any command line arguments for the task here.  these are often
    # hyperparameters such as layer depth or width.
    #
    # parser.add_argument(...)

    return parser.parse_args()


def load_data() -> tf.data.Dataset:
    """Load data into a tf Dataset"""

    # Load your data from network or disk.
    # See: https://www.tensorflow.org/io
    return tf.data.Dataset.from_tensor_slices([])


def preprocess(dataset) -> tf.data.Dataset:
    """Prepare tf dataset for training"""

    # perform any feature engineering or transformation necessary prior to
    # training.
    return dataset


def build_model() -> tf.keras.Model:
    """Build a new, uncompiled model for training"""

    # Define or import your model here.
    return tf.keras.Sequential([])


def train_model(model, dataset, epochs=10) -> tf.keras.Model:
    """Train a model on a given dataset"""
    model.compile(
        optimizer='adam',
        # tf.keras.losses.MeanSquaredError is used below as a sane default loss
        # function.  Replace with a loss from tf.keras.losses that is
        # appropriate for the problem.
        loss=tf.keras.losses.MeanSquaredError(),
        metrics=['accuracy'],
    )
    model.fit(
        dataset,
        epochs=epochs,  # replace with an appropriate number of epochs for
    )

    # If model outputs are classifications, optionally add a softmax layer for
    # interpretability:
    #   model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])

    return model


if __name__ == "__main__":
    run(parse_args())
