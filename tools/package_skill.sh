#!/usr/bin/env bash
# Build a Claude.ai-uploadable ZIP of the article-forge skill.
# The ZIP must contain the skill FOLDER at its root, not just the contents.
set -euo pipefail
cd "$(dirname "$0")/../.claude/skills"
VERSION=$(cat article-forge/VERSION)
OUT="../../article-forge-skill-v${VERSION}.zip"
rm -f "$OUT"
zip -r "$OUT" article-forge -x '*.DS_Store' '*__pycache__*' 'article-forge/evals/*'
echo "Built $(cd ../.. && pwd)/article-forge-skill-v${VERSION}.zip"
