"""
Fashion MNIST trainer function.

NOTE: this is a monolithic script for the purpose of prototyping.
TODO: break down into modular components
"""

import tensorflow as tf
import numpy as np
import logging
from google.cloud import storage
import tempfile


def train(
        training_data_uri,
        model_dir_uri,
        tensorboard_log_dir_uri=None,
        feedforward_width=128,
        feedforward_depth=1,
        input_shape=(28, 28),
        optimizer='adam',
        epochs=10,
):
    """
    Train a densely connected neural network for fashion_mnist problem.

    TODO: parameters docstring
    """
    logging.info("Training dense network")
    logging.info(f"training_data_uri: {training_data_uri}")
    logging.info(f"model_dir_uri: {model_dir_uri}")
    logging.info(f"tensorboard_log_dir_uri: {tensorboard_log_dir_uri}")
    logging.info(f"feedforward_width: {feedforward_width}")
    logging.info(f"feedforward_depth: {feedforward_depth}")
    logging.info(f"input_shape: {input_shape}")
    logging.info(f"optimizer: {optimizer}")
    logging.info(f"epochs: {epochs}")

    # load training dataset
    with tf.io.gfile.GFile(training_data_uri, mode='rb') as f:
        train_npz = np.load(f)
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
