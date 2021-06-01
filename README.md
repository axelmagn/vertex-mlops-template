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


## Q&A

### How is code in this project organized?

This repository can be used as the beginning of an ML *Project* which
holds your team's ML source code.  *Projects* are made up of one or more
*Apps*, which are self-contained code bases that solve a particular ML problem.
In order to solve that problem, *Apps* need to perform a variety of *Tasks*.
*Tasks* can be hierarchical: for example one task may be to launch a pipeline 
job, while another may be to perform the contents of a pipeline component, and
that pipeline component may itself be launching a training task on Vertex 
Training. For this reason, task should be stateless, and rely on Vertex AI for 
managing the state of the App.  When tasks need to be automated or executed as
part of a workflow, Cloud Build is leveraged as a deployment tool.

### Why use YAML configs rather than environment variables?

ML applications often involve multiple tasks running on multiple services.
Environment variables, while commonly used to configure services in the [twelve
factor app](https://12factor.net/) methodology, become brittle when required to
be propagated to subtasks.  By consolidating configuration into yaml files, we
can obviate the need to propagate environment variables.

