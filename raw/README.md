# raw/ - inputs, never deployed

`bov-site.json` and `map-manifest.json` in this repo are GENERATED. Do not
hand-edit either one.

| File | What it is |
|---|---|
| `build_gould_sites.py` | The generator that writes `bov-site.json` and the map manifest for all five Gould Palmdale BOVs. Canonical copy lives in `C:\Users\gscher\gould-bov-workspace`. |
| `media-manifest.json` | Provenance for every published photo: source site, source URL, access date, SHA-256 of both the original download and the deployed JPEG, assigned role, rights basis, and how the property mapping was verified. |
| `media-REJECTED.md` | Images found but deliberately not published, with the reason. |

To change anything on this site:

```
cd C:\Users\gscher\gould-bov-workspace
.\rebuild_all.ps1          # data -> certified maps (only if pins moved) -> render -> gate
```

The gate must exit 0 before a commit and again before deploy.
