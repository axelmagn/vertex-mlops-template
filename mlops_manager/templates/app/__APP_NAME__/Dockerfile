# TODO(axelmagn): replace with more flexible solution
ARG CPU_GPU="cpu"

# TODO(axelmagn): use templating to determine CPU/GPU
FROM gcr.io/deeplearning-platform-release/tf2-${CPU_GPU}.2-5:m73

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY . /app/
WORKDIR /app

ARG PYTHON_PACKAGE_NAME={{app_name}}
RUN python setup.py install
ENTRYPOINT [ "python", "-m", "${PYTHON_PACKAGE_NAME}" ]