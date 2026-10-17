#!/usr/bin/env bash
set -euo pipefail
kit_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SPARK_PYTHON:-python3}" "$kit_dir/build.py" "$@"
