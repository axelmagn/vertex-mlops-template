
## Create an App

```
./bin/manage.sh start app \
    --name first_app \
    --gcp-project axelmagn-dev2 \
    --gcp-region us-central1 \
    --gcp-storage-root gs://axelmagn-dev2-us-central1/apparel
    
tree first_app
```

## Create a Pipeline

```
./bin/manage.sh start pipeline \
    --name first_pipeline \
    --app first_app
    
tree first_app
```

## Create a Trainer

```
./bin/manage.sh start trainer \
    --name first_trainer \
    --app first_app
```

## Example App

```
./bin/manage.sh start app \
    --name apparel \
    --gcp-project axelmagn-dev2 \
    --gcp-region us-central1 \
    --gcp-storage-root gs://axelmagn-dev2-us-central1/apparel \
    --example fashion-mnist
    
tree apparel

cd apparel
```

## Config

```
cat config/fashion_mnist.yaml >> config/base.yaml
```

## Submit Pipeline

```
bash bin/run-local.sh build_pipeline fashion_mnist
bash bin/run-local.sh run_pipeline fashion_mnist --job-spec build/apparel-fashion-mnist-local.json
```

## Automate with Cloud Build

```
gcloud builds submit --config cicd/build_app.yaml
gcloud builds submit --config cicd/release_app.yaml
gcloud builds submit --config cicd/deploy_app.yaml
```
