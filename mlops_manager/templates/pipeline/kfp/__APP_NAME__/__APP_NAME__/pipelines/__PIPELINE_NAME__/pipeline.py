"""{{pipeline_name}} pipeline definition"""

# The template below is just one way to organize a simple pipeline.
#
# - We know that this template is very wordy.  For a smaller, less opinionated
#   template, consider using the `kfp-minimal` variant. (Not yet implemented)
#
# - This boilerplate assumes that you are performing custom preprocessing and
#   training of a model, and that your datasets are not necessarily Vertex Managed
#   Datasets. For simple tasks such as AutoML, it may be easier to use the
#   premade Vertex KFP Components here:
#   https://github.com/kubeflow/pipelines/tree/master/components/google-cloud
#
# - For more sophisticated pipelines, consider breaking it up into data
#   ingestion, training, and deployment stages.
#
# - As pipelines grow in complexity, it's a good idea to split their logic out
#   into multiple files.  This is part of why each pipeline gets its own folder.

# pylint: disable=import-outside-toplevel
# This directive prevents lint warnings for imports within component functions.
# KFP Lightweight Components are required to use imports within their function
# definitions.
# https://www.kubeflow.org/docs/components/pipelines/sdk/python-function-components/

from kfp import dsl
from kfp.v2.dsl import (Dataset, Input, Metrics, Model, Output, component)

from ...config import get_config


# By using the app's built image as our base image, we are able to write
# components that depend on other units of code within the app.
@component(base_image=get_config()['release']['images']['cpu'])
def ingest(
    # In practice, it often makes sense to emit more than one dataset in this
    # stage (such as train / eval).  This is often where dataset splitting and
    # sampling occurs. This boilerplate only emits one for simplicity.
    dataset_raw: Output[Dataset],
        metrics: Output[Metrics]):
    """
    Collect external datasets into a manageable format for experimentation and
    training.  
    """

    # insert imports here.
    from {{app_name}}.config import get_config

    # it can be handy to retrieve task-specific variables from config.
    # delete this line if config is unused.
    _config = get_config()

    # Insert ingestion code here.
    #
    # For Big Data:
    #
    # - Dataflow and Beam can be used to manage large datasets in this stage,
    #   but are often too heavyweight for smaller problems.
    #
    # For Complex Applications:
    #
    # - for more mature pipelines, consider putting this into a separate
    #   ingestion pipeline that can be used to prepare not only the production
    #   datasets, but downsampled datasets for experimentation.
    pass


# By using the app's built image as our base image, we are able to write
# components that depend on other units of code within the app.
@component(base_image=get_config()['release']['images']['cpu'])
def preprocess(dataset_raw: Input[Dataset],
               dataset_clean: Output[Dataset],
               metrics: Output[Metrics]):
    """Prepare raw data by cleaning it and performing feature engineering."""
    # insert imports here.
    from {{app_name}}.config import get_config

    # retrieve task-specific variables from config
    # delete this line if config is unused.
    _config = get_config()

    # Insert preprocessing code here.
    #
    # For Big Data:
    #
    # - Dataflow and Beam can be used to manage large datasets in this stage,
    #   but are often too heavyweight for smaller problems.
    #
    # For Complex Applications:
    #
    # - Consider breaking this stage up into cleaning and feature engineering
    #   stages, with cleaning run as part of the dataset ingestion pipeline if
    #   separate pipelines are used.
    pass

# By using the app's built image as our base image, we are able to write
# components that depend on other units of code within the app.


@component(base_image=get_config()['release']['images']['cpu'])
def train(dataset: Input[Dataset],
          model: Output[Model],
          metrics: Output[Metrics],
          ):
    # insert imports here.
    from {{app_name}}.config import get_config
    from google.cloud import aiplatform as aip

    # retrieve task-specific variables from config
    # delete this line if config is unused.
    _config = get_config()

    # This component assumes a custom training task on Vertex AI.
    # Customize the content below to match your own training workflow.

    # We recommend that training tasks should be submitted to Vertex AI Training
    # as separate jobs.  This allows you to take advantage of Vertex AI Training
    # features, and allows pipeline infrastructure to remain relatively
    # lightweight.
    # https://cloud.google.com/vertex-ai/docs/training/custom-training
    aip.init(
        project=_config['cloud']['project'],
        location=_config['cloud']['region'],
        staging_bucket=_config['cloud']['storage_root'],

    )
    # Create a training job that leverages our app's container.
    # https://googleapis.dev/python/aiplatform/latest/aiplatform.html#google.cloud.aiplatform.CustomContainerTrainingJob
    train_job = aip.CustomContainerTrainingJob(
        display_name="{{pipeline_name}}-train",
        # To use GPU accelerators, change this to the GPU image and set the
        # `accelerator_type` parameter when calling `train_job.run`.
        container_uri=_config['release']['images']['cpu'],
        command=[
            "python", "-m", _config['app_name'],
            # by passing serialized configuration directly to our task, we can
            # make sure that the training task configuration matches that of
            # this component.
            "--config-string", _config.dumps(),
            "task",
            # Insert the import path to your training task here.
            "{{app_name}}.trainers.PLACEHOLDER.task",
        ],
    )

    # Run parameters may be configured here.
    # https://googleapis.dev/python/aiplatform/latest/aiplatform.html#google.cloud.aiplatform.CustomContainerTrainingJob.run
    _model = train_job.run(
        # For the time being, always set replica_count >= 1.  Otherwise it will
        # default to 0, currently leading to a difficult to debug error.
        replica_count=1,
    )


@component(base_image=get_config()['release']['images']['cpu'])
def evaluate(dataset_eval: Input[Dataset],
             model: Input[Model],
             metrics: Output[Metrics]):
    """Evaluate the trained model."""
    # insert imports here.
    from {{app_name}}.config import get_config

    # retrieve task-specific variables from config
    # delete this line if config is unused.
    _config = get_config()

    # insert model evaluation code here.
    #
    # - It's a judgement call whether this is better performed by your training
    #   task or not. Often it makes sense to combine this step with training.
    #   However in many other cases the model emitted from training will need to
    #   be evaluated against other models that it does not have access to, or to
    #   be evaluated by a more centralized evaluation framework.


@component(base_image=get_config()['release']['images']['cpu'])
def deploy(model: Input[Model], eval_metrics: Input[Metrics]):
    """Deploy the trained model."""
    # insert imports here.
    from {{app_name}}.config import get_config

    # retrieve task-specific variables from config
    # delete this line if config is unused.
    _config = get_config()

    # Insert deployment code here.
    # Use the results of the evaluate component to only deploy models which meet
    # the requirements for production.
    #
    # We recommend making use of Vertex AI Predictions in order to take
    # advantage of its scaling, explainability, and monitoring features.
    # https://cloud.google.com/vertex-ai/docs/predictions/getting-predictions


@dsl.pipeline()
def pipeline():
    """{{pipeline_name}} pipeline definition."""

    # pylint: disable=no-value-for-parameter
    # pylint: disable=no-member
    # KFP magic handles parameter interpolation between components, triggering
    # warnings during linting.

    # compose your pipeline components here.

    ingest_task = ingest()
    preprocess_task = preprocess(
        dataset_raw=ingest_task.outputs['dataset_raw']
    )
    train_task = train(dataset=preprocess_task.outputs['dataset_clean'])
    evaluate_task = evaluate(
        dataset_eval=preprocess_task.outputs['dataset_clean'],
        model=train_task.outputs['model'],
    )
    deploy(model=train_task.outputs['model'],
           eval_metrics=evaluate_task.outputs['metrics'])
