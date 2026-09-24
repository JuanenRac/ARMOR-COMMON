#!/usr/bin/env bash
# ****************************************************************************
# A.R.M.O.R. - armor-project.sh
# Standard POSIX project workflow launcher.
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
# GPL-3.0-or-later - see LICENSE
# ****************************************************************************
set -euo pipefail
ACTION="${1:-build-test}"
PROJECT="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PROJECT_NAME="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1],encoding="utf-8"))["name"])' "$PROJECT/armor.project.json")"
echo "*******************************************************************************"
echo "* $PROJECT_NAME - $ACTION"
echo "* Mode      : $ACTION"
echo "* Author    : JuanenRac (Electro Hobby 3D)"
echo "* Email     : electrohobby3d@gmail.com"
echo "* Copyright : (C) 2026 JuanenRac"
echo "* License   : GPL-3.0-or-later - see LICENSE"
echo "* 1. Validate the real stack commands for this project."
echo "* 2. Version and CHANGELOG change only after a successful build."
echo "*******************************************************************************"
python3 "$(dirname "${BASH_SOURCE[0]}")/../tools/armor_project_tool.py" "$ACTION" "$PROJECT"
if [[ -t 0 ]]; then read -r -p "Press Enter to close..."; fi
