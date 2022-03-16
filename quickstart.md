# Vertex MLOps Template Quickstart

In this guide, you will set up and deploy a minimal machine learning project on 
Vertex AI. You will learn the template's code structure, set up a training and 
deployment pipeline, define a custom training task, and deploy your model to 
production.

The app we create will only have default functionality, but will demostrate the 
fundamentals of this system.


## Prerequisites

Before beginning the quickstart, please make sure the following steps are 
complete:

1. Select or create a google cloud project, and note its ID for later.  We will
    refer to it in this guide as `PROJECT_ID`.  
    ([project selector](https://console.cloud.google.com/projectselector2/home/dashboard))
    
    ```
    export PROJECT_ID=... # your project ID here
    ```
    
2. Select a location for your project resources and make a note of it -- for
    example, `us-central1`. (Some Vertex services require co-location between
    tasks, so it is advised that all Vertex worloads run in the same region). We
    will refer to it in this guide as `REGION`.
    
    ```
    export REGION=us-central1 # you can replace this with your preferred region 
    ```
    
2. Make sure that billing is enabled for your cloud project.
    ([documentation](https://cloud.google.com/billing/docs/how-to/modify-project#confirm_billing_is_enabled_on_a_project))
    
3. Enable the Vertex AI and Cloud Storage APIs. 
    ([enable the APIs](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com,storage-component.googleapis.com))
    
4. Install and initialize the Google Cloud CLI. ([documentation](https://cloud.google.com/sdk/docs/install))

5. Update and install `gcloud` components:
    ```
    gcloud components update && \
    gcloud components install beta
    ```
6. Configure a cloud storage bucket for the project:
    ```
    export BUCKET_NAME=... # your bucket name here (no 'gs://' in front)
    ```

    ```
    # if necessary, create the bucket
    gsutil mb -p ${PROJECT_ID} -l REGION gs://${BUCKET_NAME}
    ```
7. Install python, virtualenv, and pip locally. (methods vary)

For the CICD section of this guide, the following steps must also be completed:

1. Select or create a Docker Artifact Registry.  We will refer to it as
    `ARTIFACT_REPO`. 
    ([documentation](https://cloud.google.com/artifact-registry/docs/docker/quickstart))
    
    ```
    export ARTIFACT_REPO=... # your artifact repo here (only required for CICD)
    ```

2. Enable the Cloud Build APIs. 
    ([enable the APIs](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com,%20artifactregistry.googleapis.com))

**Note:** this quickstart assumes that you are following along on your local
development machine.  However it is also possible to follow this guide on a
user-managed Vertex Workbench instance. 
([documentation](https://cloud.google.com/vertex-ai/docs/workbench/user-managed/quickstart-create-console))

```
export PROJECT_ID= # your project ID here
export BUCKET_NAME= # your bucket name here
```
    
## Clone the Repository

Begin by cloning the Vertex MLOps Template repository.

```
git clone https://github.com/axelmagn/vertex-mlops-template.git
cd vertex-mlops-template
```

## Install python dependencies

We will be interacting extensively with the `mlops_manager` module, and the
`bin/manage.sh` wrapper script. To ensure that they work correctly, 

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Create an App

First, create an app.  The default code we will use performs classification on
the public [Iris Flower Dataset](https://archive.ics.uci.edu/ml/datasets/iris),
so let's call this app `iris_quickstart`. 

```
export APP_NAME=iris_quickstart
```

```
./bin/manage.sh start app --app-name ${APP_NAME}
```

**Note: Mind your hyphens and underscores.**  At the moment, there is little to
no string validation to prevent you from passing invalid arguments when
starting templates. Template names should always be valid python identifiers,
which allow underscores but not hyphens.  However option names and other
template variables such as URLs use hyphens. If something's not working, it's
possible that it's a typo.

This will create a new app folder in your project, which should look like this:

```
tree ${APP_NAME}/
```

```
iris_quickstart/
├── Dockerfile
├── iris_quickstart
│   ├── components
│   │   └── __init__.py
│   ├── data.py
│   ├── __init__.py
│   ├── models
│   │   └── __init__.py
│   ├── pipelines
│   │   └── __init__.py
│   └── tasks
│       └── __init__.py
├── notebooks
├── pytest.ini
├── requirements.txt
└── setup.py

6 directories, 10 files
```


### Aside: What's an App?

The Vertex MLOps Template organizes a project into discrete *"apps"*, which are 
standalone python modules and docker environments. This helps teams with 
multiple data science tasks organize them in the same git repository, while
sharing common libraries and files. This is just one of many ways you could
organize an AI project.


## Create a Pipeline

We now have an app, but it doesn't do much yet.  Let's create a Vertex pipeline 
called `iris_train_deploy` that will train and deploy our model.  The pipeline
template trains and deploys an AutoML model on this dataset by default, so no
code modification will be necessary.


```
export PIPELINE_NAME=iris_train_deploy
```

```
./bin/manage.sh start pipeline \
    --app-name ${APP_NAME} \
    --pipeline-name ${PIPELINE_NAME}
```

This will create new pipeline and test files located within the
`iris_quickstart/iris_quickstart/pipelines` directory. If you inspect them with
a code editor, you will find that `iris_train_deploy.py` defines a `pipeline`
function, but can also function as a command line script to compile and run
the pipeline.  You can customize this functionality by modifying the `compile`, 
`run_job` and `parse_args` functions.

### Compile and Run the Pipeline

Compile the pipeline and submit it to Vertex AI from your development machine
with the following commands:

**Important**: The following command changes the working directory to that of 
the recently created app.  Subsequent quickstart sections will assume that your
working directory is now `iris_quickstart/`.

```
cd ${APP_NAME}
```

```
gcloud auth application-default login
pip install -r requirements.txt
```

```
python -m ${APP_NAME}.pipelines.${PIPELINE_NAME} compile \
    --output ${PIPELINE_NAME}.json
```

**Note:** The command below can take a long time to execute.

```
python -m ${APP_NAME}.pipelines.${PIPELINE_NAME} run \
    --package ${PIPELINE_NAME}.json \
    --pipeline_root gs://${BUCKET_NAME}/${APP_NAME}/${PIPELINE_NAME} \
    --project ${PROJECT_ID}
```

## (Optional) Iterate in a Notebook

We have already created a simple pipeline that trains and deploys a robust 
AutoML model. However in the real world, data science is a highly iterative 
process. While the data science aspects of this problem are beyond the scope
of this quickstart, you can use this opportunity to experiment with the dataset
and tools in a notebook using the following commands:

```
pip install jupyter
pip install -e ${APP_NAME}
jupyter notebooks
```

**Note:** there is a `notebooks/` subdirectory intended to contain any 
notebooks related to the app.

## Create a Custom Training Task

**TODO(axelmagn): complete this section**

```
../bin/manage.sh start task \
    --variant train-tf \
    <...>
```

## Create a CICD Configuration

Ideally, this pipeline should re-trigger periodically whenever the model code 
or dataset changes.  On Google Cloud, this is handled by the Cloud Build 
service. We can create a simple CICD configuration that will build a docker 
container for our app and submit the pipeline.

```
../bin/manage.sh start cicd \
    --app-name ${APP_NAME} \
    --gcp-region ${REGION} \
    --artifact-repo ${ARTIFACT_REPO} \
    --artifact-gcs-root gs://${BUCKET_NAME}/${APP_NAME}/build \
    --pipeline-name ${PIPELINE_NAME} \
    --pipeline-root gs://${BUCKET_NAME}/${APP_NAME}/${PIPELINE_NAME}
```

This will create a `cloudbuild.yaml` file in your app directory which builds,
tests, and deploys the `iris_train_deploy` pipeline.  You can submit this as
a cloud build job with the following command:

**Note:** The command below can take a long time to execute.

```
gcloud builds submit
```

Automated deployment is beyond the scope of this quickstart, however, please
consult the following resources for more information on how it may be accomplished:

* [Cloud Build - Building repositories from GitHub](https://cloud.google.com/build/docs/automating-builds/build-repos-from-github)
* [Cloud Build - Creating Pub/Sub Triggers](https://cloud.google.com/build/docs/automating-builds/create-pubsub-triggers)
* [Practitioners Guide to MLOps: A framework for continuous delivery and automation of machine learning](https://cloud.google.com/resources/mlops-whitepaper)
