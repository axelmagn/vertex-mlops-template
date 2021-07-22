"""
Fashion MNIST trainer function.

NOTE: this is a monolithic script for the purpose of prototyping.
TODO: break down into modular components
"""

import logging
import os

import numpy as np
import tensorflow as tf

from ...cli import task, arg


@task([
    arg('--width', type=int, default=128, help="feedforward width"),
    arg('--depth', type=int, default=1, help="feedforward depth"),
    arg('--input-shape', type=str, default="28,28",
        help="input shape as comma separated integers"),
    arg('--optimizer', type=str, default="adam", help="training optimizer"),
    arg('--epochs', type=int, default=10, help="training epochs"),
])
def train(args):
    """Train a densely connected neural network for fashion_mnist problem."""

    # This function uses a lot of local variables to unpack config values.
    # While we could certainly inline some of them, extracting them this way
    # helps catch any KeyErrors cleanly, and ensure that we have all values
    # available before we start.
    # pylint: disable=too-many-locals

    training_data_uri = os.environ.get('AIP_TRAINING_DATA_URI')
    model_dir_uri = os.environ.get('AIP_MODEL_DIR')
    tensorboard_log_dir_uri = os.environ.get('AIP_TENSORBOARD_LOG_DIR', None)
    feedforward_width = args.width
    feedforward_depth = args.depth
    input_shape = [int(x) for x in args.input_shape.split(',')]
    optimizer = args.optimizer
    epochs = args.epochs

    logging.info("Training dense network")
    logging.info("training_data_uri: %s", training_data_uri)
    logging.info("model_dir_uri: %s", model_dir_uri)
    logging.info("tensorboard_log_dir_uri: %s", tensorboard_log_dir_uri)
    logging.info("feedforward_width: %s", feedforward_width)
    logging.info("feedforward_depth: %s", feedforward_depth)
    logging.info("input_shape: %s", input_shape)
    logging.info("optimizer: %s", optimizer)
    logging.info("epochs: %s", epochs)

    # load training dataset
    with tf.io.gfile.GFile(training_data_uri, mode='rb') as file:
        train_npz = np.load(file)
        train_images = train_npz['images']
        train_labels = train_npz['labels']

    # Define the model using Keras.
    model = tf.keras.Sequential(
        [tf.keras.layers.Flatten(input_shape=input_shape)]
        + [
            tf.keras.layers.Dense(feedforward_width, activation='relu')
            for _ in range(feedforward_depth)
        ]
        + [tf.keras.layers.Dense(10)]
    )

    model.compile(optimizer=optimizer,
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(
                      from_logits=True),
                  metrics=['accuracy'])

    callbacks = []
    if tensorboard_log_dir_uri is not None:
        tensorboard_callback = tf.keras.callbacks.TensorBoard(
            log_dir=tensorboard_log_dir_uri,
            histogram_freq=1)
        callbacks.append(tensorboard_callback)

    # Run a training job with specified number of epochs
    # TODO: checkpoints, tensorboard
    _train_history = model.fit(
        train_images, train_labels, epochs=epochs, callbacks=callbacks)

    model.save(model_dir_uri)
