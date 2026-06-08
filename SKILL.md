---
name: journal-figure-format
description: Prepare, inspect, style, and export scientific manuscript figures to match journal or publisher submission requirements. Use when Codex needs to identify a target journal's figure standards, apply Matplotlib presets for APS/Nature/HHL figures, check image resolution/size/color/format, convert raster figure files such as PNG/JPEG/TIFF, produce EPS, PDF, or TIFF submission-ready figures, or generate a compliance report for journals such as Nature, Science, Cell, PLOS, IEEE, Elsevier, Springer Nature, ACS, Wiley, or a user-specified journal.
---

# Journal Figure Format

## Overview

Use this skill to turn scientific figures into journal-compliant submission assets. Always separate two jobs: first identify the applicable requirements, then transform or recreate the figure and report what changed.

## Workflow

1. Identify the target journal or publisher from the user's prompt, manuscript title page, file names, cover letter, or submission notes.
2. If the journal is not explicit, ask one concise question unless a publisher-wide default is clearly acceptable.
3. Verify requirements from the official journal author guidelines whenever current accuracy matters. Journal standards change; prefer official instructions over bundled presets.
4. If browsing or official guidelines are unavailable, use `references/journal-presets.md` as a starter reference and clearly mark the result as based on a preset.
5. Classify each figure as one of:
   - `photo`: microscopy, gel, blot, photograph, heatmap, raster render.
   - `line`: plots, diagrams, charts, schematics, text-heavy vector art.
   - `combo`: mixed line art and images, annotated microscopy, multi-panel composites.
6. Inspect source files before editing. Preserve vector formats for line art when possible; rasterize only when the journal requires a raster deliverable.
7. Export submission files and a compliance report. Include assumptions, target standard, final dimensions, DPI, color mode, file format, and any warnings.

## Tools

Use `scripts/figure_prepare.py` for raster image inspection and deterministic export:

```bash
python3 /Users/macy/.codex/skills/journal-figure-format/scripts/figure_prepare.py inspect input.png --journal nature --figure-type combo
python3 /Users/macy/.codex/skills/journal-figure-format/scripts/figure_prepare.py export input.png --journal nature --figure-type combo --width-mm 89 --format eps --output-dir ./figures_ready
python3 /Users/macy/.codex/skills/journal-figure-format/scripts/figure_prepare.py export input.png --journal nature --figure-type combo --width-mm 89 --format tiff --output-dir ./figures_ready
python3 /Users/macy/.codex/skills/journal-figure-format/scripts/figure_prepare.py export input.png --journal nature --figure-type combo --width-mm 89 --format pdf --output-dir ./figures_ready
```

The script handles PNG, JPEG, and TIFF through Pillow and exports EPS, PDF, or TIFF. Raster-to-EPS is not true vector output; for plots or line art, prefer Matplotlib/vector source and export EPS directly.

If system `python3` lacks Pillow, use the Codex bundled Python runtime when available or install Pillow before running image operations.

Use `scripts/matplotlib_style.py` when creating figures from Python/Matplotlib source. It provides APS, Nature, and HHL sizing presets and sets `savefig.format` to `eps`, `pdf`, or `tiff`:

```python
from pathlib import Path
import sys

sys.path.append("/Users/macy/.codex/skills/journal-figure-format/scripts")
from matplotlib_style import load_style, save_figure

load_style(style="Nature", width="1-column", output_format="eps")
# create plot...
save_figure(plt.gcf(), "figure.eps")
```

## Figure Decisions

- Prefer the journal's exact width classes. If none are provided, use conservative defaults: single column around 85-90 mm, double column around 170-180 mm.
- Use `photo` at 300 dpi, `combo` at 600 dpi, and `line` at 1200 dpi unless the journal says otherwise.
- Keep text and labels legible after final sizing. Avoid shrinking labels during raster export.
- Use RGB unless the journal explicitly requests CMYK; many online submission systems prefer RGB and convert later.
- Avoid JPEG for final submission unless requested. Prefer TIFF for raster submission and EPS/PDF for vector or Matplotlib-generated line art when accepted.
- Do not upscale low-resolution originals silently. If required output pixels exceed source pixels by more than 10%, warn that image detail cannot be recovered.

## Output Contract

For every completed task, provide:

- Final file path(s).
- The journal or preset used.
- Key export settings: dimensions, DPI, format, color mode.
- Compliance status: pass, pass-with-warnings, or needs-source-improvement.
- Short note listing any assumptions or unresolved guideline gaps.

## References

- Read `references/journal-presets.md` when no official source is available or when a quick preset is enough.
- Update the reference file when a verified official guideline differs from a bundled preset.
