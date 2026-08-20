#!/usr/bin/env bash
# Isola o pytest de plugins globais do sistema (ex.: ROS launch_testing).
set -euo pipefail
cd "$(dirname "$0")"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export GX_ANALYTICS_ENABLED=false
export DO_NOT_TRACK=1
exec python -m pytest "$@"
