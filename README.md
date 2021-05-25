# Vertex MLOps Template

## Quickstart

**Note:** This procedure requires enabling a number of GCP services, and setting
up some IAM and service account permissions.  These steps are not yet described
here.  Until they are, expect a little bit of problem solving on your first
runthrough.

Install dev requirements

```
pip install -r requirements.txt
```

Interact with MLOps Manager

```
./bin/manage.sh --help
```

Start an app

```
./bin/manage.sh start_app \
    --name <app_name> \
    --gcp_project <project_id> \
    --gcp_region <region> \
    --gcp_storage_root <gcs_path>
```

View the app source tree

```
tree <app_name>
```

Launch the example pipeline `hello_pipeline`.

```
.<app_name>/bin/run.sh run_pipeline hello_pipeline
```

Launch a build job.

*TODO(axelmagn): wrap in runner command*

```
pushd simple_app
gcloud builds submit \
    --config config/build/cloudbuild.yaml . \
    --substitutions='_ARTIFACT_REPO_NAME=<artifact_repo_name>,_DIST_VERSION=<version>,_APP_NAME=<app_name>,_BUCKET_NAME=<bucket_name>,_PIPELINE_NAME=hello_pipeline'
```


