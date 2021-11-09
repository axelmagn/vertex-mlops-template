"""TODO(author): a brief docstring describing the task"""

import argparse
import logging
import os
import tensorflow as tf
import tensorflow_datasets as tfds

IMG_WIDTH = 128


def run(args):
    # validate and parse environment variables
    if 'AIP_MODEL_DIR' in os.environ:
        output_directory = os.environ['AIP_MODEL_DIR']
    else:
        output_directory = os.curdir
        logging.info(
            "The `AIP_MODEL_DIR` environment variable has not been set.  " +
            "Model will be saved to current directory.")

    dataset = load_data()
    dataset = preprocess(dataset)
    model = build_model()
    model = train_model(model, dataset, epochs=args.epochs)

    logging.info("Saving model to '%s' ..." % output_directory)
    model.save(output_directory)


def parse_args() -> argparse.Namespace:
    """Parse task arguments"""
    parser = argparse.ArgumentParser()

    parser.add_argument("--epochs", type=int,
                        help="NUmber of training epochs.", default=10)

    return parser.parse_args()


def load_data() -> tf.data.Dataset:
    """Load data into a tf Dataset"""
    logging.info('Loading data ...')
    return tfds.load('tf_flowers:3.*.*',
                     split='train',
                     try_gcs=True,
                     shuffle_files=True,
                     as_supervised=True)


def preprocess(dataset) -> tf.data.Dataset:
    """Prepare tf dataset for training"""
    logging.info('Preprocessing data ...')
    dataset = dataset.map(normalize_img_and_label,
                          num_parallel_calls=tf.data.experimental.AUTOTUNE)
    dataset = dataset.cache()
    dataset = dataset.shuffle(1000)
    dataset = dataset.batch(128)
    dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)
    return dataset


def normalize_img(image):
    """Normalizes image.

    * Resizes image to IMG_WIDTH x IMG_WIDTH pixels
    * Casts values from `uint8` to `float32`
    * Scales values from [0, 255] to [0, 1]

    Returns:
      A tensor with shape (IMG_WIDTH, IMG_WIDTH, 3). (3 color channels)
    """
    image = tf.image.resize_with_pad(image, IMG_WIDTH, IMG_WIDTH)
    return image / 255.


def normalize_img_and_label(image, label):
    """Normalizes image and label.

    * Performs normalize_img on image
    * Passes through label unchanged

    Returns:
      Tuple (image, label) where
      * image is a tensor with shape (IMG_WIDTH, IMG_WIDTH, 3). (3 color
        channels)
      * label is an unchanged integer [0, 4] representing flower type
    """
    return normalize_img(image), label


def build_model() -> tf.keras.Model:
    """Build a new, uncompiled model for training"""
    logging.info('Creating model ...')
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(16,
                               3,
                               padding='same',
                               activation='relu',
                               input_shape=(IMG_WIDTH, IMG_WIDTH, 3)),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(32, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dense(5)  # 5 classes
    ])
    return model


def train_model(model, dataset, epochs=10) -> tf.keras.Model:
    """Train a model on a given dataset"""
    logging.info('Training model ...')
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy'],
    )
    model.fit(dataset, epochs=epochs,)
    # Add softmax layer for interpretability
    model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])
    return model


if __name__ == "__main__":
    run(parse_args())
