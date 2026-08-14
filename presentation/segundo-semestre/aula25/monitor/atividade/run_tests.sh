#!/usr/bin/env bash
# Isola o pytest de plugins globais do sistema (ex.: ROS launch_testing).
set -euo pipefail
cd "$(dirname "$0")"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export DEEPEVAL_TELEMETRY_OPT_OUT=1
unset OPENAI_API_KEY || true
exec python -m pytest "$@"
