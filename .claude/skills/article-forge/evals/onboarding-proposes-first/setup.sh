#!/usr/bin/env bash
# Copy the shared fictional repo, then this case's own files on top.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cp -R "$here/../_fixtures/base/." .
if [ -d "$here/resources" ]; then cp -R "$here/resources/." .; fi
rm -rf profile
