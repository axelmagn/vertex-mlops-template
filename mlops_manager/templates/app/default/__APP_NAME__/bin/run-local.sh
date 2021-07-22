#!/bin/bash
#
# Utility script to invoke the app CLI with its local configuration.
set -exuo pipefail

readonly PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"

PYTHON_CMD="python"
if ! command -v "${PYTHON_CMD}" > /dev/null
then
    PYTHON_CMD="python3"
    if ! command -v "${PYTHON_CMD}" > /dev/null
    then
        echo "ERROR: Could not find a python interpreter."
        exit
    fi
fi

pushd "${PROJECT_DIR}" > /dev/null
"${PYTHON_CMD}" -m {{app_name}} \
    -c "config/base.yaml" \
    -c "config/local.yaml" \
    "${@}"
popd > /dev/null