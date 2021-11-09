ARG BUILD_IMAGE
FROM ${BUILD_IMAGE}

WORKDIR /app
RUN mkdir -p config
ARG RELEASE_CONFIG_SRC=release.yaml
COPY "${RELEASE_CONFIG_SRC}" "config/release.yaml"

ARG PIPELINE_JOB_SPEC_SRC=release/pipelines/
RUN mkdir -p ${PIPELINE_JOB_SPEC_SRC}
COPY ${PIPELINE_JOB_SPEC_SRC} ${PIPELINE_JOB_SPEC_SRC}
# List dir for sanity. It costs nothing and helps during debugging.
RUN pwd
RUN tree .

ENTRYPOINT ["python", "-m", "{{app_name}}", "-c", "config/release.yaml"]