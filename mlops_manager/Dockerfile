ARG accelerator="cpu"

FROM gcr.io/deeplearning-platform-release/tf2-${accelerator}.2-5

ARG app_name={{app_name}}
arg package_path

COPY ${package_path} .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ${package_path}

RUN mkdir -p /app
WORKDIR /app

ENTRYPOINT [ "python", "-m", "${app_name}" ]