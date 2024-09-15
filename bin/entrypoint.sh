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
if [ ! -z "${CMI_ENCODING+x}" ]; then
    SCHEMA_PARAMETERS+=("--encoding=$(eval ${CMI_ENCODING})")
fi
if [ ! -z "${CMI_HOST+x}" ]; then
    SCHEMA_PARAMETERS+=("--host=$(eval ${CMI_HOST})")
fi
if [ ! -z "${CMI_PORT+x}" ]; then
    SCHEMA_PARAMETERS+=("--port=$(eval ${CMI_PORT})")
fi
if [ ! -z "${CMI_USER+x}" ]; then
    SCHEMA_PARAMETERS+=("--user=$(eval ${CMI_USER})")
fi
if [ ! -z "${CMI_PASSWORD+x}" ]; then
    SCHEMA_PARAMETERS+=("--password=$(eval ${CMI_PASSWORD})")
fi
if [ ! -z "${CMI_SCHEMA+x}" ]; then
    SCHEMA_PARAMETERS+=("--file=$(eval ${CMI_SCHEMA})")
fi

function export_cmi() {
    # reevaluate parameters before every call
    parameters=()
    if [ ! -z "${CMI_ENCODING+x}" ]; then
        parameters+=("--encoding=$(eval ${CMI_ENCODING})")
    fi
    if [ ! -z "${CMI_HOST+x}" ]; then
        parameters+=("--host=$(eval ${CMI_HOST})")
    fi
    if [ ! -z "${CMI_PORT+x}" ]; then
        parameters+=("--port=$(eval ${CMI_PORT})")
    fi
    if [ ! -z "${CMI_USER+x}" ]; then
        parameters+=("--user=$(eval ${CMI_USER})")
    fi
    if [ ! -z "${CMI_PASSWORD+x}" ]; then
        parameters+=("--password=$(eval ${CMI_PASSWORD})")
    fi
    if [ ! -z "${CMI_AFTER+x}" ]; then
        parameters+=("--after=$(eval ${CMI_AFTER})")
    fi
    if [ ! -z "${CMI_BEFORE+x}" ]; then
        parameters+=("--before=$(eval ${CMI_BEFORE})")
    fi
    if [ ! -z "${CMI_UNIQUE+x}" ]; then
        parameters+=("--unique")
    fi
    if [ ! -z "${CMI_DELTA+x}" ]; then
        parameters+=("--min-delta=$(eval ${CMI_DELTA})")
    fi
    if [ ! -z "${CMI_NEW+x}" ]; then
        parameters+=("--only-new")
    fi
    if [ ! -z "${CMI_DATABASE+x}" ]; then
        parameters+=("--database=$(eval ${CMI_DATABASE})")
    fi
    ./bin/export_postgresql ${parameters[@]}
}

./bin/generate_sql_schema ${SCHEMA_PARAMETERS[@]}
export_cmi()

if [ ! -z "${CMI_REPEAT+x}" ]; then
    echo "sleeping for ${CMI_REPEAT} seconds"
    sleep ${CMI_REPEAT}
    export_cmi()
fi
