"""Resolve BlockFlow preset IDs into download_handler batches.

Lifts the inline python from `serverless-docker/install-entrypoint.sh` so the
installer_server and the legacy one-shot entrypoint share one parser. Fetches
the registry manifest, looks up the preset, fetches its preset.json, and
returns the parsed dict. `preset_to_download_batch` translates `preset.models`
into the download_handler input shape (using `destination_path` since the
preset stores file-relative paths under MODELS_BASE).
"""

from __future__ import annotations

import json
import urllib.request

DEFAULT_MANIFEST_URL = (
    "https://raw.githubusercontent.com/Hearmeman24/blockflow-presets/main/manifest.json"
)
FETCH_TIMEOUT_SEC = 30


def _fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=FETCH_TIMEOUT_SEC) as r:
        return json.loads(r.read())


def resolve_preset(preset_id: str, manifest_url: str = DEFAULT_MANIFEST_URL) -> dict:
    """Fetch the manifest, find the preset by id, fetch + return its preset.json.

    Raises KeyError if `preset_id` is not present in the manifest.
    """
    manifest = _fetch_json(manifest_url)
    presets = manifest.get("presets", [])
    match = next((p for p in presets if p.get("id") == preset_id), None)
    if match is None:
        raise KeyError(f"preset_id {preset_id!r} missing from manifest at {manifest_url}")
    return _fetch_json(match["preset_url"])


def preset_to_download_batch(preset: dict) -> list[dict]:
    """Translate `preset.models` into the download_handler `downloads` shape."""
    return [
        {
            "source": "url",
            "url": m["url"],
            "destination_path": m["dest"],
            "sha256": m["sha256"],
        }
        for m in preset.get("models", [])
    ]
