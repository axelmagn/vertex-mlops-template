# For applications which use tensorflow to train large custom models, consider
# deriving from a GCP Deep Learning Container. (this is disabled by default to 
# optimize docker build time)
# https://cloud.google.com/deep-learning-containers
# https://cloud.google.com/deep-learning-containers/docs/choosing-container
#
# FROM 	gcr.io/deeplearning-platform-release/tf-gpu

FROM python:3-slim

RUN pip install --upgrade pip

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install .

CMD ["python"]
