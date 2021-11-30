# MLOps Template Design

## Use Cases

### Create and Run Pipeline

1. Create empty app: `./bin/manage.sh start app --app-name simple_app`
2. Create empty pipeline: `./bin/manage.sh start pipeline --app-name simple_app --pipeline_name simple_pipeline`
3. Author pipeline: [Example](https://cloud.google.com/vertex-ai/docs/pipelines/build-pipeline)
4. CD into app directory: `cd simple_app`
5. Compile pipeline locally: `python -m simple_app.pipelines.simple_pipeline compile --output simple_pipeline.json`
6. Run pipeline remotely: `python -m simple_app.pipelines.simple_pipeline run --project PROJECT_ID --package simple_pipeline.json --pipeline_root GCS_PIPELINE_ROOT`


## Examples

### Hello Flowers Training Example

1. Create empty app: `./bin/manage.sh start app --app-name simple_app`
2. Create trainer: `./bin/manage start task --example flowers-tf --app-name simple_app --task-name train_flowers`
3. Run training locally: `cd simple_app && python -m simple_app.tasks.train_flowers`
4. Run training on cloud

