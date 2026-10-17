#!/usr/bin/env bash
# Copy the fixture repo (profile, draft, local source) into the empty workspace.
set -euo pipefail
cp -R "$(cd "$(dirname "$0")" && pwd)/resources/." .
