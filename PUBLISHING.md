# GitHub Publishing Checklist

Use this checklist before pushing the repository public.

## Required

- Confirm no real EVE profile files are present: `core_user_*.dat`, `core_char_*.dat`, `prefs.ini`.
- Confirm generated local folders are not staged: `.tmp/`, `.playwright-mcp/`, `.pytest_cache/`, `*.egg-info/`.
- Confirm downloaded/community overview samples are not staged. Only `Examples/standard_complete_overview.yaml` should be published from `Examples/`.
- Run `python -m pytest`.
- Run `python scripts\gui_smoke_qa.py --port 7478`.
- Run `python scripts\build_portable.py` and upload `dist\overview-forge-portable.zip` to GitHub Releases.
- Run `python -m build` after installing `build`, or at minimum `python -m compileall src`.
- Decide on a license before accepting external contributions. No open-source license has been selected yet.

## Suggested First GitHub Steps

```powershell
git status --short
git add .gitignore MANIFEST.in PUBLISHING.md pyproject.toml requirements.txt README.md AGENTS.md Examples/standard_complete_overview.yaml docs scripts src tests
git status --short
git commit -m "Prepare repository for GitHub publishing"
git branch -M main
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

## Notes

- The app is local/offline-first. Do not add required ESI/network dependencies for core overview editing.
- Opaque EVE profile files must remain treated as local private data.
- GUI static files under `src/eve_overview_manager/gui/static/` are included in package builds.
- The portable release is folder-run. Users extract the zip and run `run-gui.bat`; it creates a local `.venv` inside the extracted folder.
- The GitHub README includes the ISK customization note: contact `Mizz Betty` in game.
