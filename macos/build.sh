#!/bin/bash
# No Xcode project required. All invocations use rtk, including internal commands.
set -euo pipefail
cd "$(dirname "$0")"
# Python preserves existing bundle metadata and entitlements before rebuilding.
rtk proxy python3 build.py "$@"
