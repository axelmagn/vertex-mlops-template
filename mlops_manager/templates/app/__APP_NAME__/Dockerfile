# TODO(axelmagn): replace with more flexible solution
ARG cpu_gpu="cpu"

# TODO(axelmagn): use templating to determine CPU/GPU
FROM gcr.io/deeplearning-platform-release/tf2-${cpu_gpu}.2-5

ARG python_package_name="{{app_name}}"
ARG python_package_version="0.0.1"
ARG python_sdist_path="dist/${python_package_name}-${python_package_version}.tar.gz"
ARG python_sdist_local="${python_package_name}-${python_package_version}.tar.gz"

COPY ${python_sdist_path} ${python_sdist_local}
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ${python_sdist_local}

ENTRYPOINT [ "python", "-m", "${python_package_name}" ]