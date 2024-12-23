#!/bin/bash -x

set -e
set -o pipefail
set -u

THIS_PATH="$(readlink --canonicalize-existing "${0}")"
THIS_NAME="$(basename "${THIS_PATH}")"
THIS_DIR="$(dirname "${THIS_PATH}")"

# redefine command_not_found_handle so we can eval every variable
function command_not_found_handle() {
    echo $@
}

SCHEMA_PARAMETERS=()
if [ -n "${CMI_ENCODING}" ]; then
    SCHEMA_PARAMETERS+=("--encoding=$(eval ${CMI_ENCODING})")
fi
if [ -n "${CMI_HOST}" ]; then
    SCHEMA_PARAMETERS+=("--host=$(eval ${CMI_HOST})")
fi
if [ -n "${CMI_PORT}" ]; then
    SCHEMA_PARAMETERS+=("--port=$(eval ${CMI_PORT})")
fi
if [ -n "${CMI_USER}" ]; then
    SCHEMA_PARAMETERS+=("--user=$(eval ${CMI_USER})")
fi
if [ -n "${CMI_PASSWORD}" ]; then
    SCHEMA_PARAMETERS+=("--password=$(eval ${CMI_PASSWORD})")
fi
if [ -n "${CMI_SCHEMA}" ]; then
    SCHEMA_PARAMETERS+=("--file=$(eval ${CMI_SCHEMA})")
fi

function export_cmi() {
    # reevaluate parameters before every call
    parameters=()
    if [ -n "${CMI_ENCODING}" ]; then
        parameters+=("--encoding=$(eval ${CMI_ENCODING})")
    fi
    if [ -n "${CMI_HOST}" ]; then
        parameters+=("--host=$(eval ${CMI_HOST})")
    fi
    if [ -n "${CMI_PORT}" ]; then
        parameters+=("--port=$(eval ${CMI_PORT})")
    fi
    if [ -n "${CMI_USER}" ]; then
        parameters+=("--user=$(eval ${CMI_USER})")
    fi
    if [ -n "${CMI_PASSWORD}" ]; then
        parameters+=("--password=$(eval ${CMI_PASSWORD})")
    fi
    if [ -n "${CMI_AFTER}" ]; then
        parameters+=("--after=$(eval ${CMI_AFTER})")
    fi
    if [ -n "${CMI_BEFORE}" ]; then
        parameters+=("--before=$(eval ${CMI_BEFORE})")
    fi
    if [ -n "${CMI_UNIQUE}" ]; then
        parameters+=("--unique")
    fi
    if [ -n "${CMI_DELTA}" ]; then
        parameters+=("--min-delta=$(eval ${CMI_DELTA})")
    fi
    if [ -n "${CMI_NEW}" ]; then
        parameters+=("--only-new")
    fi
    if [ -n "${CMI_DATABASE}" ]; then
        parameters+=("--database=$(eval ${CMI_DATABASE})")
    fi
    ./bin/export_postgresql ${parameters[@]}
}

./bin/generate_sql_schema ${SCHEMA_PARAMETERS[@]}
export_cmi()

if [ -n "${CMI_REPEAT}" ]; then
    echo "sleeping for ${CMI_REPEAT} seconds"
    sleep ${CMI_REPEAT}
    export_cmi()
fi
