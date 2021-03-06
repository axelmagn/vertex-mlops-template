import kfp
import argparse
from kfp.v2 import compiler
from typing import Dict, Any
from google.cloud import aiplatform
from google_cloud_pipeline_components import aiplatform as gcc_aip

PIPELINE_NAME = "{{pipeline_name}}".replace('_', '-')


@kfp.dsl.pipeline(
    name=PIPELINE_NAME,
)
def pipeline(
    project_id: str,
    # uncomment for custom training
    # app_container_uri: str,
):
    # Use KFP components to define a pipeline here.
    # https://cloud.google.com/vertex-ai/docs/pipelines/build-pipeline#sdk
    # https://github.com/kubeflow/pipelines/tree/master/components/google-cloud
    # https://www.kubeflow.org/docs/components/pipelines/sdk/build-pipeline/

    # If necessary, add data preprocessing steps here to prepare data for
    # ingestion.

    # The first step of your workflow is a dataset generator.
    # This step takes a Google Cloud pipeline component, providing the necessary
    # input arguments, and uses the Python variable `ds_op` to define its
    # output. Note that here the `ds_op` only stores the definition of the
    # output but not the actual returned object from the execution. The value
    # of the object is not accessible at the dsl.pipeline level, and can only be
    # retrieved by providing it as the input to a downstream component.
    #
    # Also see TabularDatasetCreateOp, TextDatasetCreateOp,
    # TimeSeriesDatasetCreateOp, and VideoDatasetCreateOp:
    # https://google-cloud-pipeline-components.readthedocs.io/en/google-cloud-pipeline-components-0.2.1/google_cloud_pipeline_components.aiplatform.html
    ds_op = gcc_aip.ImageDatasetCreateOp(
        project=project_id,
        display_name=f"{PIPELINE_NAME}_dataset_create",
        gcs_source="gs://cloud-samples-data/vision/automl_classification/flowers/all_data_v2.csv",
        import_schema_uri=aiplatform.schema.dataset.ioformat.image.single_label_classification,
    )

    # The second step is a model training component. It takes the dataset
    # outputted from the first step, supplies it as an input argument to the
    # component (see `dataset=ds_op.outputs["dataset"]`), and will put its
    # outputs into `training_job_run_op`.
    training_job_run_op = gcc_aip.AutoMLImageTrainingJobRunOp(
        project=project_id,
        display_name=f"{PIPELINE_NAME}_training",
        prediction_type="classification",
        model_type="CLOUD",
        dataset=ds_op.outputs["dataset"],
        model_display_name="flowers-automl",
        training_fraction_split=0.6,
        validation_fraction_split=0.2,
        test_fraction_split=0.2,
        budget_milli_node_hours=8000,
    )

    # For custom training:
    # custom_training_job_run_op = gcc_aip.CustomContainerTrainingJobRunOp(
    #     project=project_id,
    #     display_name=f"{PIPELINE_NAME}_custom_training",
    #     container_uri=app_container_uri,
    #     # customize this command to invoke the appropriate custom training task
    #     command=[
    #         "python3",
    #         "-m",
    #         "{{app_name}}.tasks.<training_task>",
    #     ],
    #     dataset=ds_op.outputs["dataset"],
    #     model_display_name=f"{PIPELINE_NAME}_model_custom",
    #     training_fraction_split=0.6,
    #     validation_fraction_split=0.2,
    #     test_fraction_split=0.2,
    # )

    # The third and fourth step are for deploying the model.
    create_endpoint_op = gcc_aip.EndpointCreateOp(
        project=project_id,
        display_name=f"{PIPELINE_NAME}_create_endpoint",
    )

    model_deploy_op = gcc_aip.ModelDeployOp(
        model=training_job_run_op.outputs["model"],
        endpoint=create_endpoint_op.outputs['endpoint'],
        automatic_resources_min_replica_count=1,
        automatic_resources_max_replica_count=1,
    )


def compile(
    package_path: str,
):
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=package_path,
    )


def run_job(
    template_path: str,
    pipeline_root: str,
    pipeline_params: Dict[str, Any] = {},
):
    job = aiplatform.PipelineJob(
        display_name=PIPELINE_NAME,
        template_path=template_path,
        pipeline_root=pipeline_root,
        parameter_values=pipeline_params,
    )
    job.run()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"{PIPELINE_NAME} pipeline operations.")
    commands = parser.add_subparsers(
        help="commands", dest="command", required=True)

    # compile command arguments
    cmd_compile = commands.add_parser(
        "compile", help="compile pipeline function to a json package file.")
    cmd_compile.add_argument(
        "-o", "--output", required=True, help="package file output path.")

    # run command arguments
    cmd_run_job = commands.add_parser(
        "run", help="run pipeline job on AI platform.")
    cmd_run_job.add_argument("--package", required=True,
                             help="path to compiled pipeline package file.")
    cmd_run_job.add_argument(
        "--pipeline_root", required=True,
        help="GCS root directory for files generated by pipeline job.")
    # if needed, add arguments here for additional pipeline parameters.
    cmd_run_job.add_argument("--project", required=True, help="project ID.")
    # uncomment for custom training
    # cmd_run_job.add_argument("--app_container_uri", required=True,
    #                          help="App container URI for custom training.")

    return parser.parse_args()


def main(args):

    if args.command == "compile":
        compile(args.output)
    elif args.command == "run":
        aiplatform.init()
        # If pipeline parameters are necessary, add them here.
        pipeline_params = {
            "project_id": args.project,
            # uncomment for custom training
            # "app_container_uri": args.app_container_uri,
        }
        run_job(args.package, args.pipeline_root,
                pipeline_params=pipeline_params)
    else:
        print(f"Command not implemented: {args.command}")


if __name__ == "__main__":
    main(parse_args())
