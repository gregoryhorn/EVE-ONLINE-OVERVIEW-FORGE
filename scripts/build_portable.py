"""Build a folder-run portable release zip."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PORTABLE = DIST / "overview-forge-portable"


def main() -> int:
    if PORTABLE.exists():
        shutil.rmtree(PORTABLE)
    PORTABLE.mkdir(parents=True)

    shutil.copytree(ROOT / "src", PORTABLE / "src", ignore=shutil.ignore_patterns("__pycache__"))
    examples = PORTABLE / "Examples"
    examples.mkdir()
    shutil.copy2(ROOT / "Examples" / "standard_complete_overview.yaml", examples / "standard_complete_overview.yaml")

    for name in ["README.md", "PUBLISHING.md", "pyproject.toml", "requirements.txt"]:
        shutil.copy2(ROOT / name, PORTABLE / name)

    (PORTABLE / "run-gui.bat").write_text(_run_gui_bat(), encoding="utf-8")
    (PORTABLE / "run-cli.bat").write_text(_run_cli_bat(), encoding="utf-8")
    (PORTABLE / "README-PORTABLE.md").write_text(_portable_readme(), encoding="utf-8")

    archive = shutil.make_archive(str(DIST / "overview-forge-portable"), "zip", PORTABLE)
    print(archive)
    return 0


def _run_gui_bat() -> str:
    return """@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\\Scripts\\python.exe (
  py -3 -m venv .venv
  .venv\\Scripts\\python.exe -m pip install --upgrade pip
  .venv\\Scripts\\python.exe -m pip install -r requirements.txt
)
set PYTHONPATH=%CD%\\src
.venv\\Scripts\\python.exe -m eve_overview_manager.cli gui
"""


def _run_cli_bat() -> str:
    return """@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\\Scripts\\python.exe (
  py -3 -m venv .venv
  .venv\\Scripts\\python.exe -m pip install --upgrade pip
  .venv\\Scripts\\python.exe -m pip install -r requirements.txt
)
set PYTHONPATH=%CD%\\src
.venv\\Scripts\\python.exe -m eve_overview_manager.cli %*
"""


def _portable_readme() -> str:
    return """# Overview Forge Portable Build

This folder is meant to run in place. It does not install Overview Forge globally.

## Run The GUI

Double-click `run-gui.bat`.

The first run creates a local `.venv` folder and installs Python dependencies into that folder only.

## Run CLI Commands

Use `run-cli.bat`, for example:

```bat
run-cli.bat validate-yaml Examples\\standard_complete_overview.yaml --format json
```

Only the maintained standard overview template is included in this portable package.
Third-party/community overview samples are intentionally excluded.
"""


if __name__ == "__main__":
    raise SystemExit(main())
