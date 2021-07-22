# Vertex MLOps Template

This project helps ML Engineers and Data Scientists accelerate the creation of
AI Applications on the [Vertex AI](https://cloud.google.com/vertex-ai) platform.
It is made available as a self-contained source repository, which users are
encouraged to fork and customize to fit their own workflows.

## Getting Started

When using the Vertex MLOps Template, code is organized into "apps".  Each app
is packaged into its own container, which provides a self-contained environment
for execution on Vertex services. To get started, this section will walk you
through the creation and deployment of a simple app that performs
classifications on the
[fashion-mnist](https://www.tensorflow.org/datasets/catalog/fashion_mnist)
dataset.

### Prerequisites

In order to complete this tutorial, you will need access to a Google Cloud
Platform account and project, as well as a few basic resources within the
project.

Before starting, take a moment to set up and note the name of the following
resources:

- gcp-project: the GCP project to deploy the app within. 
  ([docs](https://cloud.google.com/resource-manager/docs/creating-managing-projects))
- gcp-region: the region to use for regionalized resources (when in doubt, use 
  us-central1). ([docs](https://cloud.google.com/compute/docs/regions-zones))
- gcp-storage-root: the Google Cloud Storage path to contain application
  objects. The bucket region *must* be set to the same region as `gcp-region` 
  for some Vertex functionality to work. 
  ([docs](https://cloud.google.com/storage/docs/creating-buckets))

It is recommended that you obtain the Editor or Owner IAM roles within
your project.  While more granular IAM roles may be utilized, granular IAM
permissions are beyond the scope of this quickstart.

It will also be necessary to enable the following Cloud Services: 
([docs](https://cloud.google.com/service-usage/docs/enable-disable))

```
gcloud services enable \
    aiplatform.googleapis.com
    appengine.googleapis.com
    cloudbuild.googleapis.com
    cloudfunctions.googleapis.com
    cloudscheduler.googleapis.com
```

### Install Manager Dependencies

```
pip install --user -r requirements.txt
```

or

```
python -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Create an App

```
./bin/manage.sh start app \
    --name first_app \
    --gcp-project {PROJECT_ID} \
    --gcp-region {REGION} \
    --gcp-storage-root gs://{BUCKET}/{PATH}
    
tree first_app
```

### Create a Pipeline

```
./bin/manage.sh start pipeline \
    --name first_pipeline \
    --app first_app
    
tree first_app
```

Take a moment to look through the code that was generated in
`first_app.pipelines.first_pipeline.pipeline`.  It contains
the boilerplate for a simple pipeline, heavily commented.

Also notice that a new configuration file was created:
`config/pipeline_first_pipeline.yaml`

### Create a Trainer

```
./bin/manage.sh start trainer \
    --name first_trainer \
    --app first_app
```

Similarly, take a moment to take a look through the trainer generated in
`first_app.trainers.first_trainer.task`.

In your pipeline definition, configure the training component to use
`first_app.trainers.first_trainer.task`. (Search for "PLACEHOLDER")
### Update Configurations

```
cd first_app
cat config/pipeline_first_pipeline.yaml >> config/base.yaml
```

### Submit Pipeline

```
bash bin/run.sh build_pipeline first_pipeline
bash bin/run.sh run_pipeline first_pipeline
```

### Automate with Cloud Build

```
gcloud builds submit --config cicd/build_app.yaml
gcloud builds submit --config cicd/release_app.yaml
gcloud builds submit --config cicd/deploy_app.yaml
```

## Resources

- [Best practices for implementing machine learning on Google Cloud](https://cloud.google.com/architecture/ml-on-gcp-best-practices)
- [Practitioners Guide to MLOps: A framework for continuous delivery and automation of machine learning](https://cloud.google.com/resources/mlops-whitepaper)

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

### Why use YAML configs rather than {gflags,protobuf,jsonnet,TOML,...}?

There are many tools and languages that can be used to configure an application.
YAML was chosen due to its already widespread use for configuration on google
cloud platform.  When authoring the configuration module, we prioritized
simplicity over scalability.  If these choices are unsuitable for your use case,
we strongly encourage you to modify your app's configuration code to meet your
needs.

### Why not publish this as a PyPi package?

This project is intended to be customized to fit your needs.  We therefore
recommend forking this repository, so that you can start to develop the
customizations and templates that fit your workflow.
