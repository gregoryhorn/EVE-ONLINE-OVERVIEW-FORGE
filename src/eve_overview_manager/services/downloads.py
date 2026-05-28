"""Download helpers for official CCP static data archives."""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

SDE_JSONL_LATEST_URL = "https://developers.eveonline.com/static-data/eve-online-static-data-latest-jsonl.zip"
SDE_YAML_LATEST_URL = "https://developers.eveonline.com/static-data/eve-online-static-data-latest-yaml.zip"


def download_file(url: str, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, output)
    return output
