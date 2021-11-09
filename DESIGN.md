# MLOps Template Design

## Use Cases

### Hello Flowers Training Example

1. Create empty app: `./bin/manage.sh start app --app-name simple_app`
2. Create trainer: `./bin/manage start task --example flowers-tf --app-name simple_app --task-name train_flowers`
3. Run training locally: `cd simple_app && python -m simple_app.tasks.train_flowers`
4. Run training on cloud

