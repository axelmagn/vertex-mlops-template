#!/bin/bash
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

case "${SKIP_LINT:-0}" in
    1|true)
        exit 0
        ;;
    *)
        python -m pylint "${PROJECT_DIR}/{{app_name}}" "${@}"
        ;;
esac