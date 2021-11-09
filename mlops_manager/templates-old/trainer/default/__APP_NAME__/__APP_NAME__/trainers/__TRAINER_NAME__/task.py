"""{{trainer_name}} task."""

# For more on custom training on Vertex AI, refer to:
# https://cloud.google.com/vertex-ai/docs/training/custom-training

# For more complex trainers, we recommend organizing into multiple files within
# the trainer directory. If there are multiple trainers depending on shared
# models or similar code, consider organizing these dependencies into
# higher-level submodules within the app.

import os

from ...cli import task, arg


@task([
    # Insert task arguments here in ArgParse format.
    # See {{app_name}}.commands for examples.
    # By invoking via the `task` command, rather than running this script
    # directly, your training task will be able to take advantage of the app's
    # configuration system.
])
def train(args):
    # This is an incomplete set of environment variables set in the Vertex
    # Training environment, depending on what configurations are used.
    # More work is needed to identify the comprehensive set of environment
    # variables set by Vertex Training.
    model_dir_uri = os.environ.get('AIP_MODEL_DIR')

    # insert model training here.
    # For managed models, write results to model_dir_uri.
    # tensorflow.io can be useful for reading and writing from GCS URIs, even if
    # tensorflow is not used for training.
    pass
