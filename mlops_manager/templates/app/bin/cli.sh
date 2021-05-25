#!/bin/bash
#
# invoke the app CLI

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
"${PYTHON_CMD}" -m {{PACKAGE_NAME}} "${@}"
popd > /dev/null