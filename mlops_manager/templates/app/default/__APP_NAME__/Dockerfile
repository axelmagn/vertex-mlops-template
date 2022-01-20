# For applications which use tensorflow to train large custom models, consider
# deriving from a GCP Deep Learning Container. (this is disabled by default to 
# optimize docker build time)
# https://cloud.google.com/deep-learning-containers
# https://cloud.google.com/deep-learning-containers/docs/choosing-container
#
# FROM 	gcr.io/deeplearning-platform-release/tf-gpu

FROM python:3-slim

RUN pip install --upgrade pip

# create a non-root user to run app
RUN groupadd -r worker && useradd --no-log-init -r -g worker --create-home worker
USER worker

# add the local pip directory to path
RUN mkdir -p /home/worker/.local/bin
ENV PATH="/home/worker/.local/bin:${PATH}"

RUN mkdir -p /home/worker/app
WORKDIR /home/worker/app

COPY --chown=worker:worker requirements.txt requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt


COPY --chown=worker:worker . .
RUN pip install --user .

CMD ["python"]
