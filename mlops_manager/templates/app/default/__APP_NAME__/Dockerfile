# Container is based on TFE images by default:
# https://cloud.google.com/deep-learning-containers/docs/choosing-container
# ACCELERATOR may take values of either `cpu` or `gpu`.
ARG ACCELERATOR="cpu"
FROM gcr.io/deeplearning-platform-release/tf2-${ACCELERATOR}.2-5:m73

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY . /app/
WORKDIR /app

RUN pip install .

ENTRYPOINT [ "python", "-m", "{{app_name}}"]