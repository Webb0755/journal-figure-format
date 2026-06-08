# Journal Figure Format

Codex skill for preparing scientific figures for journal submission. It helps identify journal or publisher figure requirements, apply Matplotlib journal presets, inspect raster figure resolution, and export submission-ready figures as EPS, PDF, or TIFF.

## Features

- Journal/publisher preset guidance for Nature, Science, Cell Press, PLOS, IEEE, Elsevier, Springer Nature, ACS, and Wiley.
- Matplotlib styles for APS, Nature, and HHL figure sizes.
- Export support for EPS, PDF, and TIFF.
- Raster inspection for dimensions, DPI, color mode, and target width.
- Compliance reports with pass/warning status.

## Install

Copy the `journal-figure-format` folder into your Codex skills directory:

```bash
cp -R journal-figure-format ~/.codex/skills/
```

Then invoke it in Codex:

```text
Use $journal-figure-format to prepare this figure for Nature submission.
```

## Matplotlib Usage

```python
import sys
import matplotlib.pyplot as plt

sys.path.append("/path/to/journal-figure-format/scripts")
from matplotlib_style import load_style, save_figure

load_style(style="Nature", width="1-column", output_format="eps")

fig, ax = plt.subplots()
ax.plot([0, 1, 2], [0, 1, 0], marker="o")
ax.set_xlabel("Time (a.u.)")
ax.set_ylabel("Response")

save_figure(fig, "figure.eps")
save_figure(fig, "figure.pdf")
save_figure(fig, "figure.tif", output_format="tiff")
```

## Raster Export Usage

```bash
python scripts/figure_prepare.py inspect input.png --journal nature --figure-type combo
python scripts/figure_prepare.py export input.png --journal nature --figure-type combo --width-mm 89 --format tiff --output-dir figures_ready
python scripts/figure_prepare.py export input.png --journal nature --figure-type combo --width-mm 89 --format pdf --output-dir figures_ready
python scripts/figure_prepare.py export input.png --journal nature --figure-type combo --width-mm 89 --format eps --output-dir figures_ready
```

For true vector EPS/PDF output, prefer exporting directly from Matplotlib or another vector source. Raster-to-EPS remains raster pixels inside an EPS container.

## Dependencies

- Python 3.10+
- Pillow for raster inspection/export
- ReportLab for raster-to-PDF export
- Matplotlib for `matplotlib_style.py`

## License

MIT License. See `LICENSE`.
